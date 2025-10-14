đẩy data local lên minio: docker-compose run --rm data-processor python scripts/upload_to_minio.py

extract image: docker-compose run --rm data-processor python scripts/extract_docx.py