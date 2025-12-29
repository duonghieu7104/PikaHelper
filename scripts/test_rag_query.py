#!/usr/bin/env python3
"""
RAG Query System - User Query → Vector Search → LLM Generation
"""

import os
import sys
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

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

class RAGQuerySystem:
    """RAG Query System for Vietnamese PokeMMO knowledge base"""
    
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
    
    def search_documents(self, query: str, limit: int = 5, score_threshold: float = 0.3) -> List[Dict[str, Any]]:
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
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            logger.info(f"📊 Found {len(results)} document results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to search documents: {e}")
            return []
    
    def search_qa_pairs(self, query: str, limit: int = 5, score_threshold: float = 0.3) -> List[Dict[str, Any]]:
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
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            logger.info(f"📊 Found {len(results)} Q&A results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to search Q&A pairs: {e}")
            return []
    
    def format_context(self, doc_results: List[Dict[str, Any]], qa_results: List[Dict[str, Any]]) -> str:
        """Format search results into context for LLM"""
        context_parts = []
        
        # Add document context
        if doc_results:
            context_parts.append("📄 **Tài liệu liên quan:**")
            for i, result in enumerate(doc_results, 1):
                payload = result.payload
                content = payload.get('content', '')
                file_name = payload.get('file_name', 'Unknown')
                score = result.score
                
                context_parts.append(f"{i}. **{file_name}** (Độ liên quan: {score:.2f})")
                context_parts.append(f"   {content[:500]}...")
                context_parts.append("")
        
        # Add Q&A context
        if qa_results:
            context_parts.append("❓ **Câu hỏi và trả lời liên quan:**")
            for i, result in enumerate(qa_results, 1):
                payload = result.payload
                question = payload.get('question', '')
                answer = payload.get('answer', '')
                score = result.score
                
                context_parts.append(f"{i}. **Q:** {question} (Độ liên quan: {score:.2f})")
                context_parts.append(f"   **A:** {answer[:300]}...")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate simple response without Gemini API"""
        logger.info("🤖 Generating simple response...")
        
        # Simple response based on context
        if context.strip():
            return f"Dựa trên thông tin tìm được, đây là câu trả lời cho câu hỏi: '{query}'\n\n{context}"
        else:
            return f"Không tìm thấy thông tin liên quan đến câu hỏi: '{query}'"
    
    def query(self, user_query: str, max_docs: int = 3, max_qa: int = 3, score_threshold: float = 0.3) -> Dict[str, Any]:
        """Main query function - RAG pipeline"""
        logger.info(f"🚀 Processing query: '{user_query}'")
        
        start_time = time.time()
        
        # Step 1: Vector search
        doc_results = self.search_documents(user_query, limit=max_docs, score_threshold=score_threshold)
        qa_results = self.search_qa_pairs(user_query, limit=max_qa, score_threshold=score_threshold)
        
        # Step 2: Format context
        context = self.format_context(doc_results, qa_results)
        
        # Step 3: Generate response
        response = self.generate_response(user_query, context)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare result
        result = {
            "query": user_query,
            "response": response,
            "context": {
                "documents": [
                    {
                        "file_name": r.payload.get('file_name', 'Unknown'),
                        "content": r.payload.get('content', '')[:200] + "...",
                        "score": r.score,
                        "source": "document"
                    }
                    for r in doc_results
                ],
                "qa_pairs": [
                    {
                        "question": r.payload.get('question', ''),
                        "answer": r.payload.get('answer', '')[:200] + "...",
                        "score": r.score,
                        "source": "qa"
                    }
                    for r in qa_results
                ]
            },
            "metadata": {
                "processing_time": round(processing_time, 2),
                "total_results": len(doc_results) + len(qa_results),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        logger.info(f"✅ Query processed in {processing_time:.2f}s")
        return result
    
    def interactive_query(self):
        """Interactive query mode"""
        logger.info("🤖 RAG Query System - Interactive Mode")
        logger.info("=" * 60)
        logger.info("Nhập câu hỏi của bạn (gõ 'quit' để thoát):")
        
        while True:
            try:
                user_input = input("\n❓ Câu hỏi: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    logger.info("👋 Tạm biệt!")
                    break
                
                if not user_input:
                    continue
                
                # Process query
                result = self.query(user_input)
                
                # Display response
                print(f"\n🤖 **Trả lời:**")
                print(result['response'])
                
                # Display context info
                print(f"\n📊 **Thông tin tham khảo:**")
                print(f"- Tài liệu: {len(result['context']['documents'])} kết quả")
                print(f"- Q&A: {len(result['context']['qa_pairs'])} kết quả")
                print(f"- Thời gian xử lý: {result['metadata']['processing_time']}s")
                
            except KeyboardInterrupt:
                logger.info("\n👋 Tạm biệt!")
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                print(f"❌ Lỗi: {e}")

def main():
    """Main function"""
    logger.info("🤖 RAG Query System for PokeMMO")
    logger.info("=" * 60)
    
    try:
        # Initialize RAG system
        rag_system = RAGQuerySystem()
        
        # Check if running in interactive mode
        if len(sys.argv) > 1:
            # Single query mode
            query = " ".join(sys.argv[1:])
            result = rag_system.query(query)
            
            print(f"🤖 **Trả lời:**")
            print(result['response'])
            
            print(f"\n📊 **Thông tin tham khảo:**")
            print(f"- Tài liệu: {len(result['context']['documents'])} kết quả")
            print(f"- Q&A: {len(result['context']['qa_pairs'])} kết quả")
            print(f"- Thời gian xử lý: {result['metadata']['processing_time']}s")
            
        else:
            # Interactive mode
            rag_system.interactive_query()
            
    except Exception as e:
        logger.error(f"❌ System failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
