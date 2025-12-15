#!/bin/bash
# Script to restart the green agent with CLOUDRUN_HOST set

# Your Cloudflare tunnel URL (update this if it changes)
TUNNEL_URL="con-played-only-landing.trycloudflare.com"

echo "=========================================="
echo "Restarting Green Agent with Cloudflare Tunnel"
echo "=========================================="
echo ""
echo "Tunnel URL: https://${TUNNEL_URL}"
echo ""

# Kill existing green agent if running
echo "Stopping existing green agent..."
pkill -f "main.py green" || echo "No existing green agent found"
sleep 2

# Set environment variable and start the agent
echo "Starting green agent with CLOUDRUN_HOST=${TUNNEL_URL}..."
echo ""
export CLOUDRUN_HOST="${TUNNEL_URL}"
uv run python main.py green

