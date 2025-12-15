"""Quick script to verify the agent card shows the correct URL."""

import asyncio
import sys
from src.my_util.my_a2a import get_agent_card

async def verify_agent_card(url):
    """Check what URL is published in the agent card"""
    print(f"Fetching agent card from: {url}")
    print("-" * 70)
    
    try:
        card = await get_agent_card(url)
        if card:
            print("✅ Agent card retrieved successfully!")
            print()
            print("Agent Card Details:")
            print(f"  Name: {card.name}")
            print(f"  URL:  {card.url}")
            print(f"  Description: {card.description}")
            print()
            
            if "trycloudflare.com" in card.url or "cloudflare" in card.url.lower():
                print("✅ SUCCESS: Agent card shows Cloudflare tunnel URL!")
                print(f"   External platforms can access: {card.url}")
            elif "localhost" in card.url:
                print("⚠️  WARNING: Agent card still shows localhost URL")
                print("   Make sure CLOUDRUN_HOST environment variable is set")
                print("   and restart the agent")
            else:
                print(f"   Published URL: {card.url}")
            
            return True
        else:
            print("❌ Failed to retrieve agent card")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Default to localhost, but can pass URL as argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "http://localhost:9001"
    
    print("=" * 70)
    print("Agent Card Verification")
    print("=" * 70)
    print()
    
    success = asyncio.run(verify_agent_card(url))
    
    print()
    print("=" * 70)
    if success:
        print("Verification complete!")
    else:
        print("Verification failed!")
    print("=" * 70)

