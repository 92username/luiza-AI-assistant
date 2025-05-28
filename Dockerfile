# etapa 1: build e indexação
FROM python:3.10-slim AS builder
WORKDIR /app

# 1.1 Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 1.2 Copia código e gera a base vetorial
COPY . .
ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
RUN python index_documents.py

# etapa 2: imagem final mais enxuta
FROM python:3.10-slim
WORKDIR /app

# 2.1 Copia o resultado da indexação e o app
COPY --from=builder /app /app

# 2.2 Expõe porta e define entrypoint
EXPOSE 8000
CMD ["uvicorn", "luiza_fast_api:app", "--host", "0.0.0.0", "--port", "8000"]
