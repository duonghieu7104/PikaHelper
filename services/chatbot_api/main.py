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

# No direct RAG import - use embedding-service instead

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
        
    async def call_rag_service(self, query: str) -> Dict[str, Any]:
        """Call embedding-service RAG endpoint"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.embedding_service_url}/rag/query",
                    json={"query": query},
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to call RAG service: {e}")
            return None
        
    async def generate_response(self, query: str, context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response using embedding-service RAG"""
        try:
            logger.info(f"🔍 Calling RAG service for query: {query}")
            
            # Call embedding-service RAG endpoint
            rag_result = await self.call_rag_service(query)
            
            if rag_result is None:
                # Fallback response
                return {
                    "response": f"""Xin chào! Tôi là trợ lý AI cho game PokeMMO. 

Câu hỏi của bạn: "{query}"

Hiện tại hệ thống RAG đang được khởi tạo. Vui lòng thử lại sau vài giây.""",
                    "sources": [],
                    "metadata": {"status": "rag_service_unavailable"}
                }
            
            return rag_result
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return {
                "response": "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
                "sources": [],
                "metadata": {"error": str(e)}
            }

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
    """Main chat endpoint with RAG integration"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Generate response using RAG engine
        rag_result = await chatbot_service.generate_response(request.message)
        
        return ChatResponse(
            response=rag_result["response"],
            session_id=session_id,
            sources=rag_result["sources"],
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
