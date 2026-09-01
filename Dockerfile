# Buat Dockerfile
cat > Dockerfile << 'EOF'
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY .env.example .env
COPY setup.py .

# Create directories
RUN mkdir -p data/uploads data/outputs/knowledge_bases data/outputs/summaries

# Expose port
EXPOSE 8080

# Run the application
CMD ["streamlit", "run", "src/app.py", "--server.port=8080", "--server.address=0.0.0.0"]
EOF