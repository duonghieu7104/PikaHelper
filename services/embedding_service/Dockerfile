FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch with CUDA support first (heavy dependency - cache this layer)
RUN pip install --no-cache-dir --timeout 1000 --retries 5 torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu118

# Copy requirements and install other dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 1000 --retries 5 -r requirements.txt

# Copy application code
COPY . .

CMD ["python", "main.py"]
