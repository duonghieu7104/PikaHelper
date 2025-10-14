#!/usr/bin/env python3
"""
Script to test Vietnamese model locally before building container
"""

import os
import sys
from pathlib import Path

def test_model_local():
    """Test if local model can be loaded"""
    model_path = "models/embedding"
    
    print(f"Testing model at: {model_path}")
    
    # Check if model directory exists
    if not os.path.exists(model_path):
        print(f"❌ Model directory not found: {model_path}")
        return False
    
    # Check required files
    required_files = ["config.json", "tokenizer.json", "tokenizer_config.json"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join(model_path, file)):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ Model directory and files exist")
    
    # Try to load tokenizer
    try:
        from transformers import AutoTokenizer
        print("Testing tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print("✅ Tokenizer loaded successfully")
        
        # Test tokenization
        test_text = "Xin chào, tôi là trợ lý AI"
        tokens = tokenizer(test_text)
        print(f"✅ Tokenization test passed: {len(tokens['input_ids'])} tokens")
        
    except Exception as e:
        print(f"❌ Tokenizer failed: {e}")
        return False
    
    # Try to load model
    try:
        from transformers import AutoModel
        print("Testing model...")
        model = AutoModel.from_pretrained(model_path)
        print("✅ Model loaded successfully")
        
    except Exception as e:
        print(f"❌ Model failed: {e}")
        return False
    
    print("✅ All tests passed! Model is ready for container.")
    return True

if __name__ == "__main__":
    success = test_model_local()
    sys.exit(0 if success else 1)
