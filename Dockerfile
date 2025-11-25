FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Default environment variables
ENV OLLAMA_HOST=http://host.docker.internal:11434
ENV DEFAULT_MODEL=mistral

# Expose no ports by default (ollama runs on host)

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
