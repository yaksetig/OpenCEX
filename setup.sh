#!/bin/bash
set -e

echo "OpenCEX Setup Script"
echo "===================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "[OK] Created .env file"
fi

# Check if external network exists
if ! docker network ls | grep -q "caddy"; then
    echo "Creating external caddy network..."
    docker network create caddy
    echo "[OK] Created caddy network"
fi

# Ask about domain configuration
echo ""
echo "Domain Configuration:"
echo "1. HTTP-only (no SSL) - recommended for development"
echo "2. Custom domain with automatic HTTPS"
read -p "Choose option (1 or 2): " choice

if [ "$choice" = "2" ]; then
    read -p "Enter your domain name: " domain
    if [ "$(uname -s)" = "Darwin" ]; then
        sed -i '' "s/^DOMAIN=.*/DOMAIN=$domain/" .env
    else
        sed -i "s/^DOMAIN=.*/DOMAIN=$domain/" .env
    fi
    echo "[OK] Configured for HTTPS with domain: $domain"
    echo "WARNING: Make sure your domain's DNS points to this server."
else
    echo "[OK] Configured for HTTP-only mode"
fi

echo ""
echo "Starting services..."
docker compose up -d

echo ""
echo "[OK] Setup complete!"
echo ""
echo "Access your exchange at:"
if [ "$choice" = "2" ]; then
    echo "  https://$domain"
else
    echo "  http://localhost"
    echo "  or http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_SERVER_IP')"
fi
