# Quick Deploy to AgentBeats

## Option 1: Cloudflare Tunnel (Recommended - Free, Multiple Tunnels)

Cloudflare Tunnel (cloudflared) is **free** and allows **unlimited tunnels** simultaneously.

### Step 1: Install cloudflared

```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Or download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

### Step 2: Start Your Agents

**Terminal 1 - Green Agent:**
```bash
python main.py green
```

**Terminal 2 - White Agent:**
```bash
python main.py white
```

### Step 3: Expose Both Agents with Cloudflare Tunnel

**Terminal 3 - Expose Green Agent:**
```bash
cloudflared tunnel --url http://localhost:9001
# Copy the HTTPS URL (e.g., https://abc123.trycloudflare.com)
```

**Terminal 4 - Expose White Agent:**
```bash
cloudflared tunnel --url http://localhost:9002
# Copy the HTTPS URL (e.g., https://def456.trycloudflare.com)
```

**Note:** Each tunnel gets a unique random URL. Keep both terminals running.

### Step 4: Verify Agent Cards

```bash
# Test green agent
curl https://your-green-cloudflare-url/.well-known/agent-card.json

# Test white agent
curl https://your-white-cloudflare-url/.well-known/agent-card.json
```

### Step 5: Submit to AgentBeats

Use the Cloudflare URLs when submitting to AgentBeats (same process as ngrok).

---

## Option 2: LocalTunnel (Free, Multiple Tunnels)

LocalTunnel is another free alternative that supports multiple tunnels.

### Step 1: Install LocalTunnel

```bash
npm install -g localtunnel
```

### Step 2: Start Your Agents

**Terminal 1 - Green Agent:**
```bash
python main.py green
```

**Terminal 2 - White Agent:**
```bash
python main.py white
```

### Step 3: Expose Both Agents

**Terminal 3 - Expose Green Agent:**
```bash
lt --port 9001
# Copy the HTTPS URL (e.g., https://abc123.loca.lt)
```

**Terminal 4 - Expose White Agent:**
```bash
lt --port 9002
# Copy the HTTPS URL (e.g., https://def456.loca.lt)
```

---

## Option 3: ngrok (Free Plan - One Tunnel at a Time)

### Step 1: Install ngrok
```bash
# Download from https://ngrok.com/download
# Or via homebrew:
brew install ngrok
```

**Note:** The free ngrok plan only allows **one tunnel at a time**. Use Cloudflare Tunnel or LocalTunnel instead for multiple tunnels.

If you must use ngrok, you can:
1. Test one agent at a time, OR
2. Use ngrok config file with `ngrok start --all` (requires paid plan for multiple tunnels)

### Verify Agent Cards

```bash
# Test green agent (replace with your actual URL)
curl https://your-green-agent-url/.well-known/agent-card.json

# Test white agent (replace with your actual URL)
curl https://your-white-agent-url/.well-known/agent-card.json
```

Both should return JSON with agent information.

### Submit to AgentBeats

1. Go to AgentBeats platform (or wait for release)
2. Click "Submit Agent" or "Add Agent"
3. Choose **Remote Mode**
4. For **Green Agent**:
   - **Public Controller URL**: `https://your-green-agent-url`
   - Type: Green Agent / Evaluation Agent
   - Name: "Medical Green Agent"
5. For **White Agent**:
   - **Public Controller URL**: `https://your-white-agent-url`
   - Type: White Agent / Participant Agent
   - Name: "Medical White Agent"

### Set Environment Variables

In AgentBeats UI or your cloud platform, set:
- `OPENAI_API_KEY`: Your OpenAI API key

## Summary

**For Quick Testing:**
- Use **Cloudflare Tunnel** (easiest, free, multiple tunnels)

**For Production:**
- Use **Railway.app** or **Fly.io** (free tiers, permanent URLs)

**Avoid:**
- ngrok free plan (only one tunnel at a time)

## GitHub Hosted Mode (No ngrok Needed)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Medical agents for AgentBeats"
git remote add origin https://github.com/yourusername/orthoai-agent.git
git push -u origin main
```

### Step 2: Submit to AgentBeats

1. Go to AgentBeats platform
2. Choose **Hosted Mode**
3. Provide:
   - Repository: `https://github.com/yourusername/orthoai-agent`
   - Branch: `main`
   - **Green Agent Entry Point**: `python main.py green`
   - **White Agent Entry Point**: `python main.py white`
   - Port: 9001 (green) or 9002 (white)

### Step 3: Configure Environment

Set `OPENAI_API_KEY` in AgentBeats UI.

## What AgentBeats Needs

✅ **Agent Card** accessible at `/.well-known/agent-card.json`  
✅ **A2A Protocol** compliance  
✅ **Public URL** (for remote mode) or **GitHub repo** (for hosted mode)  
✅ **Environment variables** configured  

## Quick Checklist

- [ ] Agents work locally (`python main.py launch`)
- [ ] Agent cards are accessible
- [ ] Public URLs work (if remote mode)
- [ ] GitHub repo is public (if hosted mode)
- [ ] Environment variables set in AgentBeats
- [ ] Agent type selected correctly (Green vs White)

## Need Help?

- Full guide: See `DEPLOY_TO_AGENTBEATS.md`
- AgentBeats contact: `sec+agentbeats@berkeley.edu`
- Check AgentBeats documentation for latest submission process

