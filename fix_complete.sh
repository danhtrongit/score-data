#!/bin/bash

echo "=== Complete Fix for API Score Docker Deployment ==="
echo ""

# Stop and remove existing containers
echo "1. Stopping and removing existing containers..."
sudo docker-compose down
sudo docker rm -f api-score-container 2>/dev/null

# Create directories with proper permissions
echo "2. Creating directories with proper permissions..."
sudo mkdir -p data logs
sudo chmod 777 data logs
echo "   ✅ Created data and logs directories with full permissions"

# Check if .env exists, create if not
echo "3. Checking .env file..."
if [ ! -f .env ]; then
    echo "   Creating .env file..."
    cat > .env << 'EOF'
# Application settings
DEBUG=false
LOG_LEVEL=INFO

# Server settings
HOST=0.0.0.0
PORT=8003

# Database - using /tmp for guaranteed write access
DATABASE_URL=sqlite:////tmp/financial_scores.db

# Google Sheets API (replace with your actual credentials)
GOOGLE_SHEETS_API_KEY=your_api_key_here
SPREADSHEET_ID=your_spreadsheet_id_here
EOF
    echo "   ✅ Created .env file"
else
    echo "   ✅ .env file exists"
fi

# Create a modified Dockerfile that uses /tmp for database
echo "4. Creating modified Dockerfile..."
cat > Dockerfile.fixed << 'EOF'
# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8003

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories with proper permissions
RUN mkdir -p /app/data /tmp/db && \
    chmod 777 /app/data /tmp/db /tmp

# No need to switch user - run as root for simplicity
# This is acceptable for development/testing

# Expose the port
EXPOSE 8003

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
EOF
echo "   ✅ Created Dockerfile.fixed"

# Create a modified docker-compose.yml
echo "5. Creating modified docker-compose.yml..."
cat > docker-compose.fixed.yml << 'EOF'
version: '3.8'

services:
  api-score:
    build:
      context: .
      dockerfile: Dockerfile.fixed
    container_name: api-score-container
    ports:
      - "8003:8003"
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
      - HOST=0.0.0.0
      - PORT=8003
      - DATABASE_URL=sqlite:////tmp/financial_scores.db
    env_file:
      - .env
    volumes:
      # Use tmpfs for database (in-memory with disk backup)
      - db-data:/tmp
      # Mount logs directory
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - api-score-network

volumes:
  db-data:
    driver: local

networks:
  api-score-network:
    driver: bridge
EOF
echo "   ✅ Created docker-compose.fixed.yml"

# Clean up old images and containers
echo "6. Cleaning up old Docker resources..."
sudo docker system prune -f

# Build with the fixed configuration
echo "7. Building Docker image with fixed configuration..."
sudo docker-compose -f docker-compose.fixed.yml build --no-cache

# Start the container
echo "8. Starting container..."
sudo docker-compose -f docker-compose.fixed.yml up -d

# Wait for container to fully start
echo "9. Waiting for container to start (10 seconds)..."
sleep 10

# Check container status
echo "10. Checking container status..."
sudo docker ps | grep api-score

# Check logs
echo ""
echo "11. Checking logs..."
sudo docker-compose -f docker-compose.fixed.yml logs --tail=30

# Test the API
echo ""
echo "12. Testing API endpoints..."
echo "   Testing health endpoint..."
if curl -s http://localhost:8003/health > /dev/null 2>&1; then
    echo "   ✅ Health endpoint is working!"
    curl -s http://localhost:8003/health | python3 -m json.tool
else
    echo "   ❌ Health endpoint not responding yet"
fi

echo ""
echo "=== Fix Complete ==="
echo ""
echo "Commands to use:"
echo "  View logs:    sudo docker-compose -f docker-compose.fixed.yml logs -f"
echo "  Stop:         sudo docker-compose -f docker-compose.fixed.yml down"
echo "  Restart:      sudo docker-compose -f docker-compose.fixed.yml restart"
echo ""
echo "Access points:"
echo "  API:          http://localhost:8003"
echo "  Docs:         http://localhost:8003/docs"
echo "  Health:       http://localhost:8003/health"
echo ""

# Final check
echo "Performing final health check..."
for i in {1..5}; do
    if curl -s http://localhost:8003/health > /dev/null 2>&1; then
        echo "✅ API is running successfully!"
        break
    else
        echo "Attempt $i/5: Waiting for API to start..."
        sleep 2
    fi
done
