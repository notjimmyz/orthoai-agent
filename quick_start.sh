#!/bin/bash
# Quick start script - kills old processes and starts fresh

echo "🧹 Cleaning up old processes..."
pkill -9 -f "agentbeats run_ctrl" 2>/dev/null || true
pkill -9 -f "main.py green" 2>/dev/null || true
rm -rf .ab 2>/dev/null || true
sleep 2

echo "✅ Cleanup complete"
echo ""
echo "Now start your setup:"
echo ""
echo "1. Terminal 1 - Start Cloudflare tunnel:"
echo "   cloudflared tunnel --url http://localhost:8010"
echo ""
echo "2. Terminal 2 - Start controller (use URL from Terminal 1):"
echo "   CLOUDRUN_HOST=https://your-url.trycloudflare.com agentbeats run_ctrl"
echo ""
echo "3. Terminal 3 - Test (after waiting 10 seconds):"
echo "   ./test_setup.sh verify"
echo ""



