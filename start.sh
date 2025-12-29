#!/bin/bash

echo "Starting PikaHelper RAG System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo ".env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your GEMINI_API_KEY"
    exit 1
fi

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=.*[^[:space:]]" .env; then
    echo "GEMINI_API_KEY is not set in .env"
    echo "Please edit .env and add your GEMINI_API_KEY"
    exit 1
fi

# Start services
echo "Starting Docker services..."
docker compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check services
echo "Checking services..."
docker compose ps

echo ""
echo "PikaHelper is running!"
echo ""
echo "API Endpoints:"
echo "   - Health: http://localhost:8000/api/health"
echo "   - Stats:  http://localhost:8000/api/stats"
echo "   - Query:  http://localhost:8000/api/query (POST)"
echo ""
echo "Web UIs:"
echo "   - MinIO Console: http://localhost:9001 (admin/password123)"
echo "   - Qdrant Dashboard: http://localhost:6333/dashboard"
echo ""
echo "Next steps:"
echo "   1. Upload DOCX files to data/raw/"
echo "   2. Run: docker compose exec data-processor python scripts/upload_to_minio.py"
echo "   3. Run: docker compose exec data-processor python scripts/extract_docx.py"
echo "   4. Run: docker compose exec data-processor python scripts/generate_embeddings.py"
echo ""

