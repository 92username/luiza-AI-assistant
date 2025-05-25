[![Build and Push Docker Image](https://github.com/92username/luiza-AI-assistant/actions/workflows/main.yml/badge.svg)](https://github.com/92username/luiza-AI-assistant/actions/workflows/main.yml) [![Deploy Luiza](https://github.com/92username/luiza-AI-assistant/actions/workflows/deploy.yml/badge.svg)](https://github.com/92username/luiza-AI-assistant/actions/workflows/deploy.yml)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Docker-Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![LangChain](https://img.shields.io/badge/langchain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white) ![ChatGPT](https://img.shields.io/badge/ChatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)

![Docker stats](https://img.shields.io/badge/Docker%20/%20stats-blue?logo=docker)
[![Docker Image Size](https://img.shields.io/docker/image-size/user92/luiza-fastapi/latest)](https://hub.docker.com/r/user92/luiza-fastapi)
[![Docker Pulls](https://img.shields.io/docker/pulls/user92/luiza-fastapi)](https://hub.docker.com/r/user92/luiza-fastapi)
[![OpenAI API](https://img.shields.io/badge/OpenAI-API-4BDBF4?logo=openai)](https://platform.openai.com/)
[![LangChain](https://img.shields.io/badge/LangChain-enabled-brightgreen)](https://www.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-vector%20store-lightgreen)](https://www.trychroma.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async%20API-009688?logo=fastapi)](https://fastapi.tiangolo.com/)


# Luiza — IA Assistente da EstudaMais.tech
---

Luiza é uma assistente virtual inteligente que utiliza **RAG (Retrieval-Augmented Generation)** com **LangChain** e **OpenAI** para responder perguntas baseadas em documentos internos da EstudaMais.tech. Seu objetivo é oferecer suporte contextualizado sobre a plataforma, produtos e iniciativas como o GitHub Student Pack (GHSP).

## 📌 O que é este projeto?

Este projeto implementa um sistema de **perguntas e respostas com base em contexto interno** (arquivos `.md`), acessível via API FastAPI. As respostas são geradas utilizando **LLM da OpenAI**, com suporte à busca vetorial em uma base indexada com **ChromaDB**.

---

## ✅ Funcionalidades

- Carregamento e indexação automática de documentos Markdown na pasta `/docs`.
- Fragmentação dos documentos e geração de embeddings com OpenAI.
- Armazenamento persistente em ChromaDB.
- RAG com busca por similaridade vetorial (com e sem filtro por tema).
- API FastAPI com endpoint `/chat`.
- Respostas geradas via LLMChain (LangChain).
- Log de interações e fallback para perguntas fora do escopo.

---

## 🚀 Como funciona?

### 1. Indexação (`index_documents.py`)
- Lê os arquivos Markdown da pasta `./docs`.
- Divide o conteúdo em pequenos blocos (chunks).
- Gera embeddings usando `text-embedding-ada-002`.
- Persiste os vetores no diretório `./chroma_db`.

### 2. API (`luizaFastAPI.py`)
- Endpoint `/chat` recebe uma mensagem do usuário.
- Busca os documentos mais relevantes no banco vetorial.
- Constrói o contexto com os chunks recuperados.
- Gera a resposta com um modelo LLM (`gpt-4.1-nano`) e o `PromptTemplate` pré-definido.
- Registra logs e respostas em CSV para futuras análises (ex: geração de FAQ).

---

## 🧰 Tecnologias e Ferramentas Utilizadas

| Tecnologia/Ferramenta  | Uso Principal |
|------------------------|---------------|
| [FastAPI](https://fastapi.tiangolo.com/) | Criação da API HTTP |
| [LangChain](https://www.langchain.com/) | Construção do pipeline RAG (retrieval + geração) |
| [OpenAI API](https://platform.openai.com/docs) | Geração de embeddings e respostas |
| [ChromaDB](https://www.trychroma.com/) | Armazenamento e busca vetorial |
| [Markdown](https://www.markdownguide.org/) | Fonte de contexto em `/docs/*.md` |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Carregamento seguro da API Key |
| [logging + CSV](https://docs.python.org/3/library/logging.html) | Log de erros e interações do usuário |
| [Pydantic](https://docs.pydantic.dev/) | Validação de requisições FastAPI |

---

## 📁 Estrutura do Projeto

.
├── docs/ # Arquivos Markdown usados como fonte de conhecimento
├── chroma_db/ # Diretório onde o banco vetorial Chroma é persistido
├── logs/ # Logs de erros e CSV com perguntas e respostas
│ └── conversas.csv
├── index_documents.py # Script para indexar os documentos
├── loader.py # Função auxiliar para carregar os .md
├── luizaFastAPI.py # API principal da assistente
├── logger.py # Logger com suporte a CSV e arquivos rotativos
└── .env # Contém a OPENAI_API_KEY (não versionado)


---

## 📡 Endpoint da API

- **POST `/chat`**
  - Requisição:
    ```json
    { "message": "O que é a EstudaMais.tech?" }
    ```
  - Resposta:
    ```json
    { "answer": "A EstudaMais.tech é uma..." }
    ```

---

## 🔒 Requisitos

- Python 3.11+
- Chave de API da OpenAI (no arquivo `.env`)
- Documentos `.md` em `./docs`
- Dependências:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🎯 Resultado Esperado

- O sistema responde perguntas com base apenas nos arquivos internos fornecidos.
- Caso a pergunta esteja fora do escopo, Luiza responde de forma gentil e clara com uma mensagem padrão.

> Exemplo de resposta fora do escopo:
> *"Não tenho essa informação no momento. Deseja perguntar algo relacionado à EstudaMais.tech ou ao GitHub Student Pack (GHSP)? 😊"*

---

## 🛠️ Contribuição

Contribuições são bem-vindas! Verifique se os arquivos `.md` foram adicionados à pasta `/docs` com nomes padronizados (`01-visao-geral.md`, `02-plataforma.md`, etc) para melhor organização por tema.

---
