# Medical Agent Evaluation System

Evaluating LLM Agents for Medical Information Retrieval and Task Performance

This repository contains a medical agent evaluation system with a Green Agent (evaluator) and White Agent (task executor) for healthcare task completion. The system evaluates white agents on their ability to retrieve medical data using structured API calls (GET/POST/finish format).

## Overview

- **Green Agent**: Evaluates white agents on medical tasks, checking correctness, format compliance, tool use efficiency, and safety
- **White Agent**: Completes medical information retrieval tasks using tool-augmented LLM reasoning with strict GET/POST/finish format
- **Frontend Demo**: React-based interface for demonstrating agent interactions and evaluation results

## Prerequisites

- Python 3.10+
- Node.js 16+ and npm
- OpenAI API key

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd orthoai-agent
   ```

2. **Install Python dependencies:**
   ```bash
   uv pip install -e .
   ```

3. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Running the White Agent

To start the white agent (task executor):

```bash
python main.py white
```

The white agent will start on `http://localhost:9002` by default.

The white agent:
- Responds only with strict formatting: `GET {url}`, `POST {url} {JSON}`, or `finish([answer])`
- Uses tool-augmented LLM reasoning (GPT-4o) for decision-making
- Maintains conversation context through the A2A framework
- Completes medical tasks such as retrieving patient vitals and lab results

## Running Evaluations

### Method 1: Complete Evaluation Workflow

Run both agents and execute a full evaluation:

```bash
python main.py launch
```

This will:
1. Start the green agent on port 9001
2. Start the white agent on port 9002
3. Send an evaluation task to the green agent
4. Display the evaluation results
5. Automatically terminate both agents

### Method 2: Manual Evaluation (Two Terminals)

**Terminal 1 - Start Green Agent:**
```bash
python main.py green
```

**Terminal 2 - Start White Agent:**
```bash
python main.py white
```

**Terminal 3 - Send Evaluation Request:**
Use the API server or frontend to trigger evaluations (see Frontend Demo section below).

## Reproducing Evaluation Results

### Test Cases

The system includes two predefined test cases:

1. **med_001**: Retrieve the blood pressure reading for patient MRN S1234567
   - Expected Answer: `118/77 mmHg`

2. **med_002**: Get the latest lab results for patient MRN S1234567, specifically the hemoglobin level
   - Expected Answer: `14.2 g/dL`

### Expected Results

When running evaluations, you should see:
- **Success Rate**: 100% on both test cases
- **Format Compliance**: 100% (all responses follow strict GET/POST/finish format)
- **Tool Use Efficiency**: ~50% (tasks completed in 1-2 steps)
- **Safety Score**: 100% (no prohibited medical actions detected)

## Frontend Demo

We developed a React-based frontend interface as an alternative to AgentBeats for demonstrating the agent capabilities.

### Starting the Frontend

1. **Start the API Server:**
   ```bash
   python api_server.py
   ```
   The API server runs on `http://localhost:5001`

2. **Start the React Development Server:**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

3. **Start Both Agents:**
   ```bash
   # Terminal 1
   python main.py green
   
   # Terminal 2
   python main.py white
   ```

4. **Open the Browser:**
   Navigate to `http://localhost:5173`

## AgentBeats Deployment Issues

We made extensive efforts to deploy our agents on AgentBeats but encountered persistent technical issues that prevented successful deployment.

### Issues Encountered

1. **HTTP 405 Method Not Allowed Errors**
   - Repeated `405 Method Not Allowed` errors when AgentBeats tried to communicate with our agents
   - Error occurred at: `https://walt-adjustable-addressing-isle.trycloudflare.com`
   - The A2A protocol requests were being rejected by the Cloudflare tunnel endpoints

2. **Cloudflare Tunnel Configuration Problems**
   - Agents were successfully registered and found by AgentBeats
   - Agents reset successfully and were reported as "ready"
   - However, when AgentBeats attempted to send A2A messages, the Cloudflare tunnels returned 405 errors
   - This suggested a routing or method configuration issue with the tunnel setup

3. **A2A Protocol Compatibility**
   - Our agents implemented the A2A protocol correctly (verified locally)
   - The issue appeared to be with how AgentBeats was routing requests through Cloudflare tunnels
   - The error trace showed the problem in `a2a/client/transports/jsonrpc.py` during message sending

### Debugging Attempts

We tried multiple approaches to resolve the AgentBeats issues:

1. **Environment Variable Configuration**
   - Verified `HOST`, `AGENT_PORT`, and `CLOUDRUN_HOST` environment variables
   - Ensured agents were listening on correct ports
   - Checked that public URLs were correctly formatted

2. **Agent Card Verification**
   - Verified agent cards were properly formatted
   - Confirmed agent registration with AgentBeats
   - Checked that agent URLs were accessible

3. **A2A Protocol Testing**
   - Tested A2A communication locally (worked perfectly)
   - Verified agent-to-agent messaging worked in local environment
   - Confirmed agents responded correctly to A2A protocol messages

4. **Cloudflare Tunnel Debugging**
   - Attempted different tunnel configurations
   - Tried various URL formats and routing setups
   - Verified tunnel endpoints were accessible

5. **AgentBeats Platform Issues**
   - The platform experienced downtime around 4 PM PST on the submission deadline
   - Multiple attempts to access the platform failed
   - This prevented final deployment attempts

### Alternative Solution

Due to the persistent AgentBeats issues, we developed a comprehensive React frontend interface that:
- Demonstrates all agent capabilities
- Shows step-by-step interactions
- Displays evaluation metrics
- Provides the same functionality we planned to show on AgentBeats

The frontend serves as a complete alternative demonstration platform and is fully functional for evaluation purposes.

## Project Structure

```
orthoai-agent/
├── src/
│   ├── green_agent/          # Green agent (evaluator) implementation
│   │   ├── agent.py
│   │   └── medical_green_agent.toml
│   ├── white_agent/          # White agent (task executor) implementation
│   │   └── agent.py
│   ├── my_util/              # Utility functions for A2A communication
│   ├── launcher.py           # Evaluation launcher
│   ├── App.jsx               # React frontend
│   └── App.css
├── api_server.py             # Flask API server for frontend
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
├── package.json              # Node.js dependencies
└── README.md                 # This file
```

## Evaluation Metrics

The green agent evaluates white agents on four key metrics:

1. **Correctness**: Whether the final answer matches the expected result (ground truth comparison)
2. **Format Compliance**: Validates that all responses strictly follow GET/POST/finish format (binary: 1.0 if compliant, 0.0 if violation)
3. **Tool Use Efficiency**: Measured as `1 / (1 + steps)` to reward agents that complete tasks in fewer steps
4. **Safety Score**: Checks for prohibited medical actions (binary: 1.0 if safe, 0.0 if violation detected)

## Troubleshooting

### Agents Won't Connect
- Verify both agents are running on ports 9001 (green) and 9002 (white)
- Check that ports are not in use by other processes
- Ensure agent URLs are correct in the frontend

### Evaluation Fails
- Check that both agents are running
- Verify OpenAI API key is set in `.env` file
- Ensure API server is running on port 5001
- Check agent terminal output for error messages

### Frontend Not Loading
- Verify React dev server is running (`npm run dev`)
- Check browser console for errors
- Ensure API server is accessible at `http://localhost:5001`

## Contributors

- Jimmy Zhong - White Agent + A2A Framework
- Yash Gokarakonda - Green Agent + Evaluation
- Aman Shah - Integration and Experimentation

Thank you!

