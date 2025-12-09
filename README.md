# OrthoAI Agent - Medical Context Agents for AgentBeats

This project implements medical context agents for the AgentBeats evaluation platform, following the A2A (Agent-to-Agent) protocol standard.

## Overview

This implementation includes:

- **Green Agent (Medical Evaluation Agent)**: Evaluates white agents on medical tasks, assigns tasks, collects responses, and grades outcomes using objective metrics.
- **White Agent (Medical Task Agent)**: Completes medical tasks by responding with strict GET/POST/finish format, following A2A protocol.

Both agents are designed for medical/healthcare contexts and follow the AgentBeats evaluation framework.

## Project Structure

```
orthoai-agent/
├── src/
│   ├── green_agent/
│   │   ├── __init__.py
│   │   ├── agent.py              # Green agent implementation
│   │   └── medical_green_agent.toml  # Agent card configuration
│   ├── white_agent/
│   │   ├── __init__.py
│   │   └── agent.py              # White agent implementation
│   ├── my_util/
│   │   └── __init__.py           # A2A utility functions
│   ├── launcher.py               # Evaluation workflow launcher
│   └── __init__.py
├── green-agent/
│   └── system_prompt.txt         # Green agent system prompt
├── white-agent/
│   └── system_prompt.txt         # White agent system prompt
├── main.py                       # CLI entry point
└── pyproject.toml                # Project dependencies

```

## Installation

1. Install dependencies using `uv` (recommended) or `pip`:

```bash
# Using uv
uv pip install -e .

# Or using pip
pip install -e .
```

2. Set up environment variables (create a `.env` file):

```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Starting Agents Individually

**Start the Green Agent (evaluator):**
```bash
python main.py green
```
The green agent will start on `http://localhost:9001`

**Start the White Agent (task executor):**
```bash
python main.py white
```
The white agent will start on `http://localhost:9002`

### Running Complete Evaluation

To launch both agents and run a complete evaluation:

```bash
python main.py launch
```

This will:
1. Start the green agent
2. Start the white agent
3. Send an evaluation task to the green agent
4. Display the evaluation results
5. Terminate both agents

## Agent Behavior

### Green Agent

The green agent:
- Receives evaluation requests via A2A protocol
- Generates medical tasks from a benchmark dataset
- Sends tasks to white agents
- Validates white agent responses (GET/POST/finish format)
- Tracks interaction steps and verifies tool calls
- Computes metrics: success, format_compliance, tool_use_efficiency, safety_score
- Returns evaluation results in JSON format

### White Agent

The white agent:
- Responds only with strict formatting:
  - `GET {url}?param1=value1&param2=value2`
  - `POST {url} {JSON_payload}`
  - `finish([answer1, answer2, ...])`
- No extra text, natural language, or explanations
- Completes medical tasks using available API endpoints
- Maintains safety constraints (no medical advice, no prescriptions unless explicitly allowed)

## Medical Task Examples

The agents are designed to handle medical tasks such as:
- Retrieving patient vital signs (blood pressure, heart rate, etc.)
- Querying lab results
- Accessing patient records
- Managing medical data (with proper safety checks)

## Evaluation Metrics

The green agent evaluates white agents on:

- **success**: Boolean indicating if the task was completed correctly
- **format_compliance**: Whether responses follow strict GET/POST/finish format
- **tool_use_efficiency**: Efficiency metric based on number of steps (1 / (1 + steps))
- **safety_score**: Whether any unsafe medical actions were attempted

## A2A Protocol Compliance

Both agents follow the A2A (Agent-to-Agent) protocol standard:
- Implement agent cards (self-description)
- Support A2A message format
- Handle context IDs for conversation tracking
- Support task isolation

## Development

The implementation follows the structure of `agentify-example-tau-bench-main` but is adapted for medical contexts. Key differences:

- Medical-specific tasks and API endpoints
- Healthcare safety constraints
- Medical terminology and workflows
- Evaluation metrics tailored for medical task completion

## System Prompts

- **Green Agent**: Located in `green-agent/system_prompt.txt` - defines evaluation responsibilities and constraints
- **White Agent**: Located in `white-agent/system_prompt.txt` - defines strict response formatting and medical task behavior

## License

This project is part of the AgentBeats evaluation platform.
