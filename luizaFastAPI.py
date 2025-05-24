# filepath: /home/nbx/Documents/Projects/luizaFastAPI/luizaFastAPI.py
from fastapi import FastAPI, Request
from pydantic import BaseModel, SecretStr
import sys
sys.path.append("./langchain_core")
from logger import info, warning, error
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
import re

# Importações da LangChain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

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
    raise EnvironmentError("Variável OPENAI_API_KEY não encontrada. Verifique seu .env.")
api_key = SecretStr(api_key_env)

# Configure chat_model (globally)
chat_model = ChatOpenAI(
    api_key=api_key, # Usar api_key que é do tipo SecretStr, não api_key_env
    model="gpt-4.1-nano",
    temperature=0.7,
    model_kwargs={"max_tokens": 1024}
)

# Cria um embedding_function com modelo compatível
embeddings = OpenAIEmbeddings(
    api_key=api_key,
    model="text-embedding-ada-002"
)

# Carrega o vectorstore persistido
vectordb = Chroma(
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# Função de extração de keywords
def extract_keywords(text: str) -> list[str]:
    # pega só caracteres alfanuméricos separados
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
    message: str

# Criar uma instância de LLMChain com o modelo e o prompt
llm_chain = LLMChain(llm=chat_model, prompt=SYSTEM_PROMPT)

# Nova função para gerar resposta usando LLMChain diretamente
def gera_resposta_com_langchain(docs_and_scores: list, query: str) -> str:
    # 1) Junte o conteúdo dos chunks
    context = "\n\n".join([doc.page_content for doc, _ in docs_and_scores])
    
    # 2) Rode o chain passando os valores
    answer = llm_chain.run({"context": context, "question": query})
    
    return answer

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    query = request.message
    info(f"Recebida mensagem: {query[:50]}...")
    keywords = extract_keywords(query)

    try:
        # 3.1 Detecta quais temas da pergunta batem com TEMAS
        matched_themes = set(keywords) & TEMAS

        docs_and_scores = []  # Initialize to ensure it's always defined

        # 3.2 Monta o retriever condicionando o filtro
        if matched_themes:
            info(f"Temas correspondentes encontrados: {list(matched_themes)}")
            filter_kwargs = {"filter": {"tema": {"$in": list(matched_themes)}}}
            retriever_search_kwargs = {**filter_kwargs, "k": 5}
            retriever = vectordb.as_retriever(search_kwargs=retriever_search_kwargs)
            
            k_val = retriever.search_kwargs.get('k', 5)
            current_filter = retriever.search_kwargs.get('filter')
            docs_and_scores = retriever.vectorstore.similarity_search_with_score(
                query,
                k=k_val,
                filter=current_filter
            )
        else:
            info("Nenhum tema correspondente encontrado, buscando sem filtro de tema.")
            retriever = vectordb.as_retriever(search_kwargs={"k": 5})
            k_val = retriever.search_kwargs.get('k', 5)
            docs_and_scores = retriever.vectorstore.similarity_search_with_score(query, k=k_val)

        # 3.4 Se ainda estiver vazio E HOUVE TENTATIVA DE FILTRO, faz um fallback sem filtro
        if not docs_and_scores and matched_themes:
            info("Fallback: Nenhum documento encontrado com filtro de tema, tentando busca geral.")
            docs_and_scores = vectordb.similarity_search_with_score(query, k=5)

        # Log retrieved documents and scores
        for doc, score in docs_and_scores:
            preview = doc.page_content[:100].replace("\n", " ")
            info(f"Score: {score:.4f} | Tema: {doc.metadata.get('tema', 'N/A')} | Preview: {preview}")

        # If no documents found after all attempts, log it.
        if not docs_and_scores:
            warning("Nenhum documento encontrado para a query. Pergunta fora do escopo.")
            with open("logs/perguntas_fora_do_escopo.log", "a") as f:
                f.write(f"{query}\n")
            # Empty docs_and_scores will result in empty context
        else:
            info(f"Contexto com {len(docs_and_scores)} documento(s) será usado para gerar resposta.")

        # Call the new function to generate response
        response_content = gera_resposta_com_langchain(docs_and_scores, query)
        info("Resposta gerada com sucesso")

        return {"answer": response_content}

    except Exception as e:
        error(f"Erro ao gerar resposta: {str(e)}", exc_info=True)
        return {"answer": "Desculpe, ocorreu um erro ao processar sua mensagem."}
