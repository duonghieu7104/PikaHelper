#!/usr/bin/env python3
"""
Script to test Vietnamese text processing through vi-stag and embedding model
"""

import os
import sys
import requests
import json
from typing import List, Dict, Any

def test_vietnamese_embedding():
    """Test Vietnamese text processing and embedding"""
    
    # Vietnamese test sentences
    test_sentences = [
        "Xin chào, tôi là trợ lý AI cho game PokeMMO",
        "Làm thế nào để tải game PokeMMO trên điện thoại?",
        "Hướng dẫn hoàn thành cốt truyện Pokemon Fire Red",
        "Cách kiếm tiền hiệu quả trong PokeMMO",
        "Xây dựng đội hình PvP mạnh nhất",
        "Hướng dẫn bắt Pokemon huyền thoại",
        "Cách mod hình ảnh 3D cho game",
        "Rematch Elite 4 để kiếm tiền",
        "Trồng Berry kiếm tiền trong game",
        "Đội hình cân bằng cho PvP"
    ]
    
    print("🇻🇳 Testing Vietnamese Text Processing and Embedding")
    print("=" * 60)
    
    # Test embedding service
    embedding_url = "http://localhost:8001"
    
    try:
        # Check if embedding service is running
        print("1. Checking embedding service health...")
        health_response = requests.get(f"{embedding_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Embedding service is running")
            print(f"   Status: {health_response.json()}")
        else:
            print("❌ Embedding service not responding")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to embedding service: {e}")
        return False
    
    print("\n2. Testing Vietnamese text preprocessing...")
    
    # Test preprocessing endpoint
    try:
        test_text = "Xin chào, tôi muốn học cách chơi PokeMMO"
        preprocess_response = requests.post(
            f"{embedding_url}/preprocess",
            data=test_text,
            headers={"Content-Type": "text/plain"},
            timeout=10
        )
        
        if preprocess_response.status_code == 200:
            preprocess_result = preprocess_response.json()
            print("✅ Text preprocessing successful")
            print(f"   Original: {preprocess_result.get('original', '')}")
            print(f"   Processed: {preprocess_result.get('processed', '')}")
            print(f"   Length: {preprocess_result.get('length_original', 0)} → {preprocess_result.get('length_processed', 0)}")
        else:
            print(f"❌ Preprocessing failed: {preprocess_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Preprocessing request failed: {e}")
    
    print("\n3. Testing embedding generation...")
    
    # Test embedding for each sentence
    embeddings = []
    for i, sentence in enumerate(test_sentences, 1):
        try:
            print(f"   Processing sentence {i}/{len(test_sentences)}: {sentence[:50]}...")
            
            # Create embedding request
            embedding_request = {
                "text": sentence,
                "chunk_id": f"test_chunk_{i}"
            }
            
            # Send request to embedding service
            response = requests.post(
                f"{embedding_url}/embed",
                json=embedding_request,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get("embedding", [])
                model_name = result.get("model_name", "Unknown")
                
                print(f"   ✅ Generated embedding: {len(embedding)} dimensions")
                print(f"   📊 Model: {model_name}")
                print(f"   🔢 First 5 values: {embedding[:5] if embedding else 'None'}")
                
                embeddings.append({
                    "sentence": sentence,
                    "embedding": embedding,
                    "model_name": model_name,
                    "dimension": len(embedding)
                })
                
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        
        print()  # Empty line for readability
    
    print("4. Analyzing results...")
    
    if embeddings:
        print(f"✅ Successfully processed {len(embeddings)} sentences")
        
        # Check embedding dimensions
        dimensions = [e["dimension"] for e in embeddings]
        unique_dims = set(dimensions)
        
        print(f"📊 Embedding dimensions: {unique_dims}")
        
        # Check model consistency
        models = [e["model_name"] for e in embeddings]
        unique_models = set(models)
        
        print(f"🤖 Models used: {unique_models}")
        
        # Sample similarity calculation (if we have multiple embeddings)
        if len(embeddings) >= 2:
            print("\n5. Testing similarity calculation...")
            try:
                # Simple cosine similarity between first two embeddings
                import numpy as np
                
                emb1 = np.array(embeddings[0]["embedding"])
                emb2 = np.array(embeddings[1]["embedding"])
                
                # Cosine similarity
                cosine_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                
                print(f"   📐 Cosine similarity between:")
                print(f"      '{embeddings[0]['sentence'][:30]}...'")
                print(f"      '{embeddings[1]['sentence'][:30]}...'")
                print(f"      = {cosine_sim:.4f}")
                
            except Exception as e:
                print(f"   ❌ Similarity calculation failed: {e}")
        
        # Save results to file
        output_file = "vietnamese_embedding_test_results.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(embeddings, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Results saved to: {output_file}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    else:
        print("❌ No embeddings were generated successfully")
        return False
    
    print("\n🎉 Vietnamese embedding test completed!")
    return True

def test_vi_stag_processing():
    """Test Vietnamese text processing with vi-stag (if available)"""
    
    print("\n🇻🇳 Testing Vietnamese Text Processing with vi-stag")
    print("=" * 60)
    
    test_texts = [
        "Xin chào, tôi là trợ lý AI cho game PokeMMO",
        "Làm thế nào để tải game PokeMMO trên điện thoại?",
        "Hướng dẫn hoàn thành cốt truyện Pokemon Fire Red"
    ]
    
    try:
        # Try to import vi-stag
        from vi_stag import ViStag
        print("✅ vi-stag library found")
        
        # Initialize ViStag
        vi_stag = ViStag()
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n{i}. Processing: {text}")
            
            try:
                # Tokenize
                tokens = vi_stag.tokenize(text)
                print(f"   🔤 Tokens: {tokens}")
                
                # POS tagging
                pos_tags = vi_stag.pos_tag(text)
                print(f"   📝 POS Tags: {pos_tags}")
                
                # Named Entity Recognition
                entities = vi_stag.ner(text)
                print(f"   🏷️  NER: {entities}")
                
            except Exception as e:
                print(f"   ❌ Processing failed: {e}")
                
    except ImportError:
        print("❌ vi-stag library not found")
        print("   Install with: pip install vi-stag")
        return False
    except Exception as e:
        print(f"❌ vi-stag initialization failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Vietnamese Text Processing and Embedding Test")
    print("=" * 60)
    
    # Test embedding service
    embedding_success = test_vietnamese_embedding()
    
    # Test vi-stag processing
    vi_stag_success = test_vi_stag_processing()
    
    print("\n📋 Summary:")
    print(f"   Embedding Service: {'✅ Success' if embedding_success else '❌ Failed'}")
    print(f"   vi-stag Processing: {'✅ Success' if vi_stag_success else '❌ Failed'}")
    
    if embedding_success and vi_stag_success:
        print("\n🎉 All tests passed! Vietnamese processing is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
