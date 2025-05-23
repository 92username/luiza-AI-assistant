from fastapi import FastAPI, Request
from pydantic import BaseModel
import sys
sys.path.append("./langchain_core")  # precisa vir antes dos imports abaixo
from retriever import load_docs
from logger import info, warning, error
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # ou "*" se quiser liberar geral no dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

system_message = """
Você é a Luiza, a assistente virtual da EstudaMais.tech — uma plataforma que ajuda estudantes universitários a desbloquear o máximo dos benefícios do GitHub Student Pack.
Você é animada, prestativa, acolhedora e gosta de explicar as coisas com entusiasmo, como se estivesse torcendo pelo sucesso do usuário. Use um tom leve e otimista, mas mantenha a precisão das informações.
Evite parecer robótica ou formal demais.

Missão:
Guiar estudantes universitários sobre:
• GitHub Student Developer Pack (GHSP)
• Ferramentas gratuitas/educacionais
• Oportunidades na Estácio e na EstudaMais

Estilo:
• Linguagem acessível e motivadora, porém direta.
• Máx. 3 parágrafos ou 200 palavras (salvo pedido do usuário).
• Use listas com `-` se melhorar a clareza.
• Cite exemplos práticos sempre que possível.

Política:
Se não souber, responda "Não tenho essa informação no momento" e ofereça canal de contato.
Nunca invente dados numéricos.
"""

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_input = request.message
    info(f"Recebida mensagem: {user_input[:50]}...")

    try:
        retrieved_docs = load_docs(user_input, k=5)
        context = "\\n\\n".join(doc.page_content for doc in retrieved_docs or [])

        if not context:
            warning("Nenhum documento encontrado para a query. Pergunta fora do escopo.")
            with open("logs/perguntas_fora_do_escopo.log", "a") as f:
                f.write(f"{user_input}\\n")
            return {"response": "Desculpe, não encontrei informações sobre isso nos meus documentos. Tente perguntar algo relacionado à EstudaMais.tech ou GitHub Student Pack."}
        else:
            info(f"Contexto recuperado: {context[:50]}...")

        llm = ChatOpenAI(
            model_name="gpt-4.1-nano",
            temperature=0.7,
            max_tokens=700,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        messages = [
            {"role": "system", "content": system_message + "\n\n" + context},
            {"role": "user", "content": user_input},
        ]

        response = llm.invoke(messages)
        response_content = response.content
        info("Resposta gerada com sucesso")

        return { "response": response_content }

    except Exception as e:
        error(f"Erro ao gerar resposta: {str(e)}", exc_info=True)
        return { "response": "Desculpe, ocorreu um erro ao processar sua mensagem." }
