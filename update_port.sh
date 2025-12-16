#!/bin/bash
# Helper script to update controller's port file with actual agent port
# This can be run after agent starts to fix port detection issues

AGENT_ID=$1
EXPECTED_PORT=${2:-9003}

if [ -z "$AGENT_ID" ]; then
    echo "Usage: ./update_port.sh <agent_id> [port]"
    echo "Get agent_id from: curl http://localhost:8010/agents"
    exit 1
fi

AGENT_DIR=".ab/agents/$AGENT_ID"

if [ ! -d "$AGENT_DIR" ]; then
    echo "Error: Agent directory not found: $AGENT_DIR"
    exit 1
fi

# Try to detect port from /port endpoint if port not provided
if [ -z "$2" ]; then
    # Try common ports
    for test_port in 9003 9002 9001; do
        if curl -s "http://localhost:$test_port/port" > /dev/null 2>&1; then
            PORT_RESPONSE=$(curl -s "http://localhost:$test_port/port")
            DETECTED_PORT=$(echo "$PORT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['port'])" 2>/dev/null)
            if [ ! -z "$DETECTED_PORT" ]; then
                EXPECTED_PORT=$DETECTED_PORT
                echo "Detected port: $EXPECTED_PORT"
                break
            fi
        fi
    done
fi

# Update port file
echo "$EXPECTED_PORT" > "$AGENT_DIR/port"
echo "running" > "$AGENT_DIR/state"
echo "Updated $AGENT_DIR/port to $EXPECTED_PORT"

