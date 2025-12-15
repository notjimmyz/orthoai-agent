# Agentify Example: Tau-Bench

Example code for agentifying Tau-Bench using A2A and MCP standards.

## Project Structure

```
src/
├── green_agent/    # Assessment manager agent
├── white_agent/    # Target agent being tested
└── launcher.py     # Evaluation coordinator
```

## Installation

```bash
uv sync
```

## Usage

First, configure `.env` with `OPENAI_API_KEY=...`, then

```bash
# Launch complete evaluation
uv run python main.py launch
```

### Using Cloudflare Tunnel for External Access

If you're exposing your agent via a Cloudflare tunnel (or similar), set the `CLOUDRUN_HOST` environment variable to ensure the agent card publishes the correct public URL:

```bash
# Set the public URL (without http:// or https:// - it will default to https://)
export CLOUDRUN_HOST=con-played-only-landing.trycloudflare.com

# Or with full URL
export CLOUDRUN_HOST=https://con-played-only-landing.trycloudflare.com

# Then start your agent
uv run python main.py green
```

**Important**: The agent will still run on `localhost:9001` (or your specified port), but the agent card will advertise the `CLOUDRUN_HOST` URL, making it accessible to external platforms like AgentBeats.

**Why this matters**: External platforms fetch the agent card to discover how to connect to your agent. If the card says `http://localhost:9001`, they can't reach it. Setting `CLOUDRUN_HOST` ensures the card publishes your public tunnel URL instead.
