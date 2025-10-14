#!/usr/bin/env python3
"""
ONNX Embedding Processor for PikaHelper RAG System
Handles Vietnamese text embedding using ONNX models
"""

import os
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ONNXEmbeddingProcessor:
    """Vietnamese embedding processor using sentence-transformers (fallback from ONNX)"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.embedding_dim = 1024  # Default dimension
        self.max_seq_length = 512
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize sentence-transformers model (fallback from ONNX)"""
        try:
            # Check if model directory exists
            if not os.path.exists(self.model_path):
                logger.error(f"❌ Model directory not found: {self.model_path}")
                raise FileNotFoundError(f"Model directory not found: {self.model_path}")
            
            # List model files
            files = os.listdir(self.model_path)
            logger.info(f"📁 Model files: {files}")
            
            # Try to load as sentence-transformers model first
            try:
                logger.info("🔄 Trying to load as sentence-transformers model...")
                self.model = SentenceTransformer(self.model_path)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.info(f"✅ Sentence-transformers model loaded from local directory")
                logger.info(f"📊 Embedding dimension: {self.embedding_dim}")
                return
            except Exception as e:
                logger.warning(f"⚠️ Failed to load as sentence-transformers: {e}")
            
            # Fallback to download from Hugging Face
            logger.info("🔄 Loading Vietnamese model from Hugging Face...")
            self.model = SentenceTransformer("AITeamVN/Vietnamese_Embedding")
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            
            logger.info(f"✅ Vietnamese model loaded from Hugging Face")
            logger.info(f"📊 Embedding dimension: {self.embedding_dim}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize model: {e}")
            raise e
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess Vietnamese text for embedding generation"""
        if not text or not isinstance(text, str):
            return ""
        
        try:
            # Basic text cleaning
            text = text.strip()
            text = " ".join(text.split())
            
            # Vietnamese text preprocessing
            text = self._vietnamese_preprocessing(text)
            
            # Truncate if too long
            if len(text) > 8000:
                text = text[:8000]
                logger.warning("⚠️ Text truncated to 8000 characters")
            
            return text
            
        except Exception as e:
            logger.warning(f"⚠️ Text preprocessing failed: {e}")
            return text.strip()
    
    def _vietnamese_preprocessing(self, text: str) -> str:
        """Vietnamese-specific text preprocessing"""
        try:
            # Try to use underthesea for Vietnamese word segmentation
            from underthesea import word_tokenize
            
            # Normalize Vietnamese text
            text = text.lower()
            
            # Tokenize using underthesea (better for Vietnamese)
            tokens = word_tokenize(text, format="text")
            
            # Join tokens with spaces for better embedding
            processed_text = " ".join(tokens.split())
            
            return processed_text
            
        except ImportError:
            logger.warning("⚠️ underthesea not available, using basic preprocessing")
            return text
        except Exception as e:
            logger.warning(f"⚠️ Vietnamese preprocessing error: {e}")
            return text
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts using sentence-transformers"""
        if not texts:
            return []
        
        try:
            # Preprocess texts
            processed_texts = [self.preprocess_text(text) for text in texts]
            logger.info(f"🔄 Processing {len(processed_texts)} texts")
            
            # Generate embeddings using sentence-transformers
            logger.info("🔄 Running sentence-transformers inference...")
            embeddings = self.model.encode(processed_texts, convert_to_tensor=False)
            
            logger.info(f"📊 Embeddings shape: {embeddings.shape}")
            logger.info(f"📊 Embedding dimension: {embeddings.shape[1]}")
            
            # Convert to list of lists
            embeddings_list = embeddings.tolist()
            
            return embeddings_list
            
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            import traceback
            traceback.print_exc()
            # Return zero embeddings for failed cases
            return [[0.0] * self.embedding_dim for _ in texts]
    
    def process_single_text(self, text: str) -> List[float]:
        """Process a single text and return embedding"""
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else [0.0] * self.embedding_dim
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_path": self.model_path,
            "embedding_dim": self.embedding_dim,
            "max_seq_length": self.max_seq_length,
            "model_name": getattr(self.model, 'model_name', 'Unknown') if self.model else 'Unknown',
            "model_type": "sentence-transformers"
        }

def test_onnx_processor():
    """Test function for ONNX processor"""
    try:
        model_path = "/app/models/embedding"
        
        if not os.path.exists(model_path):
            logger.error(f"❌ Model path not found: {model_path}")
            return None
        
        logger.info("🔄 Initializing ONNX processor...")
        processor = ONNXEmbeddingProcessor(model_path)
        
        # Test with Vietnamese sentences
        test_sentences = [
            "Xin chào, tôi là trợ lý AI chuyên về hướng dẫn game PokeMMO",
            "Làm thế nào để tải game PokeMMO trên điện thoại?",
            "Hướng dẫn hoàn thành cốt truyện Pokemon Fire Red",
            "Cách kiếm tiền hiệu quả trong PokeMMO",
            "Xây dựng đội hình PvP mạnh nhất"
        ]
        
        logger.info("🔄 Testing embedding generation...")
        embeddings = processor.generate_embeddings(test_sentences)
        
        if embeddings:
            logger.info(f"✅ Generated {len(embeddings)} embeddings")
            logger.info(f"📊 Embedding dimension: {len(embeddings[0])}")
            logger.info(f"📊 First embedding sample: {embeddings[0][:5]}")
            
            # Test similarity
            if len(embeddings) >= 2:
                from sklearn.metrics.pairwise import cosine_similarity
                sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                logger.info(f"📐 Similarity between first two: {sim:.4f}")
            
            return embeddings
        else:
            logger.error("❌ Failed to generate embeddings")
            return None
            
    except Exception as e:
        logger.error(f"❌ ONNX processor test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_onnx_processor()
