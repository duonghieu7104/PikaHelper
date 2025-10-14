- đẩy data local lên minio: docker-compose run --rm data-processor python scripts/upload_to_minio.py

- extract image: docker-compose run --rm data-processor python scripts/extract_docx.py

- upload silver q-a json: docker-compose run --rm data-processor python scripts/process_qa_json.py


- tạo embedding: docker-compose run --rm embedding-service python scripts/generate_embeddings.py


- rag tạo container mới: docker-compose run --rm embedding-service python rag_scripts/rag_query.py "Làm thế nào để tải game PokeMMO cho IOS?"

- rag tối ưu: docker-compose exec embedding-service python rag_scripts/rag_query.py "xây dựng đội hình PvP công "

- rag interactive (tối ưu nhất): docker-compose exec embedding-service python rag_scripts/rag_query.py