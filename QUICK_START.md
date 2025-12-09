# Quick Start - Testing the Medical Agents

## Fastest Way to Test

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Set up API key:**
   Create `.env` file:
   ```bash
   OPENAI_API_KEY=your_key_here
   ```

3. **Run the test:**
   ```bash
   python main.py launch
   ```

That's it! This will start both agents, run an evaluation, and show you the results.

## What You'll See

The test will:
- ✅ Start green agent (evaluator) on port 9001
- ✅ Start white agent (task executor) on port 9002  
- ✅ Send a medical task: "Retrieve blood pressure for patient MRN S1234567"
- ✅ White agent responds with: `GET https://api.medical.example.com/vitals.search?...`
- ✅ Green agent evaluates and returns JSON with metrics

## Expected Output

```
Launching medical green agent...
Green agent is ready.
Launching medical white agent...
White agent is ready.
Sending evaluation task to green agent...
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
  "white_agent_output": "...",
  "reference_answer": "['118/77 mmHg']",
  "notes": "Task completed successfully"
}
```

## Troubleshooting

- **"Module not found"**: Run `pip install -e .` from project root
- **"API key error"**: Check your `.env` file has `OPENAI_API_KEY=...`
- **Port in use**: Kill processes on ports 9001/9002 or change ports in code

For more detailed testing options, see `TESTING.md`.

