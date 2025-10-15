"""
PikaHelper Auto Pipeline DAG
Tự động hóa trình tự chạy các script có sẵn
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
    'pikahelper_auto_pipeline',
    default_args=default_args,
    description='PikaHelper Auto Pipeline - Tự động hóa trình tự script',
    schedule_interval=None,  # Chạy thủ công
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['pikahelper', 'auto', 'pipeline'],
)

# Task 1: Upload data to MinIO
upload_data = BashOperator(
    task_id='upload_data_to_minio',
    bash_command='''
    echo "📤 Step 1: Upload data to MinIO..."
    docker-compose run --rm data-processor python scripts/upload_to_minio.py
    echo "✅ Upload completed"
    ''',
    dag=dag,
)

# Task 2: Extract DOCX content
extract_docx = BashOperator(
    task_id='extract_docx_content',
    bash_command='''
    echo "📄 Step 2: Extract DOCX content and images..."
    docker-compose run --rm data-processor python scripts/extract_docx.py
    echo "✅ DOCX extraction completed"
    ''',
    dag=dag,
)

# Task 3: Process Q&A data
process_qa = BashOperator(
    task_id='process_qa_data',
    bash_command='''
    echo "❓ Step 3: Process Q&A JSON data..."
    docker-compose run --rm data-processor python scripts/process_qa_json.py
    echo "✅ Q&A processing completed"
    ''',
    dag=dag,
)

# Task 4: Generate embeddings
generate_embeddings = BashOperator(
    task_id='generate_embeddings',
    bash_command='''
    echo "🧠 Step 4: Generate embeddings..."
    docker-compose run --rm embedding-service python scripts/generate_embeddings.py
    echo "✅ Embeddings generated"
    ''',
    dag=dag,
)

# Task 5: Test RAG system
test_rag = BashOperator(
    task_id='test_rag_system',
    bash_command='''
    echo "🤖 Step 5: Test RAG system..."
    docker-compose exec embedding-service python rag_scripts/rag_query.py "Làm thế nào để tải game PokeMMO?"
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
