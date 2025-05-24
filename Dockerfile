FROM python:3.10-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y build-essential

# Copia os arquivos do projeto
COPY . /app

# Instala dependências do Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expõe a porta padrão da API
EXPOSE 8000

# Comando para iniciar o servidor FastAPI com uvicorn
CMD ["uvicorn", "luiza_fast_api:app", "--host", "0.0.0.0", "--port", "8000"]
