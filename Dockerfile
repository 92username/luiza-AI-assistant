# syntax=docker/dockerfile:1.4

# etapa 1: build e indexação
FROM python:3.10-slim AS builder
ARG OPENAI_API_KEY
WORKDIR /app

# 1.1 Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 1.2 Copia código e gera a base vetorial
COPY . .
RUN --mount=type=secret,id=openai_api_key \
    OPENAI_API_KEY="$(cat /run/secrets/openai_api_key)" \
    python index_documents.py

# etapa 2: imagem final mais enxuta
FROM python:3.13-slim
COPY --from=builder /app /app
WORKDIR /app
EXPOSE 8000
ENTRYPOINT ["python","-m","uvicorn","luiza_fastapi:app","--host","0.0.0.0","--port","8000"]
