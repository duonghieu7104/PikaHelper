#!/usr/bin/env python3
"""
Generate embeddings from PostgreSQL and store in Qdrant
Based on test_model.py - uses Vietnamese embedding model
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

import psycopg2
from psycopg2.extras import RealDictCursor
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from pyvi import ViTokenizer
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate embeddings from PostgreSQL and store in Qdrant"""
    
    def __init__(self):
        # PostgreSQL configuration
        self.postgres_host = os.getenv("POSTGRES_HOST", "postgres")
        self.postgres_db = os.getenv("POSTGRES_DB", "pikadb")
        self.postgres_user = os.getenv("POSTGRES_USER", "pika_user")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "pika_pass")
        
        # Qdrant configuration
        self.qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        
        # Initialize clients
        self.qdrant_client = QdrantClient(
            host=self.qdrant_host,
            port=self.qdrant_port
        )
        
        # Load Vietnamese embedding model
        logger.info("🇻🇳 Loading Vietnamese embedding model...")
        self.model = SentenceTransformer("huyydangg/DEk21_hcmute_embedding")
        logger.info("✅ Vietnamese embedding model loaded successfully")
    
    def tokenize_text(self, text: str) -> str:
        """Tokenize Vietnamese text using pyvi"""
        try:
            return ViTokenizer.tokenize(text)
        except Exception as e:
            logger.warning(f"⚠️ Tokenization failed for text: {text[:50]}... Error: {e}")
            return text  # Return original text if tokenization fails
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for Vietnamese text"""
        try:
            # Tokenize Vietnamese text
            tokenized_text = self.tokenize_text(text)
            
            # Generate embedding
            embedding = self.model.encode([tokenized_text])
            
            # Convert to list of floats
            return embedding[0].tolist()
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding for text: {text[:50]}... Error: {e}")
            return None
    
    def read_document_chunks(self) -> List[Dict[str, Any]]:
        """Read document chunks from PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=self.postgres_host,
                database=self.postgres_db,
                user=self.postgres_user,
                password=self.postgres_password
            )
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    c.id as chunk_id,
                    c.content,
                    c.metadata,
                    d.id as doc_id,
                    d.file_name,
                    d.file_path
                FROM chunks c
                JOIN documents d ON c.doc_id = d.id
                WHERE c.content IS NOT NULL 
                AND LENGTH(TRIM(c.content)) > 0
                ORDER BY c.id
            """)
            
            chunks = cursor.fetchall()
            cursor.close()
            conn.close()
            
            logger.info(f"📊 Found {len(chunks)} document chunks to process")
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Failed to read document chunks: {e}")
            return []
    
    def read_qa_pairs(self) -> List[Dict[str, Any]]:
        """Read Q&A pairs from PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=self.postgres_host,
                database=self.postgres_db,
                user=self.postgres_user,
                password=self.postgres_password
            )
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    id as qa_id,
                    question,
                    answer,
                    category,
                    difficulty_level,
                    tags,
                    source_file,
                    metadata
                FROM qa_pairs
                WHERE question IS NOT NULL 
                AND answer IS NOT NULL
                AND LENGTH(TRIM(question)) > 0
                AND LENGTH(TRIM(answer)) > 0
                ORDER BY id
            """)
            
            qa_pairs = cursor.fetchall()
            cursor.close()
            conn.close()
            
            logger.info(f"📊 Found {len(qa_pairs)} Q&A pairs to process")
            return qa_pairs
            
        except Exception as e:
            logger.error(f"❌ Failed to read Q&A pairs: {e}")
            return []
    
    def create_collections(self):
        """Create Qdrant collections if they don't exist"""
        try:
            # Create documents collection
            try:
                self.qdrant_client.recreate_collection(
                    collection_name="documents_collection",
                    vectors_config=VectorParams(
                        size=768,  # Vietnamese model dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info("✅ Created documents_collection")
            except Exception as e:
                logger.info(f"ℹ️ documents_collection already exists: {e}")
            
            # Create Q&A collection
            try:
                self.qdrant_client.recreate_collection(
                    collection_name="qa_collection",
                    vectors_config=VectorParams(
                        size=768,  # Vietnamese model dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info("✅ Created qa_collection")
            except Exception as e:
                logger.info(f"ℹ️ qa_collection already exists: {e}")
                
        except Exception as e:
            logger.error(f"❌ Failed to create collections: {e}")
            raise
    
    def process_document_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Process document chunks and store in Qdrant"""
        logger.info("📄 Processing document chunks...")
        
        processed_count = 0
        batch_size = 10  # Process in batches
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            points = []
            
            for chunk in batch:
                try:
                    # Generate embedding for chunk content
                    embedding = self.generate_embedding(chunk['content'])
                    if embedding is None:
                        logger.warning(f"⚠️ Skipping chunk {chunk['chunk_id']} - embedding failed")
                        continue
                    
                    # Create point for Qdrant
                    point = PointStruct(
                        id=chunk['chunk_id'],
                        vector=embedding,
                        payload={
                            "chunk_id": chunk['chunk_id'],
                            "doc_id": chunk['doc_id'],
                            "content": chunk['content'][:1000],  # Truncate for storage
                            "file_name": chunk['file_name'],
                            "file_path": chunk['file_path'],
                            "metadata": chunk['metadata'],
                            "source": "document_chunk",
                            "created_at": datetime.now().isoformat()
                        }
                    )
                    points.append(point)
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error processing chunk {chunk['chunk_id']}: {e}")
                    continue
            
            # Upload batch to Qdrant
            if points:
                try:
                    self.qdrant_client.upsert(
                        collection_name="documents_collection",
                        points=points
                    )
                    logger.info(f"📤 Uploaded batch {i//batch_size + 1}: {len(points)} chunks")
                except Exception as e:
                    logger.error(f"❌ Failed to upload batch: {e}")
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.1)
        
        logger.info(f"✅ Processed {processed_count} document chunks")
        return processed_count
    
    def process_qa_pairs(self, qa_pairs: List[Dict[str, Any]]) -> int:
        """Process Q&A pairs and store in Qdrant"""
        logger.info("❓ Processing Q&A pairs...")
        
        processed_count = 0
        batch_size = 10  # Process in batches
        
        for i in range(0, len(qa_pairs), batch_size):
            batch = qa_pairs[i:i + batch_size]
            points = []
            
            for qa in batch:
                try:
                    # Generate embedding for question (primary search target)
                    embedding = self.generate_embedding(qa['question'])
                    if embedding is None:
                        logger.warning(f"⚠️ Skipping Q&A {qa['qa_id']} - embedding failed")
                        continue
                    
                    # Create point for Qdrant
                    point = PointStruct(
                        id=qa['qa_id'],
                        vector=embedding,
                        payload={
                            "qa_id": qa['qa_id'],
                            "question": qa['question'],
                            "answer": qa['answer'],
                            "category": qa['category'],
                            "difficulty_level": qa['difficulty_level'],
                            "tags": qa['tags'],
                            "source_file": qa['source_file'],
                            "metadata": qa['metadata'],
                            "source": "qa_pair",
                            "created_at": datetime.now().isoformat()
                        }
                    )
                    points.append(point)
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error processing Q&A {qa['qa_id']}: {e}")
                    continue
            
            # Upload batch to Qdrant
            if points:
                try:
                    self.qdrant_client.upsert(
                        collection_name="qa_collection",
                        points=points
                    )
                    logger.info(f"📤 Uploaded batch {i//batch_size + 1}: {len(points)} Q&A pairs")
                except Exception as e:
                    logger.error(f"❌ Failed to upload batch: {e}")
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.1)
        
        logger.info(f"✅ Processed {processed_count} Q&A pairs")
        return processed_count
    
    def test_embeddings(self):
        """Test embedding generation with sample data"""
        logger.info("🧪 Testing embedding generation...")
        
        # Test with sample Vietnamese text
        test_texts = [
            "Làm thế nào để tải game PokeMMO trên điện thoại?",
            "Hướng dẫn hoàn thành cốt truyện Pokemon Fire Red",
            "Cách kiếm tiền hiệu quả trong PokeMMO"
        ]
        
        for i, text in enumerate(test_texts, 1):
            logger.info(f"🔧 Test {i}: {text}")
            
            # Tokenize
            tokenized = self.tokenize_text(text)
            logger.info(f"   Tokenized: {tokenized}")
            
            # Generate embedding
            embedding = self.generate_embedding(text)
            if embedding:
                logger.info(f"   ✅ Embedding generated: {len(embedding)} dimensions")
                logger.info(f"   📊 First 5 values: {embedding[:5]}")
            else:
                logger.error(f"   ❌ Embedding generation failed")
        
        logger.info("🧪 Embedding test completed")
    
    def generate_all_embeddings(self) -> Dict[str, int]:
        """Generate all embeddings and store in Qdrant"""
        logger.info("🚀 Starting embedding generation...")
        
        # Test embeddings first
        self.test_embeddings()
        
        # Create collections
        self.create_collections()
        
        # Process document chunks
        chunks = self.read_document_chunks()
        doc_processed = self.process_document_chunks(chunks)
        
        # Process Q&A pairs
        qa_pairs = self.read_qa_pairs()
        qa_processed = self.process_qa_pairs(qa_pairs)
        
        # Summary
        total_processed = doc_processed + qa_processed
        
        logger.info("🎉 Embedding generation completed!")
        logger.info(f"📊 Summary:")
        logger.info(f"   Document chunks processed: {doc_processed}")
        logger.info(f"   Q&A pairs processed: {qa_processed}")
        logger.info(f"   Total embeddings: {total_processed}")
        
        return {
            "document_chunks": doc_processed,
            "qa_pairs": qa_processed,
            "total": total_processed
        }

def main():
    """Main function to generate embeddings"""
    logger.info("🤖 Vietnamese Embedding Generator")
    logger.info("=" * 60)
    
    try:
        generator = EmbeddingGenerator()
        results = generator.generate_all_embeddings()
        
        if results["total"] > 0:
            logger.info(f"✅ Successfully generated {results['total']} embeddings")
        else:
            logger.warning("⚠️ No embeddings were generated")
            
    except Exception as e:
        logger.error(f"❌ Embedding generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
