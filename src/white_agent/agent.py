"""White agent implementation - the medical task agent being tested."""

import uvicorn
import dotenv
from pathlib import Path
from starlette.responses import JSONResponse
from starlette.routing import Route
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.utils import new_agent_text_message
from litellm import completion

dotenv.load_dotenv()


def load_system_prompt():
    """Load the system prompt for the white agent"""
    current_dir = Path(__file__).parent.parent.parent
    prompt_path = current_dir / "white-agent" / "system_prompt.txt"
    with open(prompt_path, "r") as f:
        return f.read()


def prepare_white_agent_card(url):
    """Prepare the agent card for the white agent"""
    skill = AgentSkill(
        id="medical_task_fulfillment",
        name="Medical Task Fulfillment",
        description="Handles medical tasks using GET/POST requests and finish() calls",
        tags=["medical", "healthcare"],
        examples=[],
    )
    card = AgentCard(
        name="medical_white_agent",
        description="Medical task agent that responds with GET/POST/finish format",
        url=url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(),
        skills=[skill],
    )
    return card


class MedicalWhiteAgentExecutor(AgentExecutor):
    """Executor for the medical white agent"""
    
    def __init__(self):
        self.ctx_id_to_messages = {}
        self.system_prompt = load_system_prompt()
    
    def reset_context(self, context_id):
        """Reset context for a new assessment"""
        if context_id in self.ctx_id_to_messages:
            del self.ctx_id_to_messages[context_id]
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute task assigned by green agent"""
        user_input = context.get_user_input()
        
        # Check if this is a reset command
        if "reset" in user_input.lower() or "ready, set" in user_input.lower():
            self.reset_context(context.context_id)
            await event_queue.enqueue_event(
                new_agent_text_message("reset", context_id=context.context_id)
            )
            return
        
        # Initialize or retrieve message history for this context
        if context.context_id not in self.ctx_id_to_messages:
            self.ctx_id_to_messages[context.context_id] = [
                {
                    "role": "system",
                    "content": self.system_prompt
                }
            ]
        
        messages = self.ctx_id_to_messages[context.context_id]
        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )
        
        # Get response from LLM
        try:
            response = completion(
                messages=messages,
                model="openai/gpt-4o",
                custom_llm_provider="openai",
                temperature=0.0,
            )
            next_message = response.choices[0].message.content.strip()
            
            # Validate that response follows GET/POST/finish format
            # The system prompt should enforce this, but we can add additional validation
            messages.append(
                {
                    "role": "assistant",
                    "content": next_message,
                }
            )
            
            await event_queue.enqueue_event(
                new_agent_text_message(
                    next_message, context_id=context.context_id
                )
            )
        except Exception as e:
            # On error, return finish with error indicator
            error_response = f"finish([-1])"
            await event_queue.enqueue_event(
                new_agent_text_message(
                    error_response, context_id=context.context_id
                )
            )
    
    async def cancel(self, context, event_queue) -> None:
        """Cancel execution"""
        raise NotImplementedError


def start_white_agent(agent_name="medical_white_agent", host=None, port=None):
    """Start the white agent server"""
    import os
    print("Starting medical white agent...")
    
    # Use HOST and AGENT_PORT environment variables if set (for AgentBeats controller)
    # Controller will automatically configure these environment variables when launching the agent
    host = host or os.getenv("HOST", "localhost")
    # Read AGENT_PORT from environment (set by controller), fallback to 9003 if not set
    port = port or int(os.getenv("AGENT_PORT", "9003"))
    
    print(f"Agent will listen on {host}:{port}")
    # Print port in a parseable format for controller (format: PORT=<port>)
    print(f"PORT={port}", flush=True)
    
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
    
    card = prepare_white_agent_card(url)
    
    request_handler = DefaultRequestHandler(
        agent_executor=MedicalWhiteAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    app = A2AStarletteApplication(
        agent_card=card,
        http_handler=request_handler,
    )
    
    # Build the Starlette app
    starlette_app = app.build()
    
    # Debug: Print registered routes
    print("Registered routes:")
    for route in starlette_app.routes:
        route_info = []
        if hasattr(route, 'path'):
            route_info.append(f"path={route.path}")
        if hasattr(route, 'methods'):
            route_info.append(f"methods={route.methods}")
        if hasattr(route, '__class__'):
            route_info.append(f"type={route.__class__.__name__}")
        print(f"  {' | '.join(route_info)}")
    
    # Add /status endpoint for health checks
    async def status_endpoint(request):
        return JSONResponse({
            "status": "ok",
            "agent": agent_name,
            "url": url,
            "version": card.version
        })
    
    # Add /port endpoint for controller to detect port
    async def port_endpoint(request):
        return JSONResponse({
            "port": port,
            "host": host
        })
    
    # Add the routes to the app
    starlette_app.routes.append(Route("/status", status_endpoint, methods=["GET"]))
    starlette_app.routes.append(Route("/port", port_endpoint, methods=["GET"]))
    
    uvicorn.run(starlette_app, host=host, port=port)

