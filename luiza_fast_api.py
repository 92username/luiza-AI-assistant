"""
API FastAPI para a Luiza, assistente virtual da EstudaMais.tech.

Este módulo implementa um serviço de chatbot usando FastAPI com LangChain e
retrieval-augmented generation (RAG) para responder perguntas sobre a
EstudaMais.tech e GitHub Student Pack com base em documentação indexada.
"""

import os
import re
import sys

# pylint: disable=wrong-import-position,wrong-import-order //

# Third-party imports
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, SecretStr

# Set path for local imports (needs to be before langchain imports)
sys.path.append("./langchain_core")

# LangChain imports
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Local imports
from logger import info, warning, error

# Define SYSTEM_PROMPT
SYSTEM_TEMPLATE = """
Você é a Luiza, assistente virtual da EstudaMais.tech — motivadora, clara e sempre positiva.

Utilize **apenas** as informações do contexto abaixo para formular sua resposta.  
Se a resposta não estiver no contexto, diga exatamente:
"Não tenho essa informação no momento. Deseja perguntar algo relacionado à EstudaMais.tech ou ao GitHub Student Pack (GHSP)? 😊"

==========
{context}

Pergunta: {question}
"""

SYSTEM_PROMPT = PromptTemplate.from_template(SYSTEM_TEMPLATE)

load_dotenv()

# Carrega a chave como SecretStr
api_key_env = os.getenv("OPENAI_API_KEY")
if not api_key_env:
    raise EnvironmentError(
        "Variável OPENAI_API_KEY não encontrada. Verifique seu .env."
    )
api_key = SecretStr(api_key_env)

# Configure chat_model (globally)
chat_model = ChatOpenAI(
    api_key=api_key,  # Usar api_key que é do tipo SecretStr, não api_key_env
    model="gpt-4.1-nano",
    temperature=0.7,
    model_kwargs={"max_tokens": 1024},
)

# Cria um embedding_function com modelo compatível
embeddings = OpenAIEmbeddings(api_key=api_key, model="text-embedding-ada-002")

# Carrega o vectorstore persistido
vectordb = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")


# Função de extração de keywords
def extract_keywords(text: str) -> list[str]:
    """
    Extrai palavras-chave de um texto, retornando apenas caracteres alfanuméricos.

    Args:
        text: Texto a ser processado

    Returns:
        Lista de palavras-chave extraídas em minúsculas
    """
    return re.findall(r"\w+", text.lower())


# Lista de temas válidos
TEMAS = {"visao-geral", "plataforma", "mvp", "comecar", "fontes", "github"}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """
    Modelo para requisição de chat, contendo a mensagem do usuário.
    """

    message: str


# Criar uma instância de LLMChain com o modelo e o prompt
llm_chain = LLMChain(llm=chat_model, prompt=SYSTEM_PROMPT)


# Nova função para gerar resposta usando LLMChain diretamente
def gera_resposta_com_langchain(docs_and_scores: list, query: str) -> str:
    """
    Gera resposta usando o LLMChain com base nos documentos relevantes encontrados.

    Args:
        docs_and_scores: Lista de tuplas (documento, score) de relevância
        query: Pergunta original do usuário

    Returns:
        Texto da resposta gerada pelo modelo de linguagem
    """
    # 1) Junte o conteúdo dos chunks
    context = "\n\n".join([doc.page_content for doc, _ in docs_and_scores])

    # 2) Rode o chain passando os valores
    answer = llm_chain.run({"context": context, "question": query})

    return answer


def _buscar_documentos(query: str, keywords: list) -> list:
    """
    Função auxiliar para buscar documentos relevantes baseados na query.

    Args:
        query: A pergunta do usuário
        keywords: Palavras-chave extraídas da pergunta

    Returns:
        Lista de tuplas (documento, score) de relevância
    """
    # Detectar temas correspondentes
    matched_themes = set(keywords) & TEMAS
    k_docs = 5  # Número de documentos a recuperar

    # Buscar documentos com filtro de tema, se aplicável
    if matched_themes:
        info(f"Temas correspondentes encontrados: {list(matched_themes)}")
        filter_dict = {"tema": {"$in": list(matched_themes)}}
        retriever = vectordb.as_retriever(
            search_kwargs={"filter": filter_dict, "k": k_docs}
        )
        docs_and_scores = retriever.vectorstore.similarity_search_with_score(
            query, k=k_docs, filter=filter_dict
        )

        # Fallback para busca sem filtro se não houver resultados
        if not docs_and_scores:
            info(
                "Fallback: Nenhum documento encontrado com filtro de tema, tentando busca geral."
            )
            docs_and_scores = vectordb.similarity_search_with_score(query, k=k_docs)
    else:
        # Busca sem filtro se não houver temas correspondentes
        info("Nenhum tema correspondente encontrado, buscando sem filtro de tema.")
        docs_and_scores = vectordb.similarity_search_with_score(query, k=k_docs)

    return docs_and_scores


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint de chat que recebe a mensagem do usuário e retorna uma resposta.

    Args:
        request: Objeto contendo a mensagem do usuário

    Returns:
        Dicionário com a resposta gerada
    """
    query = request.message
    info(f"Recebida mensagem: {query[:50]}...")
    keywords = extract_keywords(query)

    try:
        # Buscar documentos relevantes
        docs_and_scores = _buscar_documentos(query, keywords)

        # Log retrieved documents and scores
        for doc, score in docs_and_scores:
            preview = doc.page_content[:100].replace("\n", " ")
            info(
                f"Score: {score:.4f} | Tema: {doc.metadata.get('tema', 'N/A')} | Preview: {preview}"
            )

        # If no documents found after all attempts, log it.
        if not docs_and_scores:
            warning(
                "Nenhum documento encontrado para a query. Pergunta fora do escopo."
            )
            with open(
                "logs/perguntas_fora_do_escopo.log", "a", encoding="utf-8"
            ) as log_file:
                log_file.write(f"{query}\n")
            # Empty docs_and_scores will result in empty context
        else:
            info(
                f"Contexto com {len(docs_and_scores)} documento(s) será usado para gerar resposta."
            )

        # Call the new function to generate response
        response_content = gera_resposta_com_langchain(docs_and_scores, query)
        info("Resposta gerada com sucesso")

        return {"answer": response_content}

    except (ValueError, KeyError, IOError) as specific_error:
        error(f"Erro ao gerar resposta: {str(specific_error)}", exc_info=True)
        return {"answer": "Desculpe, ocorreu um erro ao processar sua mensagem."}
    except Exception as general_error:  # Ainda mantém o handler genérico para segurança
        error(f"Erro inesperado: {str(general_error)}", exc_info=True)
        return {
            "answer": "Desculpe, ocorreu um erro interno ao processar sua mensagem."
        }
