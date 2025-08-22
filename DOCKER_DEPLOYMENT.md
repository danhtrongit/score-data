# Docker Deployment Guide - API Score

## Quick Fix for Permission Error

You're encountering a Docker permission error. Here are two solutions:

### Solution 1: Add User to Docker Group (Recommended - Permanent Fix)

Run these commands on your server:

```bash
# Add your user to the docker group
sudo usermod -aG docker $USER

# Apply the new group membership
newgrp docker

# Or log out and log back in for changes to take effect
```

After this, you can run docker commands without sudo:
```bash
docker-compose up -d --build
```

### Solution 2: Use Sudo (Quick Fix)

Run all docker commands with sudo:

```bash
# Build and start the container
sudo docker-compose up -d --build

# View logs
sudo docker-compose logs -f

# Stop the container
sudo docker-compose down

# Restart the container
sudo docker-compose restart
```

## Automated Deployment Script

Use the provided deployment script for easier management:

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

The script will:
1. Check Docker permissions
2. Create .env file if missing
3. Offer to fix permissions or run with sudo
4. Build and start the container

## Manual Commands for Your Server

Based on your server path `/home/iqx-score/htdocs/score.iqx.vn/score-data`, here are the exact commands:

```bash
# Navigate to your project directory
cd /home/iqx-score/htdocs/score.iqx.vn/score-data

# Create .env file if not exists
nano .env
# Add the following content:
# DEBUG=false
# LOG_LEVEL=INFO
# HOST=0.0.0.0
# PORT=8003
# DATABASE_URL=sqlite:///./financial_scores.db
# GOOGLE_SHEETS_API_KEY=your_actual_api_key
# SPREADSHEET_ID=your_actual_spreadsheet_id

# Option A: If you added user to docker group
docker-compose up -d --build

# Option B: Using sudo
sudo docker-compose up -d --build

# Check if container is running
sudo docker ps

# View logs
sudo docker-compose logs -f

# Test the API
curl http://localhost:8003/health
```

## Verify Deployment

Once running, test these endpoints:

- Health Check: `curl http://localhost:8003/health`
- API Docs: Open browser to `http://your-server-ip:8003/docs`
- Root endpoint: `curl http://localhost:8003/`

## Troubleshooting

### If port 8003 is already in use:
```bash
# Check what's using port 8003
sudo lsof -i :8003

# Or change the port in docker-compose.yml and .env file
```

### If build fails:
```bash
# Clean up and rebuild
sudo docker-compose down
sudo docker system prune -f
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

### View container logs for errors:
```bash
sudo docker-compose logs -f api-score
```

## Production Considerations

1. **SSL/TLS**: Consider using a reverse proxy (nginx) for HTTPS
2. **Firewall**: Ensure port 8003 is open if accessing from outside
3. **Monitoring**: Set up monitoring for the container
4. **Backups**: Regular backups of the SQLite database file
5. **Secrets**: Use proper secret management for API keys

## Nginx Reverse Proxy Example (Optional)

If you want to serve the API through nginx with SSL:

```nginx
server {
    listen 80;
    server_name score.iqx.vn;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name score.iqx.vn;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
