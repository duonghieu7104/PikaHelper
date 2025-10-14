# PikaHelper RAG System

Hệ thống RAG (Retrieval-Augmented Generation) chuyên về hướng dẫn game PokeMMO với kiến trúc Data Lake House.

## 🏗️ Kiến trúc hệ thống

### Data Lake House Layers

1. **Bronze Layer (Raw Data)**
   - Lưu trữ file DOCX gốc trong MinIO
   - Metadata được lưu trong PostgreSQL

2. **Silver Layer (Cleaned Data)**
   - Dữ liệu đã được làm sạch và chia chunk
   - Xử lý text và images từ DOCX
   - Lưu trữ trong MinIO và PostgreSQL

3. **Gold Layer (Vector Embeddings)**
   - Chuyển đổi text thành vector embeddings
   - Lưu trữ trong Qdrant Vector Database
   - Sử dụng mô hình ONNX có sẵn

### Services

- **MinIO**: Object storage cho raw data
- **PostgreSQL**: Metadata và configuration storage
- **Qdrant**: Vector database cho embeddings
- **Redis**: Caching và session management
- **Apache Airflow**: Data processing orchestration
- **Data Processor**: Xử lý DOCX files
- **Embedding Service**: Tạo embeddings với ONNX models
- **Chatbot API**: FastAPI service với Gemini integration
- **Chatbot UI**: React frontend

## 🚀 Cài đặt và chạy

### 1. Chuẩn bị môi trường

```bash
# Clone repository
git clone <repository-url>
cd PikaHelper

# Copy environment file
cp env.example .env

# Chỉnh sửa .env với thông tin của bạn
# Đặc biệt là GEMINI_API_KEY
```

### 2. Setup ONNX Model (Tùy chọn)

Nếu bạn đã có mô hình ONNX, đặt vào thư mục `models/embedding/`:

```bash
models/embedding/
├── model.onnx          # File mô hình ONNX
├── tokenizer/          # Thư mục tokenizer
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   └── vocab.txt
└── config.json         # Cấu hình mô hình
```

Hoặc sử dụng script để tự động setup:

```bash
# Download model files
python scripts/setup_onnx_model.py --download-only

# Convert sang ONNX (cần PyTorch)
python scripts/setup_onnx_model.py --convert-onnx
```

### 3. Chạy hệ thống

```bash
# Khởi động tất cả services
docker-compose up -d

# Kiểm tra trạng thái
docker-compose ps

# Xem logs
docker-compose logs -f
```

### 4. Truy cập các services

- **Chatbot UI**: http://localhost:3000
- **Chatbot API**: http://localhost:8000
- **Embedding Service**: http://localhost:8001
- **Airflow UI**: http://localhost:8080 (admin/admin)
- **MinIO Console**: http://localhost:9001 (admin/password123)
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## 📊 Xử lý dữ liệu

### 1. Chuẩn bị dữ liệu

Đặt các file DOCX vào thư mục `data/raw/` theo cấu trúc:

```
data/raw/
├── HƯỚNG DẪN 1 Bài học vỡ lòng cho người chơi mới/
│   ├── Cách Mod hình ảnh 3D cho Game.docx
│   ├── Cách tải game cho điện thoại IOS.docx
│   └── ...
├── HƯỚNG DẪN 2 Hoàn thành cốt truyện PokeMMO/
│   ├── Hướng dẫn hoàn thành cốt truyện Pokemon Black - Vùng Unova.docx
│   └── ...
└── ...
```

### 2. Chạy data processing pipeline

```bash
# Chạy Airflow DAG
# Truy cập http://localhost:8080
# Tìm DAG "pika_data_processing" và trigger

# Hoặc chạy manual processing
docker-compose exec data-processor python main.py
```

### 3. Tạo embeddings

```bash
# Gọi API để tạo embeddings
curl -X POST http://localhost:8001/embed/process-chunks
```

## 🤖 Sử dụng Chatbot

### API Endpoints

#### Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Làm thế nào để tải game PokeMMO?",
    "session_id": "optional_session_id"
  }'
```

#### Search
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "PvP",
    "limit": 5
  }'
```

### Web UI

Truy cập http://localhost:3000 để sử dụng giao diện web.

## 🔧 Cấu hình

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | API key cho Gemini | Required |
| `POSTGRES_HOST` | PostgreSQL host | localhost |
| `POSTGRES_DB` | Database name | pikadb |
| `POSTGRES_USER` | Database user | pika_user |
| `POSTGRES_PASSWORD` | Database password | pika_pass |
| `MINIO_ENDPOINT` | MinIO endpoint | localhost:9000 |
| `MINIO_ACCESS_KEY` | MinIO access key | admin |
| `MINIO_SECRET_KEY` | MinIO secret key | password123 |
| `QDRANT_HOST` | Qdrant host | localhost |
| `QDRANT_PORT` | Qdrant port | 6333 |
| `REDIS_HOST` | Redis host | localhost |
| `REDIS_PORT` | Redis port | 6379 |

### Model Configuration

Embedding service hỗ trợ cả ONNX models và sentence-transformers:

- **ONNX Model**: Đặt vào `models/embedding/model.onnx`
- **Fallback**: Sử dụng `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384
- **Distance metric**: Cosine
- **Chunk size**: 1000 characters
- **Chunk overlap**: 200 characters

## 📈 Monitoring

### Health Checks

```bash
# Chatbot API
curl http://localhost:8000/health

# Embedding Service
curl http://localhost:8001/health

# Stats
curl http://localhost:8000/stats
curl http://localhost:8001/stats
```

### Logs

```bash
# Xem logs của tất cả services
docker-compose logs -f

# Xem logs của service cụ thể
docker-compose logs -f chatbot-api
docker-compose logs -f embedding-service
docker-compose logs -f data-processor
```

## 🛠️ Development

### Cấu trúc project

```
PikaHelper/
├── docker-compose.yml
├── env.example
├── README.md
├── data/
│   └── raw/                 # Raw DOCX files
├── models/
│   └── embedding/           # ONNX model files
├── services/
│   ├── data_processor/     # Bronze to Silver processing
│   ├── embedding_service/   # Silver to Gold processing
│   ├── chatbot_api/        # Chatbot API with Gemini
│   └── chatbot_ui/         # React frontend
├── scripts/
│   └── setup_onnx_model.py # Model setup script
├── dags/                   # Airflow DAGs
├── init_scripts/           # Database initialization
└── logs/                   # Airflow logs
```

### Thêm dữ liệu mới

1. Đặt file DOCX vào `data/raw/`
2. Chạy data processing pipeline
3. Tạo embeddings cho chunks mới
4. Restart chatbot service nếu cần

### Customization

- **Embedding Model**: Thay đổi trong `services/embedding_service/main.py`
- **Chunk Size**: Điều chỉnh trong `services/data_processor/data_cleaner.py`
- **UI Theme**: Sửa trong `services/chatbot_ui/src/App.js`
- **Prompt Template**: Cập nhật trong `services/chatbot_api/main.py`

## 🐛 Troubleshooting

### Common Issues

1. **Gemini API Error**
   - Kiểm tra `GEMINI_API_KEY` trong `.env`
   - Đảm bảo API key hợp lệ

2. **Database Connection Error**
   - Kiểm tra PostgreSQL service
   - Xem logs: `docker-compose logs postgres`

3. **Vector Search không hoạt động**
   - Kiểm tra Qdrant service
   - Đảm bảo embeddings đã được tạo

4. **File Processing Error**
   - Kiểm tra file DOCX có hợp lệ không
   - Xem logs: `docker-compose logs data-processor`

5. **ONNX Model Error**
   - Kiểm tra file model.onnx có tồn tại không
   - Xem logs: `docker-compose logs embedding-service`

### Reset System

```bash
# Dừng tất cả services
docker-compose down

# Xóa volumes (cẩn thận!)
docker-compose down -v

# Khởi động lại
docker-compose up -d
```

## 📝 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📞 Support

Nếu gặp vấn đề, vui lòng tạo issue trên GitHub repository.