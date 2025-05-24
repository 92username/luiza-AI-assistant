"""
Document loader module for the LangChain RAG project.

This module provides functionality to load and concatenate
markdown files from the docs directory.
"""

import os


def load_docs():
    """
    Procura todos os arquivos .md dentro da pasta /docs/,
    lê e concatena o conteúdo em uma única string.

    Returns:
        str: Conteúdo combinado de todos os arquivos Markdown
    """
    folder = "docs"
    combined = ""

    # Verificar se a pasta existe, criar se não existir
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Pasta {folder} criada. Adicione arquivos .md para fornecer contexto.")
        return combined

    # Iterar pelos arquivos na pasta
    for filename in os.listdir(folder):
        if filename.endswith(".md"):
            file_path = os.path.join(folder, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as file_handle:
                    combined += file_handle.read() + "\n\n"
            except (IOError, OSError, UnicodeDecodeError) as error:
                # Specific exceptions instead of catching generic Exception
                print(f"Erro ao ler o arquivo {filename}: {error}")

    return combined
