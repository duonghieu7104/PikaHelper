#!/usr/bin/env python3
"""
Quick test for Vietnamese text processing and embedding
"""

import requests
import json

def test_vietnamese_sentence():
    """Test a single Vietnamese sentence through embedding service"""
    
    # Vietnamese test sentence
    vietnamese_text = "Xin chào, tôi là trợ lý AI chuyên về hướng dẫn game PokeMMO"
    
    print(f"🇻🇳 Testing Vietnamese sentence:")
    print(f"   Text: {vietnamese_text}")
    print()
    
    # Test embedding service
    embedding_url = "http://localhost:8001"
    
    try:
        # 1. Check health
        print("1. Checking embedding service health...")
        health_response = requests.get(f"{embedding_url}/health", timeout=5)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ Service healthy: {health_data.get('status', 'unknown')}")
            print(f"   📊 Service: {health_data.get('service', 'unknown')}")
            print(f"   🌍 Environment: {health_data.get('environment', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Cannot connect to embedding service: {e}")
        return False
    
    # 2. Test preprocessing
    print("\n2. Testing text preprocessing...")
    try:
        preprocess_response = requests.post(
            f"{embedding_url}/preprocess",
            data=vietnamese_text,
            headers={"Content-Type": "text/plain"},
            timeout=10
        )
        
        if preprocess_response.status_code == 200:
            preprocess_data = preprocess_response.json()
            print(f"   ✅ Preprocessing successful")
            print(f"   📝 Original: {preprocess_data.get('original', '')}")
            print(f"   🔧 Processed: {preprocess_data.get('processed', '')}")
            print(f"   📏 Length: {preprocess_data.get('length_original', 0)} → {preprocess_data.get('length_processed', 0)}")
        else:
            print(f"   ❌ Preprocessing failed: {preprocess_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Preprocessing request failed: {e}")
    
    # 3. Test embedding generation
    print("\n3. Testing embedding generation...")
    try:
        embedding_request = {
            "text": vietnamese_text,
            "chunk_id": "vietnamese_test_001"
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
            print(f"   🤖 Model: {model_name}")
            print(f"   📊 Dimension: {len(embedding)}")
            print(f"   🔢 First 5 values: {embedding[:5] if embedding else 'None'}")
            print(f"   📈 Last 5 values: {embedding[-5:] if embedding else 'None'}")
            
            # Calculate some statistics
            if embedding:
                import numpy as np
                emb_array = np.array(embedding)
                print(f"   📊 Statistics:")
                print(f"      Mean: {np.mean(emb_array):.6f}")
                print(f"      Std: {np.std(emb_array):.6f}")
                print(f"      Min: {np.min(emb_array):.6f}")
                print(f"      Max: {np.max(emb_array):.6f}")
                print(f"      Norm: {np.linalg.norm(emb_array):.6f}")
            
            # Save result
            result = {
                "text": vietnamese_text,
                "embedding": embedding,
                "model_name": model_name,
                "dimension": len(embedding),
                "statistics": {
                    "mean": float(np.mean(emb_array)) if embedding else 0,
                    "std": float(np.std(emb_array)) if embedding else 0,
                    "min": float(np.min(emb_array)) if embedding else 0,
                    "max": float(np.max(emb_array)) if embedding else 0,
                    "norm": float(np.linalg.norm(emb_array)) if embedding else 0
                }
            }
            
            # Save to file
            with open("vietnamese_embedding_result.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"   💾 Result saved to: vietnamese_embedding_result.json")
            
        else:
            print(f"   ❌ Embedding generation failed: {embedding_response.status_code}")
            print(f"   📝 Response: {embedding_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Embedding request failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
    
    print("\n🎉 Vietnamese embedding test completed successfully!")
    return True

if __name__ == "__main__":
    print("🚀 Quick Vietnamese Text Processing Test")
    print("=" * 50)
    
    success = test_vietnamese_sentence()
    
    if success:
        print("\n✅ All tests passed! Vietnamese processing is working.")
    else:
        print("\n❌ Tests failed. Check the output above for details.")
