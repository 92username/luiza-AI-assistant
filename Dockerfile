# Replace existing multi-stage build with a simple backend image
FROM python:3.10-slim
WORKDIR /app

# Instala FastAPI, Uvicorn e dotenv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código-fonte
COPY . .

# Expõe a porta padrão do Uvicorn
EXPOSE 8000

# Inicia o serviço com Uvicorn
CMD ["uvicorn", "luiza_fast_api:app", "--host", "0.0.0.0", "--port", "8000"]
