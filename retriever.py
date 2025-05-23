#!/usr/bin/env python3
"""
Retriever module for loading relevant documents from a ChromaDB vector store
using semantic similarity search with OpenAI embeddings.
"""

import os
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document

# Import logger for detailed error tracking
try:
    from logger import logger, info, warning, error
except ImportError:
    # Fallback to basic logging if logger module is not available
    import logging

    logger = logging.getLogger(__name__)
    info = logger.info
    warning = logger.warning
    error = logger.error

try:
    from langchain_community.embeddings import OpenAIEmbeddings # Updated import
    from langchain_community.vectorstores import Chroma          # Updated import

except ImportError:
    error_msg = "Required packages not installed. Please run: pip install langchain-openai langchain-community langchain-core" # Adjusted error message slightly
    try:
        error(error_msg)
    except (NameError, AttributeError) as e:
        # Exceções específicas para quando error() não está definido ou não é uma função
        print(f"Logging unavailable: {error_msg}")
    raise ImportError(error_msg)

# Load environment variables (including OPENAI_API_KEY)
load_dotenv()


def load_docs(query: str, k: int = 5, score_threshold: float = 0.65) -> List[Document]:
    """
    Retrieve the most relevant documents from the Chroma vector store based on a query,
    logs scores, and filters by a similarity score threshold.

    Args:
        query (str): The search query text.
        k (int, optional): Number of documents to retrieve initially. Defaults to 5.
        score_threshold (float, optional): Minimum similarity score to consider a document relevant.
                                           Defaults to 0.65.

    Returns:
        List[Document]: A list of Document objects containing the most relevant text chunks
                        that meet the score threshold.

    Raises:
        ValueError: If the OPENAI_API_KEY is not found in environment variables.
        FileNotFoundError: If no documents are found with a score >= score_threshold.
    """
    if not os.getenv("OPENAI_API_KEY"):
        # Consider using the logger.error here as in previous versions for consistency if desired
        raise ValueError("OPENAI_API_KEY not found")

    # Path to the persisted Chroma database
    chroma_dir = "./chroma_index" # Assuming this path is correct and DB exists.
                                  # Previous version had an explicit check.

    # Initialize the embedding model
    embeddings = OpenAIEmbeddings()

    # Load the existing Chroma vector store
    vectordb = Chroma(persist_directory=chroma_dir, embedding_function=embeddings)

    # Busca com scores
    docs_and_scores = vectordb.similarity_search_with_score(query, k=k)

    # Logar os scores para debug
    info(f"--- Similaridade para a query: '{query}' ---")
    for doc, score in docs_and_scores:
        snippet = doc.page_content[:60].replace("\\n", " ")
        info(f"Score: {score:.4f} | {snippet}...")

    # Filtrar por similaridade mínima
    filtered_docs = [doc for doc, score in docs_and_scores if score >= score_threshold]

    if not filtered_docs:
        warning(f"Nenhum documento acima do threshold ({score_threshold}) para a query: '{query}'")
        raise FileNotFoundError(f"Nenhum documento relevante com score >= {score_threshold}")

    info(f"Busca concluída. Encontrados {len(filtered_docs)} documentos relevantes após filtro (threshold={score_threshold}).")
    return filtered_docs


# Example code is commented out to avoid the "pointless string statement" warning
# Example usage:
# docs = load_docs("O que é o MVP do projeto?")
# for i, doc in enumerate(docs):
#     print(f"Trecho {i+1}:", doc.page_content)
