#!/bin/bash
# Run script for the agent

# Set Cloudflare tunnel URL
# NOTE: Update this to match the URL that cloudflared gives you when you run:
# cloudflared tunnel --url http://localhost:8010
# This should be the controller's tunnel URL (port 8010), not the agent port
# The URL changes each time you create a new quick tunnel
export CLOUDRUN_HOST=buy-jeff-twist-safe.trycloudflare.com

# Run the white agent
uv run python main.py white

