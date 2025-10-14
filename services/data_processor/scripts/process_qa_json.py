#!/usr/bin/env python3
"""
Process Q&A JSON files from MinIO and store in PostgreSQL
Reads Q&A JSON from MinIO qa-data bucket and processes into PostgreSQL
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from minio import Minio
from minio.error import S3Error
import psycopg2
from psycopg2.extras import Json, RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QAProcessor:
    """Process Q&A JSON files and store in PostgreSQL"""
    
    def __init__(self):
        # MinIO configuration
        self.minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        self.minio_access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
        self.minio_secret_key = os.getenv("MINIO_SECRET_KEY", "password123")
        
        # PostgreSQL configuration
        self.postgres_host = os.getenv("POSTGRES_HOST", "postgres")
        self.postgres_db = os.getenv("POSTGRES_DB", "pikadb")
        self.postgres_user = os.getenv("POSTGRES_USER", "pika_user")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "pika_pass")
        
        # Initialize clients
        self.minio_client = Minio(
            self.minio_endpoint,
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=False
        )
        
        # Ensure database tables exist
        self.ensure_tables()
    
    def ensure_tables(self):
        """Create Q&A tables if they don't exist"""
        try:
            conn = psycopg2.connect(
                host=self.postgres_host,
                database=self.postgres_db,
                user=self.postgres_user,
                password=self.postgres_password
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Create qa_pairs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS qa_pairs (
                    id SERIAL PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    source_file VARCHAR(255),
                    source_document VARCHAR(255),
                    category VARCHAR(100),
                    difficulty_level VARCHAR(50),
                    tags TEXT[],
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create qa_metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS qa_metadata (
                    id SERIAL PRIMARY KEY,
                    source_file VARCHAR(255) UNIQUE,
                    total_pairs INTEGER,
                    categories JSONB,
                    difficulty_distribution JSONB,
                    processing_status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_qa_pairs_question 
                ON qa_pairs USING gin(to_tsvector('english', question))
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_qa_pairs_category 
                ON qa_pairs(category)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_qa_pairs_source 
                ON qa_pairs(source_file)
            """)
            
            cursor.close()
            conn.close()
            
            logger.info("✅ Q&A tables created/verified successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            raise
    
    def download_qa_json(self, object_name: str) -> Optional[Dict]:
        """Download Q&A JSON from MinIO"""
        try:
            logger.info(f"📥 Downloading Q&A JSON: {object_name}")
            
            # Download object
            response = self.minio_client.get_object("qa-data", object_name)
            json_data = json.loads(response.read().decode('utf-8'))
            
            logger.info(f"✅ Downloaded Q&A JSON: {len(json_data.get('qa_pairs', []))} pairs")
            return json_data
            
        except S3Error as e:
            logger.error(f"❌ Failed to download {object_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error downloading {object_name}: {e}")
            return None
    
    def process_qa_pairs(self, qa_data: Dict, source_file: str) -> int:
        """Process Q&A pairs and store in PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=self.postgres_host,
                database=self.postgres_db,
                user=self.postgres_user,
                password=self.postgres_password
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            qa_pairs = qa_data.get('qa_pairs', [])
            if not qa_pairs:
                logger.warning("⚠️ No Q&A pairs found in JSON data")
                return 0
            
            logger.info(f"📊 Processing {len(qa_pairs)} Q&A pairs...")
            
            inserted_count = 0
            categories = set()
            difficulty_levels = set()
            
            for i, pair in enumerate(qa_pairs, 1):
                try:
                    question = pair.get('question', '').strip()
                    answer = pair.get('answer', '').strip()
                    
                    if not question or not answer:
                        logger.warning(f"⚠️ Skipping invalid pair {i}: empty question or answer")
                        continue
                    
                    # Extract metadata
                    category = pair.get('category', 'general')
                    difficulty = pair.get('difficulty', 'medium')
                    tags = pair.get('tags', [])
                    source_doc = pair.get('source_document', '')
                    
                    # Store categories and difficulty for metadata
                    categories.add(category)
                    difficulty_levels.add(difficulty)
                    
                    # Insert Q&A pair
                    cursor.execute("""
                        INSERT INTO qa_pairs (
                            question, answer, source_file, source_document,
                            category, difficulty_level, tags, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        question, answer, source_file, source_doc,
                        category, difficulty, tags, Json(pair)
                    ))
                    
                    inserted_count += 1
                    
                    if i % 10 == 0:
                        logger.info(f"📝 Processed {i}/{len(qa_pairs)} pairs...")
                
                except Exception as e:
                    logger.error(f"❌ Error processing pair {i}: {e}")
                    continue
            
            # Update metadata
            self.update_qa_metadata(
                cursor, source_file, len(qa_pairs), 
                list(categories), difficulty_levels
            )
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Successfully processed {inserted_count} Q&A pairs")
            return inserted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to process Q&A pairs: {e}")
            return 0
    
    def update_qa_metadata(self, cursor, source_file: str, total_pairs: int, 
                         categories: List[str], difficulty_levels: set):
        """Update Q&A metadata table"""
        try:
            # Count difficulty distribution
            difficulty_dist = {}
            for level in difficulty_levels:
                cursor.execute("""
                    SELECT COUNT(*) FROM qa_pairs 
                    WHERE source_file = %s AND difficulty_level = %s
                """, (source_file, level))
                difficulty_dist[level] = cursor.fetchone()[0]
            
            # Insert or update metadata
            cursor.execute("""
                INSERT INTO qa_metadata (
                    source_file, total_pairs, categories, 
                    difficulty_distribution, processing_status
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (source_file) 
                DO UPDATE SET
                    total_pairs = EXCLUDED.total_pairs,
                    categories = EXCLUDED.categories,
                    difficulty_distribution = EXCLUDED.difficulty_distribution,
                    processing_status = 'completed',
                    updated_at = CURRENT_TIMESTAMP
            """, (
                source_file, total_pairs, Json(categories),
                Json(difficulty_dist), 'completed'
            ))
            
            logger.info(f"📊 Updated metadata for {source_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update metadata: {e}")
    
    def list_qa_files(self) -> List[str]:
        """List all Q&A JSON files in MinIO"""
        try:
            objects = self.minio_client.list_objects("qa-data", recursive=True)
            qa_files = [obj.object_name for obj in objects if obj.object_name.endswith('.json')]
            
            logger.info(f"📋 Found {len(qa_files)} Q&A JSON files")
            return qa_files
            
        except Exception as e:
            logger.error(f"❌ Failed to list Q&A files: {e}")
            return []
    
    def process_all_qa_files(self) -> int:
        """Process all Q&A JSON files from MinIO"""
        logger.info("🚀 Starting Q&A processing...")
        
        # List all Q&A files
        qa_files = self.list_qa_files()
        if not qa_files:
            logger.warning("⚠️ No Q&A JSON files found in MinIO")
            return 0
        
        total_processed = 0
        
        for qa_file in qa_files:
            logger.info(f"📄 Processing: {qa_file}")
            
            # Download JSON data
            qa_data = self.download_qa_json(qa_file)
            if not qa_data:
                logger.error(f"❌ Failed to download {qa_file}")
                continue
            
            # Process Q&A pairs
            processed_count = self.process_qa_pairs(qa_data, qa_file)
            total_processed += processed_count
            
            logger.info(f"✅ Completed {qa_file}: {processed_count} pairs processed")
        
        logger.info(f"🎉 Q&A processing completed! Total: {total_processed} pairs processed")
        return total_processed

def main():
    """Main function to process Q&A JSON files"""
    logger.info("🤖 Q&A JSON Processor")
    logger.info("=" * 50)
    
    try:
        processor = QAProcessor()
        total_processed = processor.process_all_qa_files()
        
        if total_processed > 0:
            logger.info(f"✅ Successfully processed {total_processed} Q&A pairs")
        else:
            logger.warning("⚠️ No Q&A pairs were processed")
            
    except Exception as e:
        logger.error(f"❌ Q&A processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
