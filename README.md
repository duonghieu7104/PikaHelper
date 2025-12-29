# PikaHelper - Simple RAG API

Hệ thống RAG API đơn giản cho PokeMMO, cung cấp REST API để tích hợp vào các ứng dụng web khác.

## 🏗️ Kiến trúc

```
┌─────────────────────────────────────┐
│      Your Web Application           │
└──────────────┬──────────────────────┘
               │ HTTP/REST
               ▼
┌─────────────────────────────────────┐
│         RAG API (Port 8000)         │
│  - POST /api/query                  │
│  - GET  /api/health                 │
│  - GET  /api/stats                  │
└──────┬──────────────┬───────────────┘
       │              │
       ▼              ▼
┌──────────┐    ┌──────────┐
│PostgreSQL│    │  Qdrant  │
│  (Meta)  │    │(Vectors) │
└──────────┘    └──────────┘
       ▲              ▲
       │              │
┌──────┴──────────────┴───────┐
│  MinIO (DOCX + Images)      │
└─────────────────────────────┘
```

## 📦 Services

- **PostgreSQL**: Lưu metadata (documents, chunks, qa_pairs)
- **Qdrant**: Vector database cho embeddings
- **MinIO**: Object storage cho DOCX files và images
- **RAG API**: REST API endpoint
- **Data Processor**: Container để chạy scripts xử lý data

## 🚀 Cài đặt và Sử dụng

### Bước 1: Chuẩn bị

```bash
# Clone repository
git clone <repository-url>
cd PikaHelper

# Tạo file .env
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### Bước 2: Khởi động hệ thống

```bash
# Khởi động tất cả services
docker-compose up -d

# Kiểm tra trạng thái
docker-compose ps
```

### Bước 3: Xử lý dữ liệu

```bash
# 1. Upload DOCX files lên MinIO
docker-compose exec data-processor python scripts/upload_to_minio.py

# 2. Extract và chunk DOCX
docker-compose exec data-processor python scripts/extract_docx.py

# 3. Process Q&A JSON (nếu có)
docker-compose exec data-processor python scripts/process_qa_json.py

# 4. Generate embeddings
docker-compose exec data-processor python scripts/generate_embeddings.py
```

## 📡 API Endpoints

### 1. Query RAG System

**POST** `/api/query`

Request:
```json
{
  "query": "Làm thế nào để tải game PokeMMO?",
  "max_results": 5
}
```

Response:
```json
{
  "query": "Làm thế nào để tải game PokeMMO?",
  "response": "Để tải game PokeMMO...",
  "sources": [
    {
      "file_name": "huong_dan.docx",
      "content": "...",
      "score": 0.85,
      "type": "document"
    }
  ],
  "images": ["http://minio:9000/images/image1.png"],
  "links": ["https://pokemmo.com/downloads"],
  "metadata": {
    "processing_time": 1.23,
    "total_results": 3
  },
  "timestamp": "2025-12-29T10:00:00"
}
```

### 2. Health Check

**GET** `/api/health`

Response:
```json
{
  "status": "healthy",
  "services": {
    "api": "running",
    "rag_engine": "initialized"
  },
  "timestamp": "2025-12-29T10:00:00"
}
```

### 3. System Statistics

**GET** `/api/stats`

Response:
```json
{
  "total_documents": 10,
  "total_chunks": 150,
  "total_embeddings": 150,
  "timestamp": "2025-12-29T10:00:00"
}
```

## 🔧 Cấu hình

### Environment Variables

```env
# Gemini API
GEMINI_API_KEY=your_api_key

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password123

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_DB=pikadb
POSTGRES_USER=pika_user
POSTGRES_PASSWORD=pika_pass

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

## 📁 Cấu trúc thư mục

```
PikaHelper/
├── api/                    # REST API
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── scripts/                # Data processing scripts
│   ├── upload_to_minio.py
│   ├── extract_docx.py
│   ├── process_qa_json.py
│   ├── generate_embeddings.py
│   ├── rag_query.py
│   ├── requirements.txt
│   └── Dockerfile
├── data/
│   └── raw/               # DOCX files để upload
├── init_scripts/
│   └── init_db.sql        # Database schema
├── docker-compose.yml
└── .env
```

## 🌐 Tích hợp vào Web Application

### JavaScript/TypeScript Example

```javascript
// Query RAG API
async function queryRAG(question) {
  const response = await fetch('http://localhost:8000/api/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: question,
      max_results: 5
    })
  });

  const data = await response.json();

  console.log('Answer:', data.response);
  console.log('Sources:', data.sources);
  console.log('Images:', data.images);
  console.log('Links:', data.links);

  return data;
}

// Usage
queryRAG('Làm thế nào để tải game PokeMMO?');
```

### Python Example

```python
import requests

def query_rag(question: str):
    response = requests.post(
        'http://localhost:8000/api/query',
        json={
            'query': question,
            'max_results': 5
        }
    )

    data = response.json()

    print('Answer:', data['response'])
    print('Sources:', data['sources'])
    print('Images:', data['images'])
    print('Links:', data['links'])

    return data

# Usage
query_rag('Làm thế nào để tải game PokeMMO?')
```

## 🛠️ Quản lý

### Xem logs

```bash
# API logs
docker-compose logs -f rag-api

# Data processor logs
docker-compose logs -f data-processor

# All services
docker-compose logs -f
```

### Dừng hệ thống

```bash
# Dừng services
docker-compose down

# Dừng và xóa volumes (cẩn thận!)
docker-compose down -v
```

### Restart services

```bash
# Restart API
docker-compose restart rag-api

# Restart all
docker-compose restart
```

## 📊 Ports

| Service | Port | Description |
|---------|------|-------------|
| RAG API | 8000 | REST API endpoint |
| PostgreSQL | 5432 | Database |
| Qdrant | 6333 | Vector DB HTTP |
| Qdrant gRPC | 6334 | Vector DB gRPC |
| MinIO API | 9000 | Object storage |
| MinIO Console | 9001 | MinIO web UI |

## 🔍 Troubleshooting

### API không khởi động được

```bash
# Check logs
docker-compose logs rag-api

# Rebuild
docker-compose build rag-api
docker-compose up -d rag-api
```

### Embeddings không được tạo

```bash
# Check Qdrant
curl http://localhost:6333/collections

# Re-run embedding generation
docker-compose exec data-processor python scripts/generate_embeddings.py
```

### MinIO không kết nối được

```bash
# Check MinIO
docker-compose logs minio

# Access MinIO console
# http://localhost:9001
# Username: admin
# Password: password123
```

## 📝 Notes

- API sử dụng Gemini 2.5 Flash cho response generation
- Vietnamese embedding model: `huyydangg/DEk21_hcmute_embedding` (768D)
- Quality thresholds: Documents > 0.6, Q&A > 0.7
- Images được boost +0.1 score

## 📄 License

MIT License

