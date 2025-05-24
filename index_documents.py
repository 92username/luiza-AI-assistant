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
from langchain_community.document_loaders import DirectoryLoader # Updated import
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma # Updated import
from langchain_openai import OpenAIEmbeddings # Updated import
from pydantic import SecretStr # Added import

# Carregar variáveis do .env
load_dotenv()

# Verificar se a API KEY está disponível
api_key_str = os.getenv("OPENAI_API_KEY")
if not api_key_str:
    raise EnvironmentError("Variável OPENAI_API_KEY não encontrada. Verifique seu .env.")
api_key_secret = SecretStr(api_key_str) # Use SecretStr

if __name__ == "__main__":
    # Carregar documentos da pasta /docs
    docs_path = "./docs"
    if not os.path.exists(docs_path):
        raise FileNotFoundError("Pasta ./docs não encontrada. Crie a pasta e adicione arquivos .md.")

    print("📄 Carregando arquivos Markdown...")
    # 1.1 Carrega todos os .md de /docs
    loader = DirectoryLoader(docs_path, glob="*.md")
    raw_documents = loader.load()

    # Dividir os textos em pedaços menores
    print(f"📃 {len(raw_documents)} documentos carregados. Fragmentando...")
    # 1.2 Configura o splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\\n\\n", "\\n", ".", " "]
    )
    # 1.3 Gera os chunks
    documents = text_splitter.split_documents(raw_documents)

    # 2. Atribuir “tema” com base no nome do arquivo
    print("🏷️ Atribuindo metadados 'tema'...")
    for doc in documents:
        src = doc.metadata["source"]  # ex: "docs/03-proposta-de-valor-e-mvp.md"
        filename = os.path.basename(src) # ex: "03-proposta-de-valor-e-mvp.md"
        if filename.startswith("01-"):
            doc.metadata["tema"] = "visao-geral"
        elif filename.startswith("02-"):
            doc.metadata["tema"] = "plataforma"
        elif filename.startswith("03-"):
            doc.metadata["tema"] = "mvp"
        elif filename.startswith("04-"):
            doc.metadata["tema"] = "comecar"
        elif filename.startswith("05-"):
            doc.metadata["tema"] = "fontes"
        else:
            doc.metadata["tema"] = None


    # Criar os embeddings e armazenar no Chroma
    print("🧠 Gerando embeddings com OpenAI...")
    # 3.1 Cria embeddings
    embedding = OpenAIEmbeddings(api_key=api_key_secret, model="text-embedding-ada-002") # Updated model and use SecretStr

    print("📦 Persistindo índice no diretório ./chroma_db ...")
    # 3.2 Monta o Chroma
    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory="./chroma_db"
    )
    # 3.3 Persiste em disco
    vectordb.persist()

    print("✅ Índice criado com sucesso!")
