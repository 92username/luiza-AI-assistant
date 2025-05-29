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

# etapa 2: final
FROM python:3.10-slim
WORKDIR /app
# 1) Copia dependências instaladas
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
# 2) Copia o código e artefatos de indexação
COPY --from=builder /app /app
EXPOSE 8000
CMD ["uvicorn","luiza_fast_api:app","--host","0.0.0.0","--port","8000"]
