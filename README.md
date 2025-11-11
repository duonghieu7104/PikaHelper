# PikaHelper - Hệ thống Chatbot AI cho PokeMMO

Link video demo https://youtu.be/304lJJlljvk

PikaHelper là một hệ thống chatbot AI được thiết kế đặc biệt để hỗ trợ người chơi PokeMMO. Hệ thống sử dụng RAG (Retrieval-Augmented Generation) để trả lời các câu hỏi về game dựa trên tài liệu hướng dẫn tiếng Việt.

## 🚀 Tính năng chính

- **Chatbot AI thông minh**: Trả lời câu hỏi về PokeMMO bằng tiếng Việt
- **Xử lý tài liệu**: Tự động xử lý và lập chỉ mục các file .docx
- **Tìm kiếm ngữ nghĩa**: Sử dụng vector embedding để tìm kiếm thông tin chính xác
- **Giao diện web thân thiện**: Chatbot UI đơn giản và dễ sử dụng
- **Quản lý dữ liệu**: Hệ thống quản lý dữ liệu đa tầng (Bronze, Silver, Gold)

## 🏗️ Kiến trúc hệ thống

<img width="2558" height="2214" alt="Untitled-2025-10-15-0104" src="https://github.com/user-attachments/assets/15a75e4f-5699-43b6-932e-8c2688a79ab0" />

## 🔧 Tại sao không sử dụng LangChain? (Why No LangChain?)

### Về Data Processor (Data Processor Architecture)

Dự án này sử dụng một pipeline xử lý dữ liệu tùy chỉnh thay vì LangChain vì các lý do sau:

#### 1. **Kiểm soát và minh bạch hoàn toàn** (Full Control & Transparency)
- Kiểm soát trực tiếp từng bước xử lý (DOCX parsing, chunking, embedding generation)
- Dễ dàng debug và theo dõi luồng dữ liệu từ Bronze → Silver → Gold layers
- Không có abstraction layer che giấu logic xử lý

#### 2. **Kiến trúc Microservices** (Microservices Architecture)
- Mỗi service có trách nhiệm riêng biệt và được tách biệt hoàn toàn
- **`data-processor`**: Xử lý DOCX extraction, chunking, và metadata extraction
- **`embedding-service`**: Quản lý vector embeddings generation
- Tích hợp trực tiếp giữa các services mà không cần abstraction overhead

#### 3. **Tối ưu hóa cho tiếng Việt** (Vietnamese Language Optimization)
- Tokenization tùy chỉnh cho tiếng Việt sử dụng `pyvi`
- Model embedding chuyên biệt: `huyydangg/DEk21_hcmute_embedding`
- Chiến lược chunking được điều chỉnh đặc biệt cho tài liệu tiếng Việt
- Xử lý trực tiếp văn bản tiếng Việt mà không cần LangChain abstractions

#### 4. **Yêu cầu xử lý đặc biệt** (Custom Requirements)
- **Trích xuất hình ảnh**: Tự động trích xuất hình ảnh từ DOCX và lưu vào MinIO
- **Trích xuất URL**: Phát hiện URL với regex và phân loại (video, download, community, official, external)
- **Metadata phong phú**: Theo dõi hình ảnh, links, chunk indices, position mapping
- **Chunking strategy**: Overlap chunking tùy chỉnh (1000 ký tự với 200 ký tự overlap)
- **Tích hợp database**: Sử dụng trực tiếp PostgreSQL với JSONB cho metadata linh hoạt

#### 5. **Dependencies nhẹ** (Lightweight Dependencies)
- Chỉ sử dụng các thư viện cần thiết: `python-docx`, `minio`, `psycopg2-binary`, `qdrant-client`
- Docker images nhỏ hơn và deployment nhanh hơn
- Không có framework overhead

#### 6. **Hiệu suất** (Performance Considerations)
- Sử dụng trực tiếp các thư viện để đạt hiệu suất tốt hơn
- Batch processing tùy chỉnh cho tập tài liệu lớn
- Quản lý bộ nhớ hiệu quả cho image extraction
- Tối ưu database queries mà không cần ORM overhead

#### 7. **Tích hợp cụ thể** (Specific Integrations)
- Tích hợp trực tiếp với MinIO S3-compatible storage
- Sử dụng PostgreSQL JSONB native cho metadata linh hoạt
- Thao tác trực tiếp với Qdrant vector database
- Orchestration pipeline tùy chỉnh với Apache Airflow

### Tính năng Data Processor

Service `data-processor` cung cấp:

- ✅ **DOCX Processing**: Trích xuất text, images, và links từ file `.docx`
- ✅ **Smart Chunking**: Paragraph-aware chunking với overlap để bảo tồn ngữ cảnh
- ✅ **Image Extraction**: Tự động trích xuất và upload hình ảnh lên MinIO
- ✅ **URL Extraction**: Phát hiện URL bằng regex với context và categorization
- ✅ **Metadata Tracking**: Metadata đầy đủ cho mỗi chunk (images, URLs, positions)
- ✅ **Database Integration**: Lưu trữ trực tiếp vào PostgreSQL với JSONB
- ✅ **Q&A Processing**: Pipeline riêng cho Q&A JSON files có cấu trúc

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
<img width="1262" height="496" alt="15-10-2025screenshot-18-17-34-406" src="https://github.com/user-attachments/assets/8aa59a7c-93b4-4e5f-ae63-2047d0d20150" />

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

Có thể thay đổi dữ liệu khác để RAG truy xuất dữ liệu theo chủ đề của bạn.

<img width="1528" height="665" alt="15-10-2025screenshot-18-22-16-419" src="https://github.com/user-attachments/assets/be8457a5-464a-414d-a8d5-bb10ca5d520b" />

```bash
docker-compose run --rm data-processor python scripts/upload_to_minio.py
```

<img width="1261" height="234" alt="15-10-2025screenshot-18-22-32-113" src="https://github.com/user-attachments/assets/007d801e-4c79-4527-87bf-5c534cfb8f5c" />

#### Bước 2: Trích xuất nội dung từ file DOCX
```bash
docker-compose run --rm data-processor python scripts/extract_docx.py
```

<img width="1233" height="281" alt="15-10-2025screenshot-18-23-36-959" src="https://github.com/user-attachments/assets/bd63cd87-e2d6-4fef-98cf-f9f495df9e8d" />

#### Bước 3: Xử lý dữ liệu Q&A
```bash
docker-compose run --rm data-processor python scripts/process_qa_json.py
```

#### Bước 4: Tạo embedding và lưu vào Qdrant
```bash
docker-compose run --rm embedding-service python scripts/generate_embeddings.py
```

<img width="1248" height="439" alt="15-10-2025screenshot-18-25-24-025" src="https://github.com/user-attachments/assets/b2f68c76-3fcc-46fc-88a7-3dad7f710a38" />

### Quy trình xử lý

Pipeline sẽ thực hiện các bước sau:
- **Upload**: Tải dữ liệu lên MinIO object storage
- **Extract**: Đọc và xử lý các file .docx trong thư mục `data/raw/`
- **Transform**: Chia nhỏ văn bản thành các chunk và xử lý Q&A
- **Load**: Tạo embedding và lưu vào Qdrant vector database

### Chi tiết Data Processing Pipeline

```
Bronze Layer (MinIO) → Silver Layer (PostgreSQL) → Gold Layer (Qdrant)
```

1. **Bronze Layer**: Raw DOCX files được lưu trữ trong MinIO
2. **Silver Layer**: Processed chunks với metadata đầy đủ trong PostgreSQL
3. **Gold Layer**: Vector embeddings trong Qdrant cho semantic search

Mỗi chunk được xử lý với:
- Content text (đã được chunked với overlap)
- Associated images (URLs từ MinIO)
- Extracted URLs với categorization
- Metadata đầy đủ (chunk index, positions, counts)

## 🎯 Sử dụng giao diện

### Bước 1: Truy cập Chatbot UI

1. Mở trình duyệt và truy cập: `http://localhost:3000`
2. Giao diện chatbot sẽ hiển thị

<img width="1413" height="823" alt="15-10-2025screenshot-18-27-13-656" src="https://github.com/user-attachments/assets/8c9811a6-e511-4d6c-b98f-bffee6ef4712" />

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
│   ├── data_processor/    # Xử lý dữ liệu (Custom implementation, no LangChain)
│   │   ├── scripts/
│   │   │   ├── extract_docx.py      # DOCX text/image/URL extraction
│   │   │   ├── process_qa_json.py   # Q&A processing
│   │   │   └── upload_to_minio.py   # MinIO upload utility
│   │   └── requirements.txt
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
