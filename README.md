# PikaHelper - Hệ thống Chatbot AI cho PokeMMO

PikaHelper là một hệ thống chatbot AI được thiết kế đặc biệt để hỗ trợ người chơi PokeMMO. Hệ thống sử dụng RAG (Retrieval-Augmented Generation) để trả lời các câu hỏi về game dựa trên tài liệu hướng dẫn tiếng Việt.

## 🚀 Tính năng chính

- **Chatbot AI thông minh**: Trả lời câu hỏi về PokeMMO bằng tiếng Việt
- **Xử lý tài liệu**: Tự động xử lý và lập chỉ mục các file .docx
- **Tìm kiếm ngữ nghĩa**: Sử dụng vector embedding để tìm kiếm thông tin chính xác
- **Giao diện web thân thiện**: Chatbot UI đơn giản và dễ sử dụng
- **Quản lý dữ liệu**: Hệ thống quản lý dữ liệu đa tầng (Bronze, Silver, Gold)

## 🏗️ Kiến trúc hệ thống

<img width="2012" height="1504" alt="Untitled-2025-10-15-0104" src="https://github.com/user-attachments/assets/fc78e210-ce5e-47b2-b555-9def207f334f" />


## 📋 Yêu cầu hệ thống

- **Docker & Docker Compose**: Phiên bản mới nhất
- **RAM**: Tối thiểu 8GB (khuyến nghị 16GB)
- **GPU**: Khuyến nghị có GPU NVIDIA để tăng tốc embedding
- **Dung lượng**: Tối thiểu 10GB trống

## 🛠️ Hướng dẫn cài đặt

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd PikaHelper
```

### Bước 2: Tạo file .env

Tạo file `.env` trong thư mục gốc của dự án:

```bash
# Tạo file .env
touch .env
```

Thêm nội dung sau vào file `.env`:

```env
# Gemini API Key - Bắt buộc để sử dụng AI
GEMINI_API_KEY=your_gemini_api_key_here
```

**Lưu ý quan trọng**: 
- Thay `your_gemini_api_key_here` bằng API key thực tế của bạn từ Google AI Studio
- Không commit file `.env` vào git (đã có trong .gitignore)

### Bước 3: Khởi động hệ thống

```bash
# Khởi động tất cả services
docker-compose up -d

# Kiểm tra trạng thái các container
docker-compose ps
```

### Bước 4: Chờ hệ thống khởi động hoàn tất

Hệ thống sẽ mất khoảng 2-5 phút để khởi động hoàn tất. Bạn có thể kiểm tra logs:

```bash
# Xem logs của tất cả services
docker-compose logs -f

# Xem logs của service cụ thể
docker-compose logs -f chatbot-api
```

## 📊 Xử lý dữ liệu

### Chạy pipeline xử lý dữ liệu

Sau khi hệ thống đã khởi động hoàn tất, chạy các lệnh sau để xử lý dữ liệu:

#### Bước 1: Upload dữ liệu lên MinIO
```bash
docker-compose run --rm data-processor python scripts/upload_to_minio.py
```

#### Bước 2: Trích xuất nội dung từ file DOCX
```bash
docker-compose run --rm data-processor python scripts/extract_docx.py
```

#### Bước 3: Xử lý dữ liệu Q&A
```bash
docker-compose run --rm data-processor python scripts/process_qa_json.py
```

#### Bước 4: Tạo embedding và lưu vào Qdrant
```bash
docker-compose run --rm embedding-service python scripts/generate_embeddings.py
```

### Quy trình xử lý

Pipeline sẽ thực hiện các bước sau:
- **Upload**: Tải dữ liệu lên MinIO object storage
- **Extract**: Đọc và xử lý các file .docx trong thư mục `data/raw/`
- **Transform**: Chia nhỏ văn bản thành các chunk và xử lý Q&A
- **Load**: Tạo embedding và lưu vào Qdrant vector database

## 🎯 Sử dụng giao diện

### Bước 1: Truy cập Chatbot UI

1. Mở trình duyệt và truy cập: `http://localhost:3000`
2. Giao diện chatbot sẽ hiển thị

### Bước 2: Bắt đầu chat

1. Nhập câu hỏi về PokeMMO bằng tiếng Việt
2. Ví dụ: "Làm thế nào để tải game PokeMMO?"
3. Hệ thống sẽ trả lời dựa trên tài liệu đã được xử lý

## 🔧 Các dịch vụ và cổng

| Service | Port | Mô tả |
|---------|------|-------|
| **Chatbot UI** | 3000 | Giao diện web chính |
| **Chatbot API** | 8000 | API backend |
| **Adminer** | 8082 | Quản lý database |
| **MinIO** | 9000, 9001 | Object storage |
| **PostgreSQL** | 5432 | Database chính |
| **Qdrant** | 6333, 6334 | Vector database |
| **Redis** | 6379 | Cache |


### Dừng hệ thống

```bash
# Dừng tất cả services
docker-compose down

# Dừng và xóa volumes (cẩn thận - sẽ mất dữ liệu)
docker-compose down -v
```

## 📁 Cấu trúc thư mục

```
PikaHelper/
├── data/raw/              # Tài liệu gốc (.docx files)
├── dags/                  # Airflow DAGs
├── services/              # Các microservices
│   ├── chatbot_api/       # API backend
│   ├── chatbot_ui/        # Web UI
│   ├── data_processor/    # Xử lý dữ liệu
│   └── embedding_service/ # Tạo embedding
├── models/                # Model files
├── cache/                 # Cache cho models
└── docker-compose.yml     # Cấu hình Docker
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📄 License

Dự án này được phát hành dưới giấy phép MIT.

## 📚 Citation

### Model Embedding được sử dụng

Dự án PikaHelper sử dụng model embedding tiếng Việt `DEk21_hcmute_embedding` để xử lý văn bản tiếng Việt trong hệ thống RAG. Model này được sử dụng để:

- Tạo vector embedding cho các chunk văn bản từ tài liệu PokeMMO
- Thực hiện tìm kiếm ngữ nghĩa trong Qdrant vector database
- Hỗ trợ chatbot trả lời câu hỏi bằng tiếng Việt

**Citation cho model embedding:**

```bibtex
@misc{DEk21_hcmute_embedding,
  title={DEk21_hcmute_embedding: A Vietnamese Text Embedding},
  author={QUANG HUY},
  year={2025},
  publisher={Huggingface},
  url={https://huggingface.co/huyydangg/DEk21_hcmute_embedding}
}
```



## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng tạo issue trên GitHub hoặc liên hệ qua email.

---

**Lưu ý**: Đảm bảo bạn có API key hợp lệ từ Google AI Studio để sử dụng tính năng AI của hệ thống.
