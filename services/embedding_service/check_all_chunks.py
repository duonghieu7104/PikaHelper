#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host='postgres',
    database='pikadb', 
    user='pika_user',
    password='pika_pass'
)
cursor = conn.cursor()

# Find all chunks with images
cursor.execute("""
SELECT doc_id, chunk_id, metadata 
FROM chunks 
WHERE metadata->>'has_images' = 'true' 
LIMIT 5
""")

results = cursor.fetchall()
print('All chunks with images:')
for row in results:
    doc_id, chunk_id, metadata = row
    file_name = metadata.get('file_name', 'Unknown')
    print(f'Doc {doc_id}, Chunk {chunk_id}: {file_name}')
    print(f'  has_images: {metadata.get("has_images", "N/A")}')
    print(f'  image_count: {metadata.get("image_count", "N/A")}')
    print()

cursor.close()
conn.close()
