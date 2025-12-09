# Deploying to AgentBeats Platform

This guide explains how to submit your medical agents to the AgentBeats evaluation platform.

## Overview

AgentBeats supports two deployment modes:

1. **Remote Mode**: Your agent runs on your own server (public URL required)
2. **Hosted Mode**: AgentBeats hosts your agent from GitHub repo or Docker image

## Prerequisites

Before deploying, ensure:

- [ ] Your agents work locally (tested with `python main.py launch`)
- [ ] Your code is in a Git repository (GitHub recommended)
- [ ] You have a way to expose your agents publicly (for remote mode)
- [ ] You have your AgentBeats account credentials

## Option 1: Remote Mode (Recommended for Testing)

In remote mode, you run the agents on your own infrastructure and provide URLs to AgentBeats.

### Step 1: Make Your Agents Publicly Accessible

You need to expose your agents so AgentBeats can reach them. Options:

#### A. Using ngrok (Quick Testing)

```bash
# Install ngrok: https://ngrok.com/download

# Terminal 1: Start green agent
python main.py green

# Terminal 2: Expose green agent
ngrok http 9001

# Terminal 3: Start white agent  
python main.py white

# Terminal 4: Expose white agent
ngrok http 9002
```

You'll get URLs like:
- Green: `https://abc123.ngrok.io`
- White: `https://def456.ngrok.io`

#### B. Using Cloud Services

Deploy to:
- **Heroku**: Use Procfile to run agents
- **Railway**: Deploy Python apps easily
- **Fly.io**: Good for long-running services
- **AWS/GCP/Azure**: Use EC2, Cloud Run, etc.

#### C. Using a VPS

Deploy to a VPS (DigitalOcean, Linode, etc.) and:
1. Install dependencies
2. Run agents with process managers (systemd, supervisor, PM2)
3. Use reverse proxy (nginx) with SSL

### Step 2: Verify Agent Cards Are Accessible

Test that AgentBeats can read your agent cards:

```bash
# Test green agent card
curl https://your-green-agent-url/.well-known/agent-card.json

# Test white agent card  
curl https://your-white-agent-url/.well-known/agent-card.json
```

Both should return JSON with agent information.

### Step 3: Submit to AgentBeats

1. Log into AgentBeats platform
2. Go to "Submit Agent" or "Add Agent"
3. Choose "Remote Mode"
4. Provide:
   - **Agent URL**: Your public URL (e.g., `https://abc123.ngrok.io`)
   - **Agent Type**: 
     - Green agent: Select "Green Agent" or "Evaluation Agent"
     - White agent: Select "White Agent" or "Participant Agent"
   - **Agent Name**: e.g., "Medical Green Agent" or "Medical White Agent"
   - **Description**: Brief description of your agent

### Step 4: Test Connection

AgentBeats will:
1. Fetch your agent card from `/.well-known/agent-card.json`
2. Verify A2A protocol compliance
3. Test basic connectivity

## Option 2: Hosted Mode (Recommended for Production)

In hosted mode, AgentBeats runs your agents for you.

### Step 1: Prepare Your Repository

Your GitHub repo should have:

```
orthoai-agent/
├── src/
│   ├── green_agent/
│   │   ├── agent.py
│   │   └── medical_green_agent.toml
│   ├── white_agent/
│   │   └── agent.py
│   └── ...
├── pyproject.toml
├── requirements.txt (optional, if not using pyproject.toml)
└── README.md
```

### Step 2: Create requirements.txt (if needed)

If AgentBeats needs a `requirements.txt`:

```bash
pip freeze > requirements.txt
```

Or create manually:

```txt
a2a-sdk[http-server]>=0.3.8
python-dotenv>=0.9.9
typer>=0.19.2
uvicorn>=0.37.0
httpx>=0.27.0
litellm>=1.0.0
```

### Step 3: Create Deployment Configuration

Create an `agentbeats.yaml` or similar config file (check AgentBeats docs for exact format):

```yaml
# Example - check AgentBeats documentation for exact format
agents:
  green:
    entrypoint: python -m src.green_agent.agent
    port: 9001
    env:
      - OPENAI_API_KEY
  white:
    entrypoint: python -m src.white_agent.agent
    port: 9002
    env:
      - OPENAI_API_KEY
```

### Step 4: Push to GitHub

```bash
git add .
git commit -m "Prepare for AgentBeats deployment"
git push origin main
```

### Step 5: Submit to AgentBeats

1. Log into AgentBeats
2. Go to "Submit Agent"
3. Choose "Hosted Mode"
4. Provide:
   - **GitHub Repository URL**: `https://github.com/yourusername/orthoai-agent`
   - **Branch**: `main` (or your branch)
   - **Agent Type**: Green or White
   - **Entry Point**: How to start the agent
   - **Environment Variables**: `OPENAI_API_KEY` (you'll set the value in AgentBeats UI)

### Step 6: Configure Environment Variables

In AgentBeats UI, set:
- `OPENAI_API_KEY`: Your OpenAI API key (stored securely by AgentBeats)

## Option 3: Docker Deployment

If AgentBeats supports Docker:

### Step 1: Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements
COPY pyproject.toml .
COPY requirements.txt* .

# Install dependencies
RUN pip install --no-cache-dir -e .

# Copy source code
COPY src/ ./src/
COPY green-agent/ ./green-agent/
COPY white-agent/ ./white-agent/

# Expose ports
EXPOSE 9001 9002

# Default command (can be overridden)
CMD ["python", "main.py", "green"]
```

### Step 2: Create docker-compose.yml (for local testing)

```yaml
version: '3.8'

services:
  green-agent:
    build: .
    command: python main.py green
    ports:
      - "9001:9001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  
  white-agent:
    build: .
    command: python main.py white
    ports:
      - "9002:9002"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Step 3: Build and Test Locally

```bash
docker-compose up
```

### Step 4: Push to Container Registry

```bash
# Tag and push to Docker Hub (or other registry)
docker build -t yourusername/orthoai-green-agent:latest .
docker push yourusername/orthoai-green-agent:latest

docker build -t yourusername/orthoai-white-agent:latest .
docker push yourusername/orthoai-white-agent:latest
```

### Step 5: Submit to AgentBeats

Provide the Docker image name in AgentBeats UI.

## Important Considerations

### 1. Environment Variables

- **Never commit API keys to Git**
- Use AgentBeats UI to set sensitive environment variables
- For local testing, use `.env` file (already in `.gitignore`)

### 2. Agent Cards

Your agent cards (TOML files) should have:
- Correct `url` field (will be set by AgentBeats in hosted mode)
- Proper `name`, `description`, `version`
- Skills and capabilities defined

### 3. Health Checks

AgentBeats may check:
- `/.well-known/agent-card.json` endpoint
- Basic A2A protocol compliance
- Response to test messages

### 4. Controller/Reset Support

For proper assessment isolation, ensure:
- White agent supports reset commands
- Green agent can reset white agents before evaluation

### 5. Port Configuration

- Agents should be configurable (not hardcoded ports)
- AgentBeats may assign ports dynamically
- Use environment variables for configuration

## Testing Before Submission

1. **Test agent cards are accessible:**
   ```bash
   curl http://localhost:9001/.well-known/agent-card.json
   curl http://localhost:9002/.well-known/agent-card.json
   ```

2. **Test A2A protocol:**
   ```bash
   python main.py launch
   ```

3. **Test with public URL (if using remote mode):**
   ```bash
   # With ngrok running
   curl https://your-ngrok-url/.well-known/agent-card.json
   ```

## Next Steps After Submission

1. **Wait for verification**: AgentBeats will verify your agent
2. **Check status**: Monitor agent status in dashboard
3. **Run assessments**: Once verified, agents can participate in evaluations
4. **View results**: Check leaderboards and metrics

## Getting Help

- **AgentBeats Documentation**: Check official docs for latest submission process
- **GitHub Issues**: Report issues or ask questions
- **Contact**: `sec+agentbeats@berkeley.edu` (from the documentation)

## Example Submission Checklist

For **Green Agent (Remote Mode)**:
- [ ] Agent running on public URL
- [ ] Agent card accessible at `/.well-known/agent-card.json`
- [ ] A2A protocol working
- [ ] Can receive and process evaluation tasks
- [ ] Returns JSON results in correct format
- [ ] Tested with white agent locally

For **White Agent (Remote Mode)**:
- [ ] Agent running on public URL
- [ ] Agent card accessible
- [ ] Responds with GET/POST/finish format only
- [ ] Supports reset commands
- [ ] Tested with green agent locally

For **Hosted Mode**:
- [ ] Code pushed to GitHub
- [ ] Repository is public (or AgentBeats has access)
- [ ] Dependencies clearly specified
- [ ] Entry points documented
- [ ] Environment variables listed
- [ ] README explains how to run

## Quick Reference

**Remote Mode URLs:**
- Green: `https://your-green-agent-url`
- White: `https://your-white-agent-url`

**Hosted Mode:**
- Repo: `https://github.com/yourusername/orthoai-agent`
- Green entrypoint: `python main.py green` or `python -m src.green_agent.agent`
- White entrypoint: `python main.py white` or `python -m src.white_agent.agent`

Good luck with your submission! 🚀

