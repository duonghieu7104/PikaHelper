#!/usr/bin/env python3
"""
Script to help setup ONNX model for PikaHelper RAG System
Converts sentence-transformers model to ONNX format
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_to_onnx(model_name: str, output_dir: str):
    """Convert sentence-transformers model to ONNX format"""
    try:
        from sentence_transformers import SentenceTransformer
        import torch
        
        logger.info(f"Loading model: {model_name}")
        model = SentenceTransformer(model_name)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Convert to ONNX
        logger.info("Converting to ONNX format...")
        
        # Get the underlying transformer model
        transformer = model[0].auto_model
        
        # Create dummy input
        dummy_input = {
            'input_ids': torch.randint(0, 1000, (1, 128), dtype=torch.long),
            'attention_mask': torch.ones(1, 128, dtype=torch.long)
        }
        
        # Export to ONNX
        onnx_path = output_path / "model.onnx"
        torch.onnx.export(
            transformer,
            (dummy_input['input_ids'], dummy_input['attention_mask']),
            str(onnx_path),
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['input_ids', 'attention_mask'],
            output_names=['last_hidden_state'],
            dynamic_axes={
                'input_ids': {0: 'batch_size', 1: 'sequence'},
                'attention_mask': {0: 'batch_size', 1: 'sequence'},
                'last_hidden_state': {0: 'batch_size', 1: 'sequence'}
            }
        )
        
        # Save tokenizer
        tokenizer_path = output_path / "tokenizer"
        model[0].tokenizer.save_pretrained(str(tokenizer_path))
        
        # Save config
        config = {
            "model_name": model_name,
            "embedding_dim": model.get_sentence_embedding_dimension(),
            "max_seq_length": 512,
            "model_type": "sentence_transformer"
        }
        
        import json
        with open(output_path / "config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Model converted successfully to: {output_path}")
        logger.info(f"ONNX model saved to: {onnx_path}")
        logger.info(f"Tokenizer saved to: {tokenizer_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to convert model: {e}")
        return False

def download_model(model_name: str, output_dir: str):
    """Download and setup model files"""
    try:
        from sentence_transformers import SentenceTransformer
        
        logger.info(f"Downloading model: {model_name}")
        model = SentenceTransformer(model_name)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save tokenizer
        tokenizer_path = output_path / "tokenizer"
        model[0].tokenizer.save_pretrained(str(tokenizer_path))
        
        # Save config
        config = {
            "model_name": model_name,
            "embedding_dim": model.get_sentence_embedding_dimension(),
            "max_seq_length": 512,
            "model_type": "sentence_transformer"
        }
        
        import json
        with open(output_path / "config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Model downloaded successfully to: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Setup ONNX model for PikaHelper")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2", 
                       help="Model name to use")
    parser.add_argument("--output", default="./models/embedding", 
                       help="Output directory for model files")
    parser.add_argument("--convert-onnx", action="store_true", 
                       help="Convert to ONNX format")
    parser.add_argument("--download-only", action="store_true", 
                       help="Only download model files")
    
    args = parser.parse_args()
    
    if args.convert_onnx:
        success = convert_to_onnx(args.model, args.output)
    elif args.download_only:
        success = download_model(args.model, args.output)
    else:
        logger.info("Please specify --convert-onnx or --download-only")
        return
    
    if success:
        logger.info("Setup completed successfully!")
        logger.info(f"Model files are in: {args.output}")
        logger.info("You can now start the embedding service with your ONNX model.")
    else:
        logger.error("Setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
