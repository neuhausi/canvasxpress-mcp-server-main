# Use Amazon ECR Public Python image (no rate limits)
FROM public.ecr.aws/docker/library/python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . /app/

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Create cache directory for vector database
RUN mkdir -p /root/.cache

# Default command (run MCP server)
CMD ["python", "/app/src/mcp_server.py"]
