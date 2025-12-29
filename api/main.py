#!/usr/bin/env python3
"""
Simple RAG API for PikaHelper
Provides REST API endpoints for querying the RAG system
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add scripts to path
sys.path.append('/app/scripts')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    max_results: int = 5

class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[Dict[str, Any]]
    images: List[str]
    links: List[str]
    metadata: Dict[str, Any]
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    timestamp: str

class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_embeddings: int
    timestamp: str

# FastAPI app
app = FastAPI(
    title="PikaHelper RAG API",
    description="Simple RAG API for PokeMMO guidance",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG engine
rag_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG engine on startup"""
    global rag_engine
    try:
        logger.info("🚀 Initializing RAG engine...")
        from rag_query import RAGQueryEngine
        rag_engine = RAGQueryEngine()
        logger.info("✅ RAG engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG engine: {e}")
        rag_engine = None

@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system
    
    Args:
        query: User question in Vietnamese
        max_results: Maximum number of results to return
    
    Returns:
        Response with answer, sources, images, and links
    """
    try:
        if rag_engine is None:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")
        
        logger.info(f"🔍 Processing query: {request.query}")
        
        # Query RAG engine
        result = rag_engine.query(request.query, max_docs=request.max_results, max_qa=request.max_results)
        
        # Extract images and links from sources
        all_images = []
        all_links = []
        
        for doc in result['context']['documents']:
            if 'metadata' in doc and doc['metadata']:
                metadata = doc['metadata']
                if 'images' in metadata and metadata['images']:
                    all_images.extend(metadata['images'])
                if 'urls' in metadata and metadata['urls']:
                    all_links.extend(metadata['urls'])
        
        # Format sources
        sources = []
        for doc in result['context']['documents']:
            sources.append({
                "file_name": doc['file_name'],
                "content": doc['content'],
                "score": doc['score'],
                "type": "document"
            })
        
        for qa in result['context']['qa_pairs']:
            sources.append({
                "question": qa['question'],
                "answer": qa['answer'],
                "score": qa['score'],
                "type": "qa"
            })
        
        return QueryResponse(
            query=request.query,
            response=result['response'],
            sources=sources,
            images=list(set(all_images)),
            links=list(set(all_links)),
            metadata=result['metadata'],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        services={
            "api": "running",
            "rag_engine": "initialized" if rag_engine else "not_initialized"
        },
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/stats", response_model=StatsResponse)
async def stats():
    """Get system statistics"""
    try:
        import psycopg2

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            database=os.getenv("POSTGRES_DB", "pikadb"),
            user=os.getenv("POSTGRES_USER", "pika_user"),
            password=os.getenv("POSTGRES_PASSWORD", "pika_pass")
        )
        cursor = conn.cursor()

        # Get counts
        cursor.execute("SELECT COUNT(*) FROM documents")
        total_documents = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chunks")
        total_chunks = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM embeddings")
        total_embeddings = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return StatsResponse(
            total_documents=total_documents,
            total_chunks=total_chunks,
            total_embeddings=total_embeddings,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

