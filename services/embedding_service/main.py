#!/usr/bin/env python3
"""
Embedding Service for PikaHelper RAG System
Handles Vietnamese text embedding using ONNX models
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import ONNX processor
from onnx_processor import ONNXEmbeddingProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmbeddingRequest(BaseModel):
    text: str
    chunk_id: Optional[str] = None

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    chunk_id: Optional[str] = None
    model_name: str
    
    model_config = {"protected_namespaces": ()}

class EmbeddingService:
    def __init__(self):
        self.processor = None
        self.model_name = "AITeamVN/Vietnamese_Embedding"
        self.embedding_dim = 1024
        self.model_path = "/app/models/embedding"
        
    def load_model(self):
        """Load Vietnamese ONNX model using ONNXEmbeddingProcessor"""
        try:
            logger.info(f"🔄 Loading ONNX model from: {self.model_path}")
            
            # Initialize ONNX processor
            self.processor = ONNXEmbeddingProcessor(self.model_path)
            
            # Get model info
            model_info = self.processor.get_model_info()
            self.embedding_dim = model_info.get("embedding_dim", 1024)
            self.model_name = f"AITeamVN/Vietnamese_Embedding (ONNX - {model_info.get('embedding_dim', 1024)}D)"
            
            logger.info(f"✅ Vietnamese ONNX model loaded successfully")
            logger.info(f"📊 Model embedding dimension: {self.embedding_dim}")
            logger.info(f"📊 Model name: {self.model_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load ONNX model: {e}")
            return False
    
    def encode_text(self, text: str) -> List[float]:
        """Encode text to embedding vector using ONNX processor"""
        try:
            # Load model if not already loaded
            if not self.processor:
                logger.info("🔄 Model not loaded, attempting to load ONNX model...")
                if not self.load_model():
                    raise ValueError("Failed to load ONNX model")
            
            # Use ONNX processor to generate embedding
            embedding = self.processor.process_single_text(text)
            
            logger.info(f"✅ Generated embedding with dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to encode text: {e}")
            raise
    

# Initialize services
embedding_service = EmbeddingService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info("Embedding service started - ready for development")
    yield
    # Shutdown (if needed)
    logger.info("Embedding service shutting down")

# Create FastAPI app with lifespan
app = FastAPI(
    title="PikaHelper Embedding Service", 
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/embed", response_model=EmbeddingResponse)
async def create_embedding(request: EmbeddingRequest):
    """Create embedding for a single text using ONNX processor"""
    try:
        # Try to load model if not loaded
        if not embedding_service.processor:
            logger.info("🔄 Model not loaded, attempting to load ONNX model...")
            if not embedding_service.load_model():
                logger.warning("⚠️ Failed to load ONNX model, using mock data")
                mock_embedding = [0.1] * embedding_service.embedding_dim
                return EmbeddingResponse(
                    embedding=mock_embedding,
                    chunk_id=request.chunk_id,
                    model_name="Mock Model (ONNX Fallback)"
                )
        
        # Generate real embedding using ONNX processor
        logger.info(f"🔄 Processing text: {request.text[:50]}...")
        embedding = embedding_service.encode_text(request.text)
        
        logger.info(f"✅ Generated embedding with dimension: {len(embedding)}")
        
        return EmbeddingResponse(
            embedding=embedding,
            chunk_id=request.chunk_id,
            model_name=embedding_service.model_name
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to create embedding: {e}")
        # Fallback to mock data
        mock_embedding = [0.1] * embedding_service.embedding_dim
        return EmbeddingResponse(
            embedding=mock_embedding,
            chunk_id=request.chunk_id,
            model_name="Mock Model (Error Fallback)"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "embedding-service",
        "version": "1.0.0",
        "environment": "development"
    }

@app.post("/preprocess")
async def preprocess_text(text: str):
    """Test text preprocessing"""
    return {
        "original": text,
        "processed": text.strip(),
        "length_original": len(text),
        "length_processed": len(text.strip()),
        "status": "mock_preprocessing"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
