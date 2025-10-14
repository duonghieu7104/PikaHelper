#!/bin/bash
# Script to copy Vietnamese embedding model to container

echo "Copying Vietnamese embedding model to container..."

# Check if model directory exists
if [ ! -d "models/embedding" ]; then
    echo "Error: models/embedding directory not found!"
    echo "Please ensure you have the Vietnamese embedding model in models/embedding/"
    exit 1
fi

# Create models directory in container if it doesn't exist
docker exec pika_embedding_service mkdir -p /app/models/embedding 2>/dev/null || true

# Copy model files to container
echo "Copying model files..."
docker cp models/embedding/. pika_embedding_service:/app/models/embedding/

echo "Model copied successfully!"
echo "You can now restart the embedding service:"
echo "docker-compose restart embedding-service"
