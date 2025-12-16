#!/bin/bash
# Run script for the agent

# Set ngrok tunnel URL
# NOTE: Update this to match the URL that ngrok gives you when you run:
# ngrok http 8010
# This should be the controller's tunnel URL (port 8010), not the agent port
# The URL changes each time you create a new tunnel
export CLOUDRUN_HOST=55c3b2b7f0c1.ngrok-free.app

# Set agent port (controller should set this, but ensure it's set)
export AGENT_PORT=9003
export HOST=${HOST:-localhost}

# Run the white agent
uv run python main.py white

