#!/bin/bash

# Script to deploy the API Score application with proper Docker permissions

echo "=== API Score Deployment Script ==="
echo ""

# Check if running with sudo when needed
check_docker_permissions() {
    if ! docker ps >/dev/null 2>&1; then
        echo "❌ Docker requires elevated permissions."
        echo "The current user needs to be added to the docker group or use sudo."
        echo ""
        return 1
    else
        echo "✅ Docker permissions OK"
        return 0
    fi
}

# Option 1: Add user to docker group (recommended for persistent fix)
fix_docker_group() {
    echo "Adding current user to docker group..."
    echo "Run these commands:"
    echo ""
    echo "  sudo usermod -aG docker $USER"
    echo "  newgrp docker"
    echo ""
    echo "After running these commands, log out and log back in for changes to take effect."
    echo "Then run: docker-compose up -d --build"
}

# Option 2: Run with sudo (quick fix)
run_with_sudo() {
    echo "Running Docker Compose with sudo..."
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        echo "❌ .env file not found. Creating from template..."
        cp .env.example .env 2>/dev/null || {
            echo "Creating basic .env file..."
            cat > .env << 'EOF'
# Application settings
DEBUG=false
LOG_LEVEL=INFO

# Server settings
HOST=0.0.0.0
PORT=8003

# Database
DATABASE_URL=sqlite:///./financial_scores.db

# Google Sheets API (replace with your actual credentials)
GOOGLE_SHEETS_API_KEY=your_api_key_here
SPREADSHEET_ID=your_spreadsheet_id_here
EOF
        }
        echo "✅ .env file created. Please update with your actual credentials."
        echo ""
    fi
    
    # Build and run with sudo
    echo "Building and starting containers..."
    sudo docker-compose down 2>/dev/null
    sudo docker-compose up -d --build
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Deployment successful!"
        echo ""
        echo "Application is running at:"
        echo "  - API: http://localhost:8003"
        echo "  - Docs: http://localhost:8003/docs"
        echo "  - Health: http://localhost:8003/health"
        echo ""
        echo "To view logs: sudo docker-compose logs -f"
        echo "To stop: sudo docker-compose down"
    else
        echo "❌ Deployment failed. Check the error messages above."
    fi
}

# Main execution
echo "Checking Docker permissions..."
if check_docker_permissions; then
    echo ""
    echo "Running Docker Compose..."
    docker-compose up -d --build
else
    echo ""
    echo "Choose an option:"
    echo "1) Fix permissions permanently (recommended)"
    echo "2) Run with sudo (quick fix)"
    echo "3) Exit"
    echo ""
    read -p "Enter choice [1-3]: " choice
    
    case $choice in
        1)
            fix_docker_group
            ;;
        2)
            run_with_sudo
            ;;
        3)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice. Exiting..."
            exit 1
            ;;
    esac
fi
