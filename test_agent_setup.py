#!/usr/bin/env python3
"""Test script to verify agent setup and endpoints."""

import asyncio
import httpx
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_agent_card(url, agent_name):
    """Test if agent card endpoint is accessible"""
    print(f"\n{'='*70}")
    print(f"Testing {agent_name} Agent Card")
    print(f"{'='*70}")
    print(f"URL: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test agent card endpoint
            card_url = f"{url}/.well-known/agent-card.json"
            print(f"\n1. Testing agent card endpoint: {card_url}")
            response = await client.get(card_url)
            
            if response.status_code == 200:
                print("   ✅ Agent card endpoint accessible")
                card_data = response.json()
                print(f"   Agent Name: {card_data.get('name', 'N/A')}")
                print(f"   Agent URL: {card_data.get('url', 'N/A')}")
                print(f"   Version: {card_data.get('version', 'N/A')}")
                return True
            else:
                print(f"   ❌ Agent card endpoint returned status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
    except httpx.TimeoutException:
        print("   ❌ Timeout: Agent not responding")
        return False
    except httpx.ConnectError:
        print("   ❌ Connection Error: Cannot connect to agent")
        print("   Make sure the agent is running")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_status_endpoint(url, agent_name):
    """Test if status endpoint is accessible"""
    print(f"\n2. Testing status endpoint: {url}/status")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{url}/status")
            
            if response.status_code == 200:
                print("   ✅ Status endpoint accessible")
                status_data = response.json()
                print(f"   Status: {status_data.get('status', 'N/A')}")
                return True
            else:
                print(f"   ❌ Status endpoint returned status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_a2a_protocol(url, agent_name):
    """Test if A2A protocol endpoint accepts POST requests"""
    print(f"\n3. Testing A2A protocol endpoint (JSON-RPC POST)")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try to send a simple JSON-RPC request
            # The A2A protocol uses JSON-RPC, so we'll test if POST is accepted
            jsonrpc_payload = {
                "jsonrpc": "2.0",
                "id": "test-1",
                "method": "a2a/sendMessage",
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": "test"}]
                    }
                }
            }
            
            response = await client.post(
                url,
                json=jsonrpc_payload,
                headers={"Content-Type": "application/json"}
            )
            
            # We expect either 200 (success) or a proper error response (not 405)
            if response.status_code == 200:
                print("   ✅ A2A protocol endpoint accepts POST requests")
                return True
            elif response.status_code == 405:
                print("   ❌ A2A protocol endpoint returned 405 Method Not Allowed")
                print("   This is the error we're trying to fix!")
                return False
            elif response.status_code in [400, 422]:
                # These are acceptable - means endpoint exists but request format might be wrong
                print(f"   ⚠️  A2A protocol endpoint returned {response.status_code}")
                print("   (This is OK - endpoint exists, just need proper request format)")
                return True
            else:
                print(f"   ⚠️  Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return True  # Not a 405, so endpoint might be working
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("Agent Setup Test Suite")
    print("="*70)
    
    # Test green agent (port 9001)
    green_url = "http://localhost:9001"
    green_tests = [
        await test_agent_card(green_url, "Green"),
        await test_status_endpoint(green_url, "Green"),
        await test_a2a_protocol(green_url, "Green"),
    ]
    
    # Test white agent (port 9002)
    white_url = "http://localhost:9002"
    white_tests = [
        await test_agent_card(white_url, "White"),
        await test_status_endpoint(white_url, "White"),
        await test_a2a_protocol(white_url, "White"),
    ]
    
    # Summary
    print(f"\n{'='*70}")
    print("Test Summary")
    print(f"{'='*70}")
    print(f"\nGreen Agent:")
    print(f"  Agent Card: {'✅' if green_tests[0] else '❌'}")
    print(f"  Status Endpoint: {'✅' if green_tests[1] else '❌'}")
    print(f"  A2A Protocol: {'✅' if green_tests[2] else '❌'}")
    
    print(f"\nWhite Agent:")
    print(f"  Agent Card: {'✅' if white_tests[0] else '❌'}")
    print(f"  Status Endpoint: {'✅' if white_tests[1] else '❌'}")
    print(f"  A2A Protocol: {'✅' if white_tests[2] else '❌'}")
    
    all_passed = all(green_tests) and all(white_tests)
    
    if all_passed:
        print(f"\n✅ All tests passed! Agents are properly configured.")
        return 0
    else:
        print(f"\n❌ Some tests failed. Please check the errors above.")
        print(f"\nMake sure:")
        print(f"  1. Both agents are running (python main.py green & python main.py white)")
        print(f"  2. Agents are listening on ports 9001 (green) and 9002 (white)")
        print(f"  3. No firewall is blocking access")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

