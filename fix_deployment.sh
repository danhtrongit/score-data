#!/bin/bash

# Fix script for SQLite database permission issues in Docker

echo "=== Fixing API Score Docker Deployment ==="
echo ""

# Stop existing containers
echo "Stopping existing containers..."
sudo docker-compose down

# Create data and logs directories with proper permissions
echo "Creating data and logs directories..."
mkdir -p data logs
chmod 755 data logs

# Update .env file to use correct database path
echo "Updating .env file..."
if grep -q "DATABASE_URL=sqlite:///./financial_scores.db" .env 2>/dev/null; then
    sed -i 's|DATABASE_URL=sqlite:///./financial_scores.db|DATABASE_URL=sqlite:////app/data/financial_scores.db|' .env
    echo "✅ Updated DATABASE_URL in .env"
fi

# Clean up old containers and images
echo "Cleaning up old containers and images..."
sudo docker system prune -f

# Rebuild and start the container
echo "Rebuilding and starting container..."
sudo docker-compose build --no-cache
sudo docker-compose up -d

# Wait for container to start
echo "Waiting for container to start..."
sleep 5

# Check container status
echo ""
echo "Checking container status..."
sudo docker ps | grep api-score

# Check logs
echo ""
echo "Checking recent logs..."
sudo docker-compose logs --tail=20

# Test the health endpoint
echo ""
echo "Testing health endpoint..."
curl -s http://localhost:8003/health | python3 -m json.tool 2>/dev/null || echo "Health check failed"

echo ""
echo "=== Deployment fix complete ==="
echo ""
echo "To monitor logs: sudo docker-compose logs -f"
echo "To stop: sudo docker-compose down"
echo ""
echo "If the health check failed, wait a few more seconds and try:"
echo "  curl http://localhost:8003/health"
