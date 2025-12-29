#!/usr/bin/env python3
"""
Test vector search in Qdrant
"""

import os
import sys
import logging
from typing import List, Dict, Any
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from pyvi import ViTokenizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QdrantTester:
    """Test vector search in Qdrant"""
    
    def __init__(self):
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
            return text
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for Vietnamese text"""
        try:
            tokenized_text = self.tokenize_text(text)
            embedding = self.model.encode([tokenized_text])
            return embedding[0].tolist()
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            return None
    
    def test_collections(self):
        """Test Qdrant collections"""
        logger.info("🔍 Testing Qdrant collections...")
        
        try:
            collections = self.qdrant_client.get_collections()
            logger.info(f"📊 Found {len(collections.collections)} collections:")
            
            for collection in collections.collections:
                info = self.qdrant_client.get_collection(collection.name)
                logger.info(f"  📁 {collection.name}: {info.points_count} points")
                
        except Exception as e:
            logger.error(f"❌ Failed to get collections: {e}")
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search in documents collection"""
        logger.info(f"🔍 Searching documents for: '{query}'")
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if query_embedding is None:
                return []
            
            # Search in documents collection
            results = self.qdrant_client.search(
                collection_name="documents_collection",
                query_vector=query_embedding,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            logger.info(f"📊 Found {len(results)} document results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to search documents: {e}")
            return []
    
    def search_qa_pairs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search in Q&A collection"""
        logger.info(f"🔍 Searching Q&A pairs for: '{query}'")
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if query_embedding is None:
                return []
            
            # Search in Q&A collection
            results = self.qdrant_client.search(
                collection_name="qa_collection",
                query_vector=query_embedding,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            logger.info(f"📊 Found {len(results)} Q&A results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to search Q&A pairs: {e}")
            return []
    
    def test_semantic_search(self):
        """Test semantic search with various queries"""
        logger.info("🧪 Testing semantic search...")
        
        # Test queries
        test_queries = [
            "Làm thế nào để tải game PokeMMO?",
            "Cách kiếm tiền trong PokeMMO",
            "Hướng dẫn PvP Pokemon",
            "Elite 4 rematch",
            "Pokemon huyền thoại",
            "Breeding Pokemon",
            "Christmas event",
            "Halloween sự kiện"
        ]
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"🔍 Test {i}: {query}")
            logger.info(f"{'='*60}")
            
            # Search documents
            doc_results = self.search_documents(query, limit=3)
            if doc_results:
                logger.info("📄 Top document results:")
                for j, result in enumerate(doc_results, 1):
                    score = result.score
                    payload = result.payload
                    content = payload.get('content', '')[:100] + "..."
                    file_name = payload.get('file_name', 'Unknown')
                    logger.info(f"  {j}. Score: {score:.4f} | File: {file_name}")
                    logger.info(f"     Content: {content}")
            
            # Search Q&A
            qa_results = self.search_qa_pairs(query, limit=3)
            if qa_results:
                logger.info("❓ Top Q&A results:")
                for j, result in enumerate(qa_results, 1):
                    score = result.score
                    payload = result.payload
                    question = payload.get('question', '')
                    answer = payload.get('answer', '')[:100] + "..."
                    logger.info(f"  {j}. Score: {score:.4f} | Q: {question}")
                    logger.info(f"     A: {answer}")
    
    def test_filtered_search(self):
        """Test filtered search"""
        logger.info("🔍 Testing filtered search...")
        
        try:
            # Search with filter for specific file
            query = "PokeMMO game"
            query_embedding = self.generate_embedding(query)
            
            # Filter by source
            results = self.qdrant_client.search(
                collection_name="documents_collection",
                query_vector=query_embedding,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="source",
                            match=MatchValue(value="document_chunk")
                        )
                    ]
                ),
                limit=3,
                with_payload=True
            )
            
            logger.info(f"📊 Filtered search results: {len(results)}")
            for result in results:
                payload = result.payload
                logger.info(f"  File: {payload.get('file_name', 'Unknown')}")
                logger.info(f"  Score: {result.score:.4f}")
                
        except Exception as e:
            logger.error(f"❌ Filtered search failed: {e}")
    
    def test_similarity_threshold(self):
        """Test similarity threshold"""
        logger.info("🎯 Testing similarity threshold...")
        
        query = "PokeMMO download"
        query_embedding = self.generate_embedding(query)
        
        # Test different similarity thresholds
        thresholds = [0.7, 0.6, 0.5, 0.4]
        
        for threshold in thresholds:
            results = self.qdrant_client.search(
                collection_name="documents_collection",
                query_vector=query_embedding,
                limit=10,
                score_threshold=threshold,
                with_payload=True
            )
            
            logger.info(f"📊 Threshold {threshold}: {len(results)} results")
            if results:
                logger.info(f"  Best score: {results[0].score:.4f}")
                logger.info(f"  Worst score: {results[-1].score:.4f}")
    
    def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Qdrant Vector Search Tests")
        logger.info("=" * 60)
        
        # Test collections
        self.test_collections()
        
        # Test semantic search
        self.test_semantic_search()
        
        # Test filtered search
        self.test_filtered_search()
        
        # Test similarity threshold
        self.test_similarity_threshold()
        
        logger.info("\n🎉 All tests completed!")

def main():
    """Main function"""
    logger.info("🤖 Qdrant Vector Search Tester")
    logger.info("=" * 60)
    
    try:
        tester = QdrantTester()
        tester.run_all_tests()
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
