#!/bin/bash
# Run script for the agent

# Set Cloudflare tunnel URL
# NOTE: Update this to match the URL that cloudflared gives you when you run:
# cloudflared tunnel --url http://localhost:9001
# The URL changes each time you create a new quick tunnel
export CLOUDRUN_HOST=walt-adjustable-addressing-isle.trycloudflare.com

# Set controller port (for agentbeats controller)
# export PORT=8030

# Run the green agent
uv run python main.py green

