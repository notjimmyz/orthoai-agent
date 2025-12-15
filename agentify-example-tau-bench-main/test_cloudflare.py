"""Test script to verify Cloudflare tunnel setup for tau-bench green agent."""

import asyncio
import json
from src.my_util.my_a2a import send_message, wait_agent_ready
from a2a.utils import get_text_parts

async def test_cloudflare_green_agent():
    """Test the green agent via Cloudflare tunnel"""
    
    # Cloudflare tunnel URL for green agent
    green_url = "https://being-stock-struck-acceptable.trycloudflare.com"
    
    # White agent running locally
    white_url = "http://localhost:9002"
    
    print("=" * 70)
    print("Cloudflare Tunnel Test - Tau-Bench Green Agent")
    print("=" * 70)
    print()
    print(f"Green agent URL: {green_url}")
    print(f"White agent URL: {white_url}")
    print()
    
    # Step 1: Check if green agent is accessible
    print("Step 1: Checking if green agent is accessible...")
    try:
        is_ready = await wait_agent_ready(green_url, timeout=10)
        if is_ready:
            print("✅ Green agent is accessible via Cloudflare tunnel!")
        else:
            print("❌ Green agent not ready. Make sure:")
            print("   1. Green agent is running: uv run python main.py green")
            print("   2. Cloudflare tunnel is active: cloudflared tunnel --url http://localhost:9001")
            return False
    except Exception as e:
        print(f"❌ Error checking green agent: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("Step 2: Sending evaluation task to green agent...")
    print("-" * 70)
    
    # Prepare task message (same format as launcher.py)
    task_config = {
        "env": "retail",
        "user_strategy": "llm",
        "user_model": "openai/gpt-4o",
        "user_provider": "openai",
        "task_split": "test",
        "task_ids": [1],
    }
    
    task_text = f"""
Your task is to instantiate tau-bench to test the agent located at:
<white_agent_url>
{white_url}/
</white_agent_url>
You should use the following env configuration:
<env_config>
{json.dumps(task_config, indent=2)}
</env_config>
    """
    
    print("Task configuration:")
    print(json.dumps(task_config, indent=2))
    print()
    print("Sending task...")
    
    try:
        # Send message to green agent
        response = await send_message(green_url, task_text)
        
        # Extract text from response
        text_parts = get_text_parts(response.root.result.parts)
        
        if text_parts:
            print("✅ Response received from green agent:")
            print("-" * 70)
            print(text_parts[0])
            print("-" * 70)
            print()
            print("✅ Test completed successfully!")
            return True
        else:
            print("⚠️  Response received but no text parts found:")
            print(response)
            return True
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    print("Prerequisites:")
    print("1. White agent must be running: uv run python main.py white")
    print("2. Green agent must be running: uv run python main.py green")
    print("3. Cloudflare tunnel must be active")
    print()
    print("=" * 70)
    print()
    
    success = asyncio.run(test_cloudflare_green_agent())
    
    print()
    print("=" * 70)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed. Check the output above for details.")
    print("=" * 70)

