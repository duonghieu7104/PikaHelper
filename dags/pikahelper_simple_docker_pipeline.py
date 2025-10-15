"""
PikaHelper Simple Docker Pipeline DAG
Sử dụng docker run để chạy các container
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

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
    'pikahelper_simple_docker_pipeline',
    default_args=default_args,
    description='PikaHelper Simple Docker Pipeline - Chạy container đơn giản',
    schedule_interval=None,  # Chạy thủ công
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['pikahelper', 'simple', 'docker'],
)

# Task 1: Upload data to MinIO
upload_data = BashOperator(
    task_id='upload_data_to_minio',
    bash_command='''
    echo "📤 Step 1: Upload data to MinIO..."
    docker run --rm --network pikahelper_pika_network \
    -e MINIO_ENDPOINT=minio:9000 \
    -e MINIO_ACCESS_KEY=admin \
    -e MINIO_SECRET_KEY=password123 \
    -e POSTGRES_HOST=postgres \
    -e POSTGRES_DB=pikadb \
    -e POSTGRES_USER=pika_user \
    -e POSTGRES_PASSWORD=pika_pass \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/services/data_processor:/app \
    pika_data_processor:latest python scripts/upload_to_minio.py
    echo "✅ Upload completed"
    ''',
    dag=dag,
)

# Task 2: Extract DOCX content
extract_docx = BashOperator(
    task_id='extract_docx_content',
    bash_command='''
    echo "📄 Step 2: Extract DOCX content and images..."
    docker run --rm --network pikahelper_pika_network \
    -e MINIO_ENDPOINT=minio:9000 \
    -e MINIO_ACCESS_KEY=admin \
    -e MINIO_SECRET_KEY=password123 \
    -e POSTGRES_HOST=postgres \
    -e POSTGRES_DB=pikadb \
    -e POSTGRES_USER=pika_user \
    -e POSTGRES_PASSWORD=pika_pass \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/services/data_processor:/app \
    pika_data_processor:latest python scripts/extract_docx.py
    echo "✅ DOCX extraction completed"
    ''',
    dag=dag,
)

# Task 3: Process Q&A data
process_qa = BashOperator(
    task_id='process_qa_data',
    bash_command='''
    echo "❓ Step 3: Process Q&A JSON data..."
    docker run --rm --network pikahelper_pika_network \
    -e MINIO_ENDPOINT=minio:9000 \
    -e MINIO_ACCESS_KEY=admin \
    -e MINIO_SECRET_KEY=password123 \
    -e POSTGRES_HOST=postgres \
    -e POSTGRES_DB=pikadb \
    -e POSTGRES_USER=pika_user \
    -e POSTGRES_PASSWORD=pika_pass \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/services/data_processor:/app \
    pika_data_processor:latest python scripts/process_qa_json.py
    echo "✅ Q&A processing completed"
    ''',
    dag=dag,
)

# Task 4: Generate embeddings
generate_embeddings = BashOperator(
    task_id='generate_embeddings',
    bash_command='''
    echo "🧠 Step 4: Generate embeddings..."
    docker run --rm --network pikahelper_pika_network \
    -e QDRANT_HOST=qdrant \
    -e QDRANT_PORT=6333 \
    -e POSTGRES_HOST=postgres \
    -e POSTGRES_DB=pikadb \
    -e POSTGRES_USER=pika_user \
    -e POSTGRES_PASSWORD=pika_pass \
    -v $(pwd)/models:/app/models \
    -v $(pwd)/cache:/root/.cache \
    -v $(pwd)/services/embedding_service:/app \
    pika_embedding_service:latest python scripts/generate_embeddings.py
    echo "✅ Embeddings generated"
    ''',
    dag=dag,
)

# Task 5: Test RAG system
test_rag = BashOperator(
    task_id='test_rag_system',
    bash_command='''
    echo "🤖 Step 5: Test RAG system..."
    docker run --rm --network pikahelper_pika_network \
    -e QDRANT_HOST=qdrant \
    -e QDRANT_PORT=6333 \
    -e GEMINI_API_KEY=${GEMINI_API_KEY} \
    -v $(pwd)/models:/app/models \
    -v $(pwd)/cache:/root/.cache \
    -v $(pwd)/services/embedding_service:/app \
    -v $(pwd)/services/rag_engine/scripts:/app/rag_scripts \
    pika_embedding_service:latest python rag_scripts/rag_query.py "Làm thế nào để tải game PokeMMO?"
    echo "✅ RAG test completed"
    ''',
    dag=dag,
)

# Task 6: Pipeline complete
pipeline_complete = BashOperator(
    task_id='pipeline_complete',
    bash_command='''
    echo "🎉 PikaHelper Pipeline Completed Successfully!"
    echo "📅 Time: $(date)"
    echo "📊 All data processed and ready for use"
    echo "🚀 RAG system is ready!"
    ''',
    dag=dag,
)

# Define task dependencies - Sequential execution
upload_data >> extract_docx >> process_qa >> generate_embeddings >> test_rag >> pipeline_complete
