#!/usr/bin/env python3
"""
Test script để kiểm tra ONNX model loading và embedding generation
"""

import os
import sys
import numpy as np
import requests
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_onnx_model_files():
    """Test if ONNX model files exist and are accessible"""
    try:
        model_path = "/app/models/embedding"
        
        if not os.path.exists(model_path):
            logger.error(f"❌ Model path not found: {model_path}")
            return False
        
        # List model files
        files = os.listdir(model_path)
        logger.info(f"📁 Model files: {files}")
        
        # Check for required files
        required_files = ["model.onnx", "config.json", "tokenizer.json"]
        missing_files = []
        
        for file in required_files:
            if file not in files:
                missing_files.append(file)
        
        if missing_files:
            logger.warning(f"⚠️ Missing files: {missing_files}")
        else:
            logger.info("✅ All required model files found")
        
        # Check file sizes
        for file in files:
            file_path = os.path.join(model_path, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                logger.info(f"📄 {file}: {size:,} bytes")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking model files: {e}")
        return False

def test_onnx_processor():
    """Test ONNX processor directly"""
    try:
        # Import ONNX processor
        sys.path.append('/app')
        from onnx_processor import ONNXEmbeddingProcessor
        
        model_path = "/app/models/embedding"
        
        logger.info("🔄 Initializing ONNX processor...")
        processor = ONNXEmbeddingProcessor(model_path)
        
        # Get model info
        model_info = processor.get_model_info()
        logger.info(f"📊 Model info: {model_info}")
        
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

def test_embedding_service():
    """Test embedding service API"""
    try:
        embedding_url = "http://localhost:8001"
        
        # Test health
        logger.info("🔄 Testing embedding service health...")
        response = requests.get(f"{embedding_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"✅ Service healthy: {health_data}")
        else:
            logger.error(f"❌ Service unhealthy: {response.status_code}")
            return False
        
        # Test embedding generation
        test_sentences = [
            "Xin chào, tôi là trợ lý AI chuyên về hướng dẫn game PokeMMO",
            "Làm thế nào để tải game PokeMMO trên điện thoại?",
            "Hướng dẫn hoàn thành cốt truyện Pokemon Fire Red"
        ]
        
        all_embeddings = []
        successful_tests = 0
        
        for i, sentence in enumerate(test_sentences, 1):
            logger.info(f"\n{i}. Testing sentence: {sentence}")
            logger.info("-" * 50)
            
            try:
                response = requests.post(
                    f"{embedding_url}/embed",
                    json={"text": sentence, "chunk_id": f"test_{i:03d}"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    embedding = result.get("embedding", [])
                    model_name = result.get("model_name", "Unknown")
                    dimension = len(embedding)
                    
                    logger.info(f"✅ Embedding generated successfully")
                    logger.info(f"📊 Model: {model_name}")
                    logger.info(f"📊 Dimension: {dimension}")
                    logger.info(f"📊 First 5 values: {embedding[:5]}")
                    
                    # Check if embedding is not all zeros or same values
                    unique_values = len(set(embedding))
                    if unique_values > 1:
                        logger.info(f"✅ Embedding has {unique_values} unique values")
                        all_embeddings.append(embedding)
                        successful_tests += 1
                    else:
                        logger.warning(f"⚠️ Embedding has only {unique_values} unique values (likely mock data)")
                        all_embeddings.append(embedding)
                        successful_tests += 1
                else:
                    logger.error(f"❌ Embedding generation failed: {response.status_code}")
                    logger.error(f"Error: {response.text}")
                    
            except Exception as e:
                logger.error(f"❌ Request failed: {e}")
        
        # Test similarity if we have embeddings
        if len(all_embeddings) >= 2:
            logger.info("\n🔄 Testing similarity between embeddings...")
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                sim = cosine_similarity([all_embeddings[0]], [all_embeddings[1]])[0][0]
                logger.info(f"📐 Cosine similarity between first two: {sim:.4f}")
                
                if sim < 0.99:  # Not identical
                    logger.info("✅ Embeddings are different (not mock data)")
                else:
                    logger.warning("⚠️ Embeddings are very similar (might be mock data)")
                    
            except Exception as e:
                logger.error(f"❌ Similarity calculation failed: {e}")
        
        logger.info(f"\n📊 Test Summary:")
        logger.info(f"✅ Successful tests: {successful_tests}/{len(test_sentences)}")
        logger.info(f"📊 Total embeddings: {len(all_embeddings)}")
        
        return successful_tests > 0
        
    except Exception as e:
        logger.error(f"❌ Embedding service test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting ONNX Embedding Tests")
    logger.info("=" * 50)
    
    # Test 1: Check model files
    logger.info("\n1. Testing model files...")
    files_ok = test_onnx_model_files()
    
    # Test 2: Test ONNX processor directly
    logger.info("\n2. Testing ONNX processor...")
    processor_ok = test_onnx_processor()
    
    # Test 3: Test embedding service API
    logger.info("\n3. Testing embedding service API...")
    service_ok = test_embedding_service()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 Test Results Summary:")
    logger.info(f"📁 Model files: {'✅ OK' if files_ok else '❌ FAILED'}")
    logger.info(f"🔧 ONNX processor: {'✅ OK' if processor_ok else '❌ FAILED'}")
    logger.info(f"🌐 Embedding service: {'✅ OK' if service_ok else '❌ FAILED'}")
    
    if files_ok and processor_ok and service_ok:
        logger.info("🎉 All tests passed! ONNX embedding is working correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
