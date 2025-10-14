#!/usr/bin/env python3
"""
Chatbot API Service for PikaHelper RAG System
Handles chat interactions with Gemini API and vector search
"""

import os
import sys
import logging
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="PikaHelper Chatbot API",
    description="RAG-based chatbot for PokeMMO game guidance",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[Dict[str, Any]]
    timestamp: str

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_found: int

class ChatbotService:
    def __init__(self):
        self.embedding_service_url = os.getenv("EMBEDDING_SERVICE_URL", "http://embedding-service:8001")
        
    def generate_response(self, query: str, context: List[Dict[str, Any]] = None) -> str:
        """Generate response using simple template (no Gemini for now)"""
        try:
            # Simple response template
            if context:
                context_text = "\n".join([doc.get("content", "") for doc in context])
                response = f"""Dựa trên thông tin có sẵn:

{context_text}

Câu trả lời cho câu hỏi "{query}": Đây là một câu hỏi về PokeMMO. Tôi đang trong quá trình phát triển và sẽ có thể trả lời chi tiết hơn sau khi hệ thống được hoàn thiện."""
            else:
                response = f"""Xin chào! Tôi là trợ lý AI cho game PokeMMO. 

Câu hỏi của bạn: "{query}"

Hiện tại tôi đang trong quá trình phát triển. Hệ thống sẽ sớm có thể:
- Hướng dẫn tải và cài đặt game
- Hướng dẫn hoàn thành cốt truyện  
- Tư vấn về PvP và xây dựng đội hình
- Hướng dẫn kiếm tiền trong game

Hãy thử lại sau nhé!"""
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau."

# Initialize services
chatbot_service = ChatbotService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Chatbot API service started - ready for development")

async def search_similar_chunks(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search for similar chunks using vector similarity"""
    # Mock data for development
    mock_results = [
        {
            "content": f"Mock content for query: {query}",
            "file_name": "mock_file.docx",
            "file_path": "/data/raw/mock_file.docx",
            "metadata": {"source": "development"},
            "score": 0.85
        }
    ]
    
    return mock_results[:limit]

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """Main chat endpoint"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Search for relevant context
        context = await search_similar_chunks(request.message, limit=5)
        
        # Generate response
        response_text = chatbot_service.generate_response(
            request.message, 
            context
        )
        
        # Format sources
        sources = []
        for i, doc in enumerate(context, 1):
            sources.append({
                "source_id": i,
                "file_name": doc.get("file_name", ""),
                "file_path": doc.get("file_path", ""),
                "score": doc.get("score", 0.0),
                "preview": doc.get("content", "")[:200] + "..." if len(doc.get("content", "")) > 200 else doc.get("content", "")
            })
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            sources=sources,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search documents endpoint"""
    try:
        results = await search_similar_chunks(request.query, request.limit)
        
        return SearchResponse(
            results=results,
            query=request.query,
            total_found=len(results)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "chatbot-api",
        "version": "1.0.0"
    }

@app.get("/stats")
async def get_stats():
    """Get chatbot statistics"""
    try:
        return {
            "active_sessions": 0,
            "total_chunks": 0,
            "total_embeddings": 0,
            "service_status": "running"
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
