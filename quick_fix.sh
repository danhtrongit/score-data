#!/bin/bash

echo "=== Quick Fix - Running without Docker volumes ==="
echo ""

# Stop existing container
sudo docker-compose down

# Update .env to use /tmp which always has write permissions
echo "Updating DATABASE_URL to use /tmp..."
sed -i 's|DATABASE_URL=.*|DATABASE_URL=sqlite:////tmp/financial_scores.db|' .env

# Create a simple Dockerfile without user switching
cat > Dockerfile.simple << 'EOF'
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8003
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8003
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
EOF

# Create simplified docker-compose
cat > docker-compose.simple.yml << 'EOF'
version: '3.8'
services:
  api-score:
    build:
      context: .
      dockerfile: Dockerfile.simple
    container_name: api-score-container
    ports:
      - "8003:8003"
    environment:
      - DATABASE_URL=sqlite:////tmp/financial_scores.db
      - DEBUG=false
      - LOG_LEVEL=INFO
      - HOST=0.0.0.0
      - PORT=8003
    env_file:
      - .env
    restart: unless-stopped
EOF

# Build and run
echo "Building and starting container..."
sudo docker-compose -f docker-compose.simple.yml build --no-cache
sudo docker-compose -f docker-compose.simple.yml up -d

# Wait and test
sleep 5
echo ""
echo "Testing API..."
curl -s http://localhost:8003/health | python3 -m json.tool || echo "Still starting..."

echo ""
echo "To view logs: sudo docker-compose -f docker-compose.simple.yml logs -f"
echo "To stop: sudo docker-compose -f docker-compose.simple.yml down"
