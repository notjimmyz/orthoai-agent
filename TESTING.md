# Testing Guide for OrthoAI Medical Agents

This guide explains how to test the medical green and white agents.

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -e .
   # or
   uv pip install -e .
   ```

2. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Testing Methods

### Method 1: Quick Test (Recommended)

Run the complete evaluation workflow with a single command:

```bash
python main.py launch
```

This will:
- Start the green agent on `http://localhost:9001`
- Start the white agent on `http://localhost:9002`
- Send an evaluation task to the green agent
- Display the evaluation results
- Automatically terminate both agents

**Expected Output:**
```
Launching medical green agent...
Green agent is ready.
Launching medical white agent...
White agent is ready.
Sending evaluation task to green agent...
Task description:
...
@@@ Green agent: Resetting white agent state...
@@@ Green agent: Sending task to white agent...
@@@ White agent response (step 1):
GET https://api.medical.example.com/vitals.search?mrn=S1234567&name=BP
...
Evaluation Result: ✅
{
  "task_id": "med_001",
  "success": true,
  "metrics": {
    "format_compliance": 1.0,
    "tool_use_efficiency": 0.5,
    "safety_score": 1.0
  },
  ...
}
```

### Method 2: Manual Testing (Two Terminals)

**Terminal 1 - Start Green Agent:**
```bash
python main.py green
```

You should see:
```
Starting medical green agent...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:9001
```

**Terminal 2 - Start White Agent:**
```bash
python main.py white
```

You should see:
```
Starting medical white agent...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:9002
```

**Terminal 3 - Send Test Request:**

You can test by sending a message directly to the green agent using curl or Python:

```python
import asyncio
from src.my_util import my_a2a

async def test():
    green_url = "http://localhost:9001"
    task_text = """
Your task is to evaluate the medical agent located at:
<white_agent_url>
http://localhost:9002/
</white_agent_url>
You should test it with the following medical task:
<task_description>
Retrieve the blood pressure reading for patient MRN S1234567
</task_description>
<max_steps>
30
</max_steps>
    """
    response = await my_a2a.send_message(green_url, task_text)
    print(response)

asyncio.run(test())
```

### Method 3: Test Individual Components

#### Test White Agent Directly

You can test the white agent by sending it a task directly:

```python
import asyncio
from src.my_util import my_a2a

async def test_white_agent():
    white_url = "http://localhost:9002"
    
    # Start white agent first: python main.py white
    
    task = """
You are a medical assistant agent. Your task is to complete the following medical task using only GET/POST requests and finish() calls.

Available API endpoints:
- GET https://api.medical.example.com/vitals.search?mrn=<mrn>&name=<vital_name>
- GET https://api.medical.example.com/labs.search?mrn=<mrn>&test=<test_name>

Task: Retrieve the blood pressure reading for patient MRN S1234567

Remember:
- Use only GET, POST, or finish([...]) format
- No extra text or explanations
"""
    
    response = await my_a2a.send_message(white_url, task)
    print("White agent response:", response.root.result.parts)

asyncio.run(test_white_agent())
```

#### Test Green Agent Evaluation Logic

You can test the green agent's evaluation function directly:

```python
import asyncio
from src.green_agent.agent import evaluate_white_agent

async def test():
    white_url = "http://localhost:9002"  # Make sure white agent is running
    result = await evaluate_white_agent(
        white_url, 
        "Retrieve the blood pressure reading for patient MRN S1234567",
        max_steps=30
    )
    print(result)

asyncio.run(test())
```

## Verification Checklist

After running tests, verify:

- [ ] Both agents start without errors
- [ ] Green agent can receive tasks
- [ ] White agent responds with GET/POST/finish format
- [ ] Green agent correctly parses white agent responses
- [ ] Evaluation metrics are calculated correctly
- [ ] JSON results are returned in the expected format
- [ ] Reset functionality works (white agent clears context)

## Common Issues

### Issue: "Module not found" errors
**Solution:** Make sure you're in the project root and dependencies are installed:
```bash
pip install -e .
```

### Issue: "OPENAI_API_KEY not found"
**Solution:** Create a `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your_key_here" > .env
```

### Issue: Port already in use
**Solution:** Kill the process using the port or change ports in the code:
```bash
# Find and kill process on port 9001
lsof -ti:9001 | xargs kill -9
```

### Issue: White agent not responding correctly
**Solution:** Check that:
1. The system prompt file exists at `white-agent/system_prompt.txt`
2. The OpenAI API key is valid
3. The white agent is receiving messages (check logs)

### Issue: Green agent can't parse responses
**Solution:** Verify the white agent is returning strict format:
- `GET {url}`
- `POST {url} {json}`
- `finish([...])`

No extra text should be present.

## Debugging Tips

1. **Enable verbose logging:** Add print statements in the agent code
2. **Check agent cards:** Visit `http://localhost:9001/.well-known/agent-card` and `http://localhost:9002/.well-known/agent-card` to verify agents are running
3. **Test with curl:**
   ```bash
   curl http://localhost:9001/.well-known/agent-card
   curl http://localhost:9002/.well-known/agent-card
   ```

## Expected Behavior

### White Agent
- Should respond ONLY with GET/POST/finish format
- Should NOT include any explanatory text
- Should complete tasks within the step limit
- Should handle reset commands

### Green Agent
- Should reset white agent before evaluation
- Should send clear task descriptions
- Should validate response formats
- Should calculate metrics correctly
- Should return JSON results

## Next Steps

Once basic testing passes:
1. Test with different medical tasks
2. Test edge cases (invalid formats, timeouts, etc.)
3. Test multi-step interactions
4. Test safety constraint violations
5. Integrate with actual medical API endpoints (if available)

