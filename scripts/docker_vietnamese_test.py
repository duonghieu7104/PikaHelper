#!/usr/bin/env python3
"""
Vietnamese text processing test to run inside Docker container
"""

import requests
import json
import numpy as np

def test_vietnamese_embedding():
    """Test Vietnamese text processing and embedding"""
    
    print("🇻🇳 Testing Vietnamese Text Processing in Docker Container")
    print("=" * 60)
    
    # Vietnamese test sentences
    test_sentences = [
        "Xin chào, tôi là trợ lý AI chuyên về hướng dẫn game PokeMMO",
        "Làm thế nào để tải game PokeMMO trên điện thoại?",
        "Hướng dẫn hoàn thành cốt truyện Pokemon Fire Red",
        "Cách kiếm tiền hiệu quả trong PokeMMO",
        "Xây dựng đội hình PvP mạnh nhất"
    ]
    
    embedding_url = "http://localhost:8001"
    
    try:
        # 1. Check health
        print("1. Checking embedding service health...")
        health_response = requests.get(f"{embedding_url}/health", timeout=5)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ Service healthy: {health_data.get('status', 'unknown')}")
            print(f"   📊 Service: {health_data.get('service', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Cannot connect to embedding service: {e}")
        return False
    
    # 2. Test each sentence
    embeddings = []
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n{i}. Testing sentence: {sentence}")
        print("-" * 50)
        
        try:
            # Test preprocessing
            print("   🔧 Testing preprocessing...")
            preprocess_response = requests.post(
                f"{embedding_url}/preprocess",
                data=sentence.encode('utf-8'),
                headers={"Content-Type": "text/plain; charset=utf-8"},
                timeout=10
            )
            
            if preprocess_response.status_code == 200:
                preprocess_data = preprocess_response.json()
                print(f"   ✅ Preprocessing successful")
                print(f"      Original: {preprocess_data.get('original', '')}")
                print(f"      Processed: {preprocess_data.get('processed', '')}")
            else:
                print(f"   ❌ Preprocessing failed: {preprocess_response.status_code}")
            
            # Test embedding
            print("   🧠 Testing embedding generation...")
            embedding_request = {
                "text": sentence,
                "chunk_id": f"vietnamese_test_{i:03d}"
            }
            
            embedding_response = requests.post(
                f"{embedding_url}/embed",
                json=embedding_request,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if embedding_response.status_code == 200:
                embedding_data = embedding_response.json()
                embedding = embedding_data.get("embedding", [])
                model_name = embedding_data.get("model_name", "Unknown")
                
                print(f"   ✅ Embedding generated successfully")
                print(f"      Model: {model_name}")
                print(f"      Dimension: {len(embedding)}")
                print(f"      First 5 values: {embedding[:5] if embedding else 'None'}")
                
                # Calculate statistics
                if embedding:
                    emb_array = np.array(embedding)
                    print(f"      Statistics:")
                    print(f"        Mean: {np.mean(emb_array):.6f}")
                    print(f"        Std: {np.std(emb_array):.6f}")
                    print(f"        Min: {np.min(emb_array):.6f}")
                    print(f"        Max: {np.max(emb_array):.6f}")
                    print(f"        Norm: {np.linalg.norm(emb_array):.6f}")
                
                embeddings.append({
                    "sentence": sentence,
                    "embedding": embedding,
                    "model_name": model_name,
                    "dimension": len(embedding)
                })
                
            else:
                print(f"   ❌ Embedding failed: {embedding_response.status_code}")
                print(f"      Response: {embedding_response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    # 3. Test similarity between embeddings
    if len(embeddings) >= 2:
        print(f"\n3. Testing similarity between embeddings...")
        try:
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
    
    # 4. Save results
    if embeddings:
        print(f"\n4. Saving results...")
        try:
            with open("/app/vietnamese_embedding_results.json", "w", encoding="utf-8") as f:
                json.dump(embeddings, f, ensure_ascii=False, indent=2)
            print(f"   💾 Results saved to: /app/vietnamese_embedding_results.json")
        except Exception as e:
            print(f"   ❌ Failed to save results: {e}")
    
    print(f"\n🎉 Vietnamese embedding test completed!")
    print(f"   📊 Processed {len(embeddings)} sentences successfully")
    
    return len(embeddings) > 0

if __name__ == "__main__":
    success = test_vietnamese_embedding()
    exit(0 if success else 1)
