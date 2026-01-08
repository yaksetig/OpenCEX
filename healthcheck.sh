#!/bin/bash

echo "OpenCEX Health Check"
echo "===================="

# Check if containers are running
echo ""
echo "Container Status:"
docker ps --filter "name=opencex" --format "table {{.Names}}\t{{.Status}}" | grep -E "opencex|frontend|caddy|redis|postgresql|rabbitmq"

# Check endpoints
echo ""
echo "Endpoint Status:"
curl -s -o /dev/null -w "Frontend: %{http_code}\n" http://localhost/
curl -s -o /dev/null -w "API: %{http_code}\n" http://localhost/api/
curl -s -o /dev/null -w "WebSocket: %{http_code}\n" http://localhost/ws/

echo ""
echo "Caddy Configuration:"
docker exec opencex-caddy-1 caddy version 2>/dev/null || echo "Caddy not responding"
