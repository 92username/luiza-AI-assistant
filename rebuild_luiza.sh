#!/bin/bash
# Script para rebuildar a imagem da Luiza com cache limpo e subir o container
echo "⛔ Parando e removendo container da Luiza..."
sudo docker-compose down --remove-orphans

echo "🧼 Removendo imagem antiga da Luiza..."
IMAGE_ID=$(docker images | grep luizafastapi_luiza-api | awk '{print $3}')
if [ -n "$IMAGE_ID" ]; then
  sudo docker rmi -f "$IMAGE_ID"
else
  echo "⚠️  Nenhuma imagem antiga encontrada."
fi

echo "🔄 Rebuildando a imagem da Luiza com cache limpo..."
sudo docker-compose build --no-cache

echo "🚀 Subindo o container da Luiza..."
sudo docker-compose up
