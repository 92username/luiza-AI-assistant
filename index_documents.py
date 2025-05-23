
import os
"""
Este script indexa documentos Markdown para um sistema de recuperação de texto usando Langchain e OpenAI.

O processo inclui:
1. Carregamento de documentos Markdown do diretório ./docs
2. Fragmentação dos documentos em chunks menores para processamento eficiente
3. Geração de embeddings usando a API da OpenAI
4. Armazenamento dos embeddings no Chroma Vector Database

Dependências:
- langchain
- openai
- chromadb
- python-dotenv

Requisitos:
- Arquivo .env com a variável OPENAI_API_KEY definida
- Diretório ./docs com arquivos Markdown (.md) para indexação

Uso:
    $ python index_documents.py

Saída:
    Os embeddings são armazenados no diretório ./chroma_index
"""
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Carregar variáveis do .env
load_dotenv()

# Verificar se a API KEY está disponível
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("Variável OPENAI_API_KEY não encontrada. Verifique seu .env.")

# Carregar documentos da pasta /docs
docs_path = "./docs"
if not os.path.exists(docs_path):
    raise FileNotFoundError("Pasta ./docs não encontrada. Crie a pasta e adicione arquivos .md.")

print("📄 Carregando arquivos Markdown...")
loader = DirectoryLoader(docs_path, glob="**/*.md")
raw_documents = loader.load()

# Dividir os textos em pedaços menores
print(f"📃 {len(raw_documents)} documentos carregados. Fragmentando...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
documents = text_splitter.split_documents(raw_documents)

# Criar os embeddings e armazenar no Chroma
print("🧠 Gerando embeddings com OpenAI...")
embedding = OpenAIEmbeddings(api_key=api_key)

print("📦 Persistindo índice no diretório ./chroma_index ...")
vectordb = Chroma.from_documents(documents, embedding, persist_directory="./chroma_index")
vectordb.persist()

print("✅ Índice criado com sucesso!")
