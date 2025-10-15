"""
PikaHelper Docker Pipeline DAG
Sử dụng DockerOperator để chạy các container khác
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

# Default arguments
default_args = {
    'owner': 'pikahelper',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

# Create DAG
dag = DAG(
    'pikahelper_docker_pipeline',
    default_args=default_args,
    description='PikaHelper Docker Pipeline - Chạy các container khác',
    schedule_interval=None,  # Chạy thủ công
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['pikahelper', 'docker', 'orchestration'],
)

# Task 1: Upload data to MinIO
upload_data = DockerOperator(
    task_id='upload_data_to_minio',
    image='pika_data_processor:latest',
    command='python scripts/upload_to_minio.py',
    environment={
        'MINIO_ENDPOINT': 'minio:9000',
        'MINIO_ACCESS_KEY': 'admin',
        'MINIO_SECRET_KEY': 'password123',
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_DB': 'pikadb',
        'POSTGRES_USER': 'pika_user',
        'POSTGRES_PASSWORD': 'pika_pass'
    },
    network_mode='pikahelper_pika_network',
    dag=dag,
)

# Task 2: Extract DOCX content
extract_docx = DockerOperator(
    task_id='extract_docx_content',
    image='pika_data_processor:latest',
    command='python scripts/extract_docx.py',
    environment={
        'MINIO_ENDPOINT': 'minio:9000',
        'MINIO_ACCESS_KEY': 'admin',
        'MINIO_SECRET_KEY': 'password123',
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_DB': 'pikadb',
        'POSTGRES_USER': 'pika_user',
        'POSTGRES_PASSWORD': 'pika_pass'
    },
    network_mode='pikahelper_pika_network',
    dag=dag,
)

# Task 3: Process Q&A data
process_qa = DockerOperator(
    task_id='process_qa_data',
    image='pika_data_processor:latest',
    command='python scripts/process_qa_json.py',
    environment={
        'MINIO_ENDPOINT': 'minio:9000',
        'MINIO_ACCESS_KEY': 'admin',
        'MINIO_SECRET_KEY': 'password123',
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_DB': 'pikadb',
        'POSTGRES_USER': 'pika_user',
        'POSTGRES_PASSWORD': 'pika_pass'
    },
    network_mode='pikahelper_pika_network',
    dag=dag,
)

# Task 4: Generate embeddings
generate_embeddings = DockerOperator(
    task_id='generate_embeddings',
    image='pika_embedding_service:latest',
    command='python scripts/generate_embeddings.py',
    environment={
        'QDRANT_HOST': 'qdrant',
        'QDRANT_PORT': '6333',
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_DB': 'pikadb',
        'POSTGRES_USER': 'pika_user',
        'POSTGRES_PASSWORD': 'pika_pass'
    },
    network_mode='pikahelper_pika_network',
    dag=dag,
)

# Task 5: Test RAG system
test_rag = DockerOperator(
    task_id='test_rag_system',
    image='pika_embedding_service:latest',
    command='python rag_scripts/rag_query.py "Làm thế nào để tải game PokeMMO?"',
    environment={
        'QDRANT_HOST': 'qdrant',
        'QDRANT_PORT': '6333',
        'GEMINI_API_KEY': '${GEMINI_API_KEY}'
    },
    network_mode='pikahelper_pika_network',
    dag=dag,
)

# Task 6: Pipeline complete
pipeline_complete = DockerOperator(
    task_id='pipeline_complete',
    image='alpine:latest',
    command='echo "🎉 PikaHelper Pipeline Completed Successfully!"',
    dag=dag,
)

# Define task dependencies - Sequential execution
upload_data >> extract_docx >> process_qa >> generate_embeddings >> test_rag >> pipeline_complete
