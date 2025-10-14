#!/usr/bin/env python3
"""
RAG Query Engine - High Quality Results Only
Threshold: Documents > 0.6, Q&A > 0.7
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

class RAGQueryEngine:
    """High-quality RAG Query Engine with strict thresholds"""
    
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
    
    def search_documents(self, query: str, limit: int = 5, score_threshold: float = 0.6) -> List[Dict[str, Any]]:
        """Search in documents collection with high threshold"""
        logger.info(f"🔍 Searching documents for: '{query}' (threshold: {score_threshold})")
        
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
            
            logger.info(f"📊 Found {len(results)} document results (threshold: {score_threshold})")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to search documents: {e}")
            return []
    
    def search_qa_pairs(self, query: str, limit: int = 5, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search in Q&A collection with high threshold"""
        logger.info(f"🔍 Searching Q&A pairs for: '{query}' (threshold: {score_threshold})")
        
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
            
            logger.info(f"📊 Found {len(results)} Q&A results (threshold: {score_threshold})")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to search Q&A pairs: {e}")
            return []
    
    def format_high_quality_context(self, doc_results: List[Dict[str, Any]], qa_results: List[Dict[str, Any]]) -> str:
        """Format high-quality search results into context"""
        context_parts = []
        
        # Add document context (high quality only)
        if doc_results:
            context_parts.append("📄 **Tài liệu chất lượng cao:**")
            for i, result in enumerate(doc_results, 1):
                payload = result.payload
                content = payload.get('content', '')
                file_name = payload.get('file_name', 'Unknown')
                score = result.score
                
                context_parts.append(f"{i}. **{file_name}** (Độ liên quan: {score:.3f})")
                context_parts.append(f"   {content[:600]}...")
                context_parts.append("")
        
        # Add Q&A context (high quality only)
        if qa_results:
            context_parts.append("❓ **Câu hỏi và trả lời chất lượng cao:**")
            for i, result in enumerate(qa_results, 1):
                payload = result.payload
                question = payload.get('question', '')
                answer = payload.get('answer', '')
                score = result.score
                
                context_parts.append(f"{i}. **Q:** {question} (Độ liên quan: {score:.3f})")
                context_parts.append(f"   **A:** {answer[:400]}...")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def generate_high_quality_response(self, query: str, context: str) -> str:
        """Generate high-quality response based on filtered context"""
        logger.info("🤖 Generating high-quality response...")
        
        if context.strip():
            return f"**Câu trả lời chất lượng cao cho:** '{query}'\n\n{context}"
        else:
            return f"Không tìm thấy thông tin chất lượng cao cho câu hỏi: '{query}'\n\n💡 **Gợi ý:** Hãy thử diễn đạt câu hỏi khác hoặc sử dụng từ khóa cụ thể hơn."
    
    def query(self, user_query: str, max_docs: int = 3, max_qa: int = 3) -> Dict[str, Any]:
        """High-quality RAG query with strict thresholds"""
        logger.info(f"🚀 Processing high-quality query: '{user_query}'")
        
        start_time = time.time()
        
        # Step 1: High-threshold vector search
        doc_results = self.search_documents(user_query, limit=max_docs, score_threshold=0.6)
        qa_results = self.search_qa_pairs(user_query, limit=max_qa, score_threshold=0.7)
        
        # Step 2: Format high-quality context
        context = self.format_high_quality_context(doc_results, qa_results)
        
        # Step 3: Generate high-quality response
        response = self.generate_high_quality_response(user_query, context)
        
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
                        "content": r.payload.get('content', '')[:300] + "...",
                        "score": r.score,
                        "source": "document",
                        "quality": "high" if r.score >= 0.6 else "medium"
                    }
                    for r in doc_results
                ],
                "qa_pairs": [
                    {
                        "question": r.payload.get('question', ''),
                        "answer": r.payload.get('answer', '')[:300] + "...",
                        "score": r.score,
                        "source": "qa",
                        "quality": "high" if r.score >= 0.7 else "medium"
                    }
                    for r in qa_results
                ]
            },
            "metadata": {
                "processing_time": round(processing_time, 2),
                "total_results": len(doc_results) + len(qa_results),
                "high_quality_results": len([r for r in doc_results if r.score >= 0.6]) + len([r for r in qa_results if r.score >= 0.7]),
                "thresholds": {
                    "documents": 0.6,
                    "qa_pairs": 0.7
                },
                "timestamp": datetime.now().isoformat()
            }
        }
        
        logger.info(f"✅ High-quality query processed in {processing_time:.2f}s")
        logger.info(f"📊 Results: {len(doc_results)} docs + {len(qa_results)} Q&A = {len(doc_results) + len(qa_results)} total")
        return result
    
    def interactive_query(self):
        """Interactive high-quality query mode"""
        logger.info("🤖 High-Quality RAG Query Engine - Interactive Mode")
        logger.info("=" * 60)
        logger.info("🎯 Chế độ chất lượng cao:")
        logger.info("   📄 Documents: threshold > 0.6")
        logger.info("   ❓ Q&A: threshold > 0.7")
        logger.info("Nhập câu hỏi của bạn (gõ 'quit' để thoát):")
        
        while True:
            try:
                user_input = input("\n❓ Câu hỏi: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    logger.info("👋 Tạm biệt!")
                    break
                
                if not user_input:
                    continue
                
                # Process high-quality query
                result = self.query(user_input)
                
                # Display response
                print(f"\n🤖 **Trả lời chất lượng cao:**")
                print(result['response'])
                
                # Display quality info
                print(f"\n📊 **Thông tin chất lượng:**")
                print(f"- Tài liệu: {len(result['context']['documents'])} kết quả (threshold: 0.6)")
                print(f"- Q&A: {len(result['context']['qa_pairs'])} kết quả (threshold: 0.7)")
                print(f"- Kết quả chất lượng cao: {result['metadata']['high_quality_results']}")
                print(f"- Thời gian xử lý: {result['metadata']['processing_time']}s")
                
            except KeyboardInterrupt:
                logger.info("\n👋 Tạm biệt!")
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                print(f"❌ Lỗi: {e}")

def main():
    """Main function"""
    logger.info("🤖 High-Quality RAG Query Engine for PokeMMO")
    logger.info("=" * 60)
    
    try:
        # Initialize RAG engine
        rag_engine = RAGQueryEngine()
        
        # Check if running in interactive mode
        if len(sys.argv) > 1:
            # Single query mode
            query = " ".join(sys.argv[1:])
            result = rag_engine.query(query)
            
            print(f"🤖 **Trả lời chất lượng cao:**")
            print(result['response'])
            
            print(f"\n📊 **Thông tin chất lượng:**")
            print(f"- Tài liệu: {len(result['context']['documents'])} kết quả (threshold: 0.6)")
            print(f"- Q&A: {len(result['context']['qa_pairs'])} kết quả (threshold: 0.7)")
            print(f"- Kết quả chất lượng cao: {result['metadata']['high_quality_results']}")
            print(f"- Thời gian xử lý: {result['metadata']['processing_time']}s")
            
        else:
            # Interactive mode
            rag_engine.interactive_query()
            
    except Exception as e:
        logger.error(f"❌ System failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
