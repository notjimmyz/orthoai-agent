"""Test script to verify Cloudflare tunnel setup for green agent."""

import asyncio
from src.my_util import my_a2a
from a2a.utils import get_text_parts

async def test_cloudflare_green_agent():
    """Test the green agent via Cloudflare tunnel"""
    
    # Cloudflare tunnel URL for green agent
    green_url = "https://belts-suppliers-documents-copper.trycloudflare.com"
    
    # White agent running locally
    white_url = "http://localhost:9002"
    
    print("Testing Cloudflare tunnel setup...")
    print(f"Green agent URL: {green_url}")
    print(f"White agent URL: {white_url}")
    print()
    
    # First, check if green agent is accessible
    print("Checking if green agent is accessible...")
    try:
        is_ready = await my_a2a.wait_agent_ready(green_url, timeout=10)
        if is_ready:
            print("✅ Green agent is accessible via Cloudflare tunnel!")
        else:
            print("❌ Green agent not ready. Make sure:")
            print("   1. Green agent is running: python main.py green")
            print("   2. Cloudflare tunnel is active: cloudflared tunnel --url http://localhost:9001")
            return
    except Exception as e:
        print(f"❌ Error checking green agent: {e}")
        return
    
    print()
    print("Sending evaluation task to green agent...")
    
    # Prepare task message
    task_text = f"""
Your task is to evaluate the medical agent located at:
<white_agent_url>
{white_url}/
</white_agent_url>
You should test it with the following medical task:
<task_description>
Retrieve the blood pressure reading for patient MRN S1234567
</task_description>
<max_steps>
30
</max_steps>
    """
    
    try:
        # Send message to green agent
        response = await my_a2a.send_message(green_url, task_text)
        
        # Extract text from response
        text_parts = get_text_parts(response.root.result.parts)
        
        if text_parts:
            print("✅ Response received from green agent:")
            print("-" * 60)
            print(text_parts[0])
            print("-" * 60)
        else:
            print("Response received (no text parts):")
            print(response)
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("Cloudflare Tunnel Test")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("1. White agent must be running: python main.py white")
    print("2. Green agent must be running: python main.py green")
    print("3. Cloudflare tunnel must be active")
    print()
    print("=" * 60)
    print()
    
    asyncio.run(test_cloudflare_green_agent())


