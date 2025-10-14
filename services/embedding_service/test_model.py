#!/usr/bin/env python3
"""
Test Vietnamese embedding model with sentence-transformers
"""

from sentence_transformers import SentenceTransformer
import torch
from pyvi import ViTokenizer

print("🇻🇳 Testing Vietnamese Embedding Model")
print("=" * 60)

# Download from the 🤗 Hub
print("📥 Loading model: huyydangg/DEk21_hcmute_embedding")
model = SentenceTransformer("huyydangg/DEk21_hcmute_embedding")
print("✅ Model loaded successfully")

# Define query (câu hỏi về PokeMMO) và docs (hướng dẫn)
query = "Làm thế nào để tải game PokeMMO trên điện thoại?"
docs = [
    "Hướng dẫn tải game PokeMMO cho điện thoại Android và iOS",
    "Cách hoàn thành cốt truyện Pokemon Fire Red trong PokeMMO",
    "Hướng dẫn kiếm tiền hiệu quả bằng cách Rematch Elite 4",
    "Xây dựng đội hình PvP mạnh nhất cho PokeMMO",
    "Cách bắt Pokemon huyền thoại trong game PokeMMO"
]

print(f"\n📝 Query: {query}")
print(f"📚 Number of documents: {len(docs)}")

# Tách từ cho query
print("\n🔧 Tokenizing query...")
segmented_query = ViTokenizer.tokenize(query)
print(f"   Original: {query}")
print(f"   Segmented: {segmented_query}")

# Tách từ cho từng dòng văn bản
print("\n🔧 Tokenizing documents...")
segmented_docs = [ViTokenizer.tokenize(doc) for doc in docs]
for i, (original, segmented) in enumerate(zip(docs, segmented_docs), 1):
    print(f"   Doc {i}:")
    print(f"      Original: {original}")
    print(f"      Segmented: {segmented}")

# Encode query and documents
print("\n🧠 Generating embeddings...")
query_embedding = model.encode([segmented_query])
doc_embeddings = model.encode(segmented_docs)

print(f"✅ Query embedding shape: {query_embedding.shape}")
print(f"✅ Document embeddings shape: {doc_embeddings.shape}")
print(f"📊 Embedding dimension: {query_embedding.shape[1]}")

# Calculate cosine similarity
print("\n📐 Calculating cosine similarity...")
similarities = torch.nn.functional.cosine_similarity(
    torch.tensor(query_embedding), torch.tensor(doc_embeddings)
).flatten()

# Sort documents by cosine similarity
sorted_indices = torch.argsort(similarities, descending=True)
sorted_docs = [docs[idx] for idx in sorted_indices]
sorted_scores = [similarities[idx].item() for idx in sorted_indices]

# Print sorted documents with their cosine scores
print("\n🎯 Results (sorted by relevance):")
print("-" * 60)
for i, (doc, score) in enumerate(zip(sorted_docs, sorted_scores), 1):
    print(f"{i}. Score: {score:.4f}")
    print(f"   Document: {doc}")
    print()

# Test với một câu tiếng Việt đơn giản
print("\n🧪 Testing with simple Vietnamese sentence:")
test_sentence = "Xin chào, tôi là trợ lý AI chuyên về hướng dẫn game PokeMMO"
print(f"   Original: {test_sentence}")

segmented_test = ViTokenizer.tokenize(test_sentence)
print(f"   Segmented: {segmented_test}")

test_embedding = model.encode([segmented_test])
print(f"   Embedding shape: {test_embedding.shape}")
print(f"   Embedding dimension: {test_embedding.shape[1]}")
print(f"   First 10 values: {test_embedding[0][:10]}")

# Check if embedding is not mock data
unique_values = len(set(test_embedding[0]))
print(f"   Unique values: {unique_values}")

if unique_values > 10:
    print("   ✅ Real embedding generated (not mock data)!")
else:
    print("   ⚠️  Possible mock data detected")

print("\n🎉 Test completed successfully!")

