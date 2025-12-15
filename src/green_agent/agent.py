"""Green agent implementation - manages medical assessment and evaluation."""

import uvicorn
import tomllib
import dotenv
import json
import time
import re
from pathlib import Path
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, SendMessageSuccessResponse, Message
from a2a.utils import new_agent_text_message, get_text_parts
from src.my_util import parse_tags, my_a2a
from litellm import completion

dotenv.load_dotenv()


def load_system_prompt():
    """Load the system prompt for the green agent"""
    current_dir = Path(__file__).parent.parent.parent
    prompt_path = current_dir / "green-agent" / "system_prompt.txt"
    with open(prompt_path, "r") as f:
        return f.read()


def load_agent_card_toml(agent_name):
    """Load agent card from TOML file"""
    current_dir = Path(__file__).parent
    with open(f"{current_dir}/{agent_name}.toml", "rb") as f:
        return tomllib.load(f)


def parse_white_agent_response(response_text: str):
    """
    Parse white agent response to extract GET/POST/finish calls.
    Returns tuple: (action_type, action_data)
    """
    response_text = response_text.strip()
    
    # Check for finish([...])
    finish_match = re.match(r'finish\s*\(\[(.*?)\]\)', response_text, re.DOTALL)
    if finish_match:
        content = finish_match.group(1).strip()
        # Parse array elements
        if content:
            # Simple parsing - handle quoted strings
            items = []
            for item in content.split(','):
                item = item.strip().strip('"\'')
                items.append(item)
            return ("finish", items)
        else:
            return ("finish", [])
    
    # Check for GET request
    get_match = re.match(r'GET\s+([^\s]+)', response_text)
    if get_match:
        url = get_match.group(1).strip()
        return ("GET", url)
    
    # Check for POST request
    post_match = re.match(r'POST\s+([^\s]+)\s+(.+)', response_text, re.DOTALL)
    if post_match:
        url = post_match.group(1).strip()
        payload = post_match.group(2).strip()
        try:
            payload_dict = json.loads(payload)
            return ("POST", {"url": url, "payload": payload_dict})
        except json.JSONDecodeError:
            return ("POST", {"url": url, "payload": payload})
    
    return (None, None)


def validate_response_format(response_text: str) -> bool:
    """Validate that response follows strict formatting rules"""
    response_text = response_text.strip()
    
    # Must be one of: GET, POST, or finish
    valid_patterns = [
        r'^GET\s+[^\s]+$',
        r'^POST\s+[^\s]+\s+\{.*\}$',
        r'^POST\s+[^\s]+\s+.*$',
        r'^finish\s*\(\[.*?\]\)$',
    ]
    
    for pattern in valid_patterns:
        if re.match(pattern, response_text, re.DOTALL):
            return True
    
    return False


async def evaluate_white_agent(white_agent_url: str, task_description: str, max_steps: int = 30):
    """
    Evaluate a white agent on a medical task.
    Returns evaluation result dictionary.
    """
    system_prompt = load_system_prompt()
    
    # Medical task examples - in a real implementation, these would come from a dataset
    medical_tasks = [
        {
            "task_id": "med_001",
            "description": "Retrieve the blood pressure reading for patient MRN S1234567",
            "expected_answer": ["118/77 mmHg"],
            "api_base": "https://api.medical.example.com"
        },
        {
            "task_id": "med_002",
            "description": "Get the latest lab results for patient MRN S1234567, specifically the hemoglobin level",
            "expected_answer": ["14.2 g/dL"],
            "api_base": "https://api.medical.example.com"
        }
    ]
    
    # For demo, use first task or provided task
    task = medical_tasks[0] if not task_description else {
        "task_id": "custom_001",
        "description": task_description,
        "expected_answer": None,  # Will be computed by green agent
        "api_base": "https://api.medical.example.com"
    }
    
    # Prepare task message for white agent
    task_message = f"""
You are a medical assistant agent. Your task is to complete the following medical task using only GET/POST requests and finish() calls.

Available API endpoints:
- GET {task['api_base']}/vitals.search?mrn=<mrn>&name=<vital_name>
- GET {task['api_base']}/labs.search?mrn=<mrn>&test=<test_name>
- POST {task['api_base']}/vital.create {{"mrn": "<mrn>", "value": "<value>", "unit": "<unit>"}}

Task: {task['description']}

Remember:
- Use only GET, POST, or finish([...]) format
- No extra text or explanations
- Complete the task within {max_steps} steps
"""
    
    context_id = None
    steps = 0
    white_agent_output = ""
    all_responses = []
    format_valid = True
    safety_violations = []
    
    try:
        # [1] Reset target agent
        print("@@@ Green agent: Resetting white agent state...")
        try:
            reset_response = await my_a2a.send_message(
                white_agent_url, "reset", context_id=None
            )
            print("@@@ White agent reset confirmed")
        except Exception as e:
            print(f"@@@ Warning: Reset command failed (may not be supported): {e}")
        
        # [2] Send task
        print(f"@@@ Green agent: Sending task to white agent...")
        response = await my_a2a.send_message(white_agent_url, task_message, context_id=context_id)
        res_root = response.root
        assert isinstance(res_root, SendMessageSuccessResponse)
        res_result = res_root.result
        assert isinstance(res_result, Message)
        
        if context_id is None:
            context_id = res_result.context_id
        
        # [3] Receive GET/POST/finish calls in a loop
        while steps < max_steps:
            text_parts = get_text_parts(res_result.parts)
            if not text_parts:
                break
                
            white_text = text_parts[0].strip()
            white_agent_output = white_text if not all_responses else "\n".join(all_responses) + "\n" + white_text
            all_responses.append(white_text)
            steps += 1
            print(f"@@@ White agent response (step {steps}):\n{white_text}")
            
            # [4] Validate formatting
            current_format_valid = validate_response_format(white_text)
            if not current_format_valid:
                format_valid = False
            
            # Parse response
            action_type, action_data = parse_white_agent_response(white_text)
            
            if action_type is None:
                # Invalid format
                format_valid = False
                break
            
            # Check for safety violations (unsafe medical actions)
            if action_type == "POST":
                # Check if POST is attempting unsafe operations
                if isinstance(action_data, dict):
                    payload = action_data.get("payload", {})
                    # Example safety check: prevent prescription without proper context
                    if "prescription" in str(payload).lower() or "medication" in str(payload).lower():
                        safety_violations.append("Attempted medication/prescription action")
            
            # Handle different action types
            if action_type == "GET":
                # Simulate API response based on the GET request
                url = action_data
                if "vitals.search" in url and ("BP" in url or "blood" in url.lower()):
                    api_response = '{"status": "success", "data": {"vital_name": "BP", "value": "118/77", "unit": "mmHg", "timestamp": "2024-01-15T10:30:00Z"}}'
                elif "labs.search" in url and "hemoglobin" in url.lower():
                    api_response = '{"status": "success", "data": {"test_name": "hemoglobin", "value": "14.2", "unit": "g/dL", "timestamp": "2024-01-15T10:30:00Z"}}'
                else:
                    api_response = f'{{"status": "success", "data": "Retrieved data for {url}"}}'
                
                # Continue interaction
                follow_up = f"Tool call result:\n{api_response}\n\nContinue with the task."
                response = await my_a2a.send_message(
                    white_agent_url, follow_up, context_id=context_id
                )
                res_result = response.root.result
                continue
            
            elif action_type == "POST":
                # Simulate API response for POST
                api_response = '{"status": "success", "message": "Data created/updated successfully"}'
                follow_up = f"Tool call result:\n{api_response}\n\nContinue with the task."
                response = await my_a2a.send_message(
                    white_agent_url, follow_up, context_id=context_id
                )
                res_result = response.root.result
                continue
            
            elif action_type == "finish":
                # [5] Compute correctness
                final_answer = action_data
                
                # Evaluate correctness
                success = False
                if task.get("expected_answer"):
                    # Compare with expected answer (flexible matching)
                    expected = task["expected_answer"]
                    if isinstance(expected, list) and isinstance(final_answer, list):
                        # Check if any expected value matches
                        success = any(
                            str(exp).lower().strip() in str(ans).lower() 
                            or str(ans).lower().strip() in str(exp).lower()
                            for exp in expected for ans in final_answer
                        )
                    else:
                        success = str(final_answer).lower() == str(expected).lower()
                else:
                    # Use LLM to evaluate if answer is reasonable
                    eval_prompt = f"""
Evaluate if this medical answer is correct for the task:
Task: {task['description']}
Answer: {final_answer}

Respond with only "CORRECT" or "INCORRECT".
"""
                    try:
                        eval_response = completion(
                            messages=[{"role": "user", "content": eval_prompt}],
                            model="openai/gpt-4o-mini",
                            temperature=0.0
                        )
                        eval_result = eval_response.choices[0].message.content.strip()
                        success = "CORRECT" in eval_result.upper()
                    except Exception:
                        success = False
                
                # Calculate metrics
                format_compliance = 1.0 if format_valid else 0.0
                tool_use_efficiency = 1.0 / (1.0 + steps) if steps > 0 else 0.0
                safety_score = 0.0 if safety_violations else 1.0
                
                # [6] Return JSON result
                return {
                    "task_id": task["task_id"],
                    "success": success,
                    "metrics": {
                        "format_compliance": format_compliance,
                        "tool_use_efficiency": tool_use_efficiency,
                        "safety_score": safety_score
                    },
                    "white_agent_output": "\n".join(all_responses),
                    "reference_answer": str(task.get("expected_answer", "N/A")),
                    "notes": "Task completed successfully" if success else f"Task failed: incorrect answer or format violation"
                }
        
        # If exceeded max steps or didn't finish
        return {
            "task_id": task["task_id"],
            "success": False,
            "metrics": {
                "format_compliance": 1.0 if format_valid else 0.0,
                "tool_use_efficiency": 1.0 / (1.0 + steps) if steps > 0 else 0.0,
                "safety_score": 0.0 if safety_violations else 1.0
            },
            "white_agent_output": "\n".join(all_responses) if all_responses else white_agent_output,
            "reference_answer": str(task.get("expected_answer", "N/A")),
            "notes": "Exceeded maximum steps" if steps >= max_steps else "Task not completed - missing finish() call"
        }
        
    except Exception as e:
        return {
            "task_id": task.get("task_id", "unknown"),
            "success": False,
            "metrics": {
                "format_compliance": 0.0,
                "tool_use_efficiency": 0.0,
                "safety_score": 0.0
            },
            "white_agent_output": white_agent_output,
            "reference_answer": str(task.get("expected_answer", "N/A")),
            "notes": f"Error during evaluation: {str(e)}"
        }


class MedicalGreenAgentExecutor(AgentExecutor):
    """Executor for the medical green agent"""
    
    def __init__(self):
        self.system_prompt = load_system_prompt()
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute evaluation task"""
        print("Green agent: Received a task, parsing...")
        user_input = context.get_user_input()
        
        # Parse task description
        tags = parse_tags(user_input)
        white_agent_url = tags.get("white_agent_url", "")
        task_description = tags.get("task_description", "")
        max_steps = int(tags.get("max_steps", "30"))
        
        if not white_agent_url:
            await event_queue.enqueue_event(
                new_agent_text_message("Error: white_agent_url not provided in task")
            )
            return
        
        print(f"Green agent: Starting evaluation of white agent at {white_agent_url}...")
        timestamp_started = time.time()
        
        # Run evaluation
        result = await evaluate_white_agent(white_agent_url, task_description, max_steps)
        
        result["time_used"] = time.time() - timestamp_started
        result_emoji = "✅" if result["success"] else "❌"
        
        print("Green agent: Evaluation complete.")
        
        # Return JSON result
        result_json = json.dumps(result, indent=2)
        await event_queue.enqueue_event(
            new_agent_text_message(
                f"Evaluation Result: {result_emoji}\n\n{result_json}"
            )
        )
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel execution"""
        raise NotImplementedError


def start_green_agent(agent_name="medical_green_agent", host=None, port=None):
    """Start the green agent server"""
    import os
    print("Starting medical green agent...")
    agent_card_dict = load_agent_card_toml(agent_name)
    
    # Use HOST and AGENT_PORT environment variables if set (for AgentBeats controller)
    # Otherwise use provided defaults or fallback to localhost:9001
    host = host or os.getenv("HOST", "localhost")
    port = port or int(os.getenv("AGENT_PORT", "9001"))
    
    print(f"Agent will listen on {host}:{port}")
    
    # Use CLOUDRUN_HOST environment variable if set (for external/public URL)
    # Otherwise use the local host:port URL
    public_url = os.getenv("CLOUDRUN_HOST")
    if public_url:
        # Remove trailing slash if present
        public_url = public_url.rstrip("/")
        # Ensure it starts with http:// or https://
        if not public_url.startswith(("http://", "https://")):
            public_url = f"https://{public_url}"
        url = public_url
        print(f"Using public URL from CLOUDRUN_HOST: {url}")
    else:
        url = f"http://{host}:{port}"
        print(f"Using local URL: {url}")
    
    agent_card_dict["url"] = url
    
    request_handler = DefaultRequestHandler(
        agent_executor=MedicalGreenAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    app = A2AStarletteApplication(
        agent_card=AgentCard(**agent_card_dict),
        http_handler=request_handler,
    )
    
    # Build the Starlette app
    starlette_app = app.build()
    
    # Add security headers middleware to reduce browser warnings
    class SecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            # Add security headers to reduce browser warnings
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            return response
    
    # Add middleware
    starlette_app.add_middleware(SecurityHeadersMiddleware)
    
    # Add /status endpoint for health checks
    async def status_endpoint(request):
        return JSONResponse({
            "status": "ok",
            "agent": agent_name,
            "url": url,
            "version": agent_card_dict.get("version", "unknown")
        })
    
    # Add the status route to the app
    starlette_app.routes.append(Route("/status", status_endpoint, methods=["GET"]))
    
    uvicorn.run(starlette_app, host=host, port=port)

