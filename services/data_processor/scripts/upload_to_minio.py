#!/usr/bin/env python3
"""
Script to upload local data files to MinIO
Reads from local ./data/raw/ and uploads to MinIO bronze bucket
"""

import os
import sys
import logging
from pathlib import Path
from typing import List
import mimetypes

from minio import Minio
from minio.error import S3Error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MinIOUploader:
    """MinIO client for uploading files"""
    
    def __init__(self):
        # MinIO configuration
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "password123")
        
        # Initialize MinIO client
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False
        )
        
        # Ensure bucket exists
        self.ensure_bucket()
    
    def ensure_bucket(self):
        """Create bronze-raw bucket if it doesn't exist"""
        bucket_name = "bronze-raw"
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"✅ Created bucket: {bucket_name}")
            else:
                logger.info(f"✅ Bucket {bucket_name} already exists")
        except S3Error as e:
            logger.error(f"❌ Failed to create bucket: {e}")
            raise
    
    def upload_file(self, local_path: Path, object_name: str) -> bool:
        """Upload single file to MinIO"""
        try:
            # Get file size
            file_size = local_path.stat().st_size
            
            # Get content type
            content_type, _ = mimetypes.guess_type(str(local_path))
            if not content_type:
                content_type = "application/octet-stream"
            
            # Upload file
            with open(local_path, 'rb') as file_data:
                self.client.put_object(
                    bucket_name="bronze-raw",
                    object_name=object_name,
                    data=file_data,
                    length=file_size,
                    content_type=content_type
                )
            
            logger.info(f"✅ Uploaded: {object_name} ({file_size} bytes)")
            return True
            
        except S3Error as e:
            logger.error(f"❌ Failed to upload {object_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error uploading {object_name}: {e}")
            return False
    
    def upload_directory(self, local_dir: Path) -> int:
        """Upload all files from local directory to MinIO"""
        if not local_dir.exists():
            logger.error(f"❌ Directory not found: {local_dir}")
            return 0
        
        uploaded_count = 0
        total_files = 0
        
        # Get all files recursively
        for file_path in local_dir.rglob("*"):
            if file_path.is_file():
                total_files += 1
                
                # Skip temporary files
                if file_path.name.startswith('~$'):
                    logger.info(f"⏭️ Skipping temp file: {file_path.name}")
                    continue
                
                # Create object name (relative path from data/raw)
                try:
                    # Get relative path from data/raw
                    relative_path = file_path.relative_to(local_dir)
                    object_name = str(relative_path).replace("\\", "/")
                    
                    logger.info(f"📤 Uploading: {file_path.name}")
                    
                    # Upload file
                    if self.upload_file(file_path, object_name):
                        uploaded_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error processing {file_path}: {e}")
                    continue
        
        logger.info(f"📊 Upload Summary:")
        logger.info(f"   Total files found: {total_files}")
        logger.info(f"   Successfully uploaded: {uploaded_count}")
        logger.info(f"   Failed uploads: {total_files - uploaded_count}")
        
        return uploaded_count

def main():
    """Main function to upload data files"""
    logger.info("🚀 Starting data upload to MinIO...")
    
    try:
        # Initialize uploader
        uploader = MinIOUploader()
        
        # Define local data directory
        data_dir = Path("./data/raw")
        
        if not data_dir.exists():
            logger.error(f"❌ Data directory not found: {data_dir}")
            logger.info("💡 Make sure you're running from the project root directory")
            sys.exit(1)
        
        logger.info(f"📁 Reading from: {data_dir.absolute()}")
        logger.info(f"🎯 Uploading to: {uploader.endpoint}/bronze-raw")
        
        # Upload all files
        uploaded_count = uploader.upload_directory(data_dir)
        
        if uploaded_count > 0:
            logger.info(f"✅ Upload completed! {uploaded_count} files uploaded to MinIO")
        else:
            logger.warning("⚠️ No files were uploaded")
            
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
