#!/usr/bin/env python3
"""Test script to diagnose controller and agent setup issues."""

import asyncio
import httpx
import sys
from pathlib import Path

async def test_controller_endpoint(url, test_name):
    """Test various endpoints on the controller"""
    print(f"\n{'='*70}")
    print(f"Testing {test_name}")
    print(f"{'='*70}")
    print(f"Controller URL: {url}")
    
    results = {}
    
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        # Test 1: Root endpoint
        print(f"\n1. Testing root endpoint: {url}/")
        try:
            response = await client.get(f"{url}/")
            print(f"   Status: {response.status_code}")
            results['root'] = response.status_code == 200
            if response.status_code != 200:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results['root'] = False
        
        # Test 2: Agent card endpoint
        print(f"\n2. Testing agent card: {url}/.well-known/agent-card.json")
        try:
            response = await client.get(f"{url}/.well-known/agent-card.json")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                card = response.json()
                print(f"   ✅ Agent card accessible")
                print(f"   Agent Name: {card.get('name', 'N/A')}")
                print(f"   Agent URL: {card.get('url', 'N/A')}")
                results['agent_card'] = True
            else:
                print(f"   ❌ Status {response.status_code}: {response.text[:200]}")
                results['agent_card'] = False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results['agent_card'] = False
        
        # Test 3: POST request (JSON-RPC)
        print(f"\n3. Testing POST request (A2A protocol): {url}/")
        try:
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
            print(f"   Status: {response.status_code}")
            if response.status_code == 405:
                print(f"   ❌ 405 Method Not Allowed - This is the problem!")
                print(f"   Response headers: {dict(response.headers)}")
                results['post'] = False
            elif response.status_code == 200:
                print(f"   ✅ POST request accepted")
                results['post'] = True
            else:
                print(f"   ⚠️  Status {response.status_code}: {response.text[:200]}")
                results['post'] = response.status_code != 405
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results['post'] = False
        
        # Test 4: Check if there's a /to_agent endpoint
        print(f"\n4. Testing controller routing: {url}/to_agent/")
        try:
            response = await client.get(f"{url}/to_agent/")
            print(f"   Status: {response.status_code}")
            results['routing'] = response.status_code != 404
        except Exception as e:
            print(f"   Status: {e}")
            results['routing'] = False
    
    return results


async def main():
    """Run diagnostics"""
    print("\n" + "="*70)
    print("Controller Setup Diagnostics")
    print("="*70)
    
    # Test green agent controller
    green_url = "https://reveal-retained-rico-sbjct.trycloudflare.com"
    green_results = await test_controller_endpoint(green_url, "Green Agent Controller")
    
    # Test white agent controller  
    white_url = "https://buy-jeff-twist-safe.trycloudflare.com"
    white_results = await test_controller_endpoint(white_url, "White Agent Controller")
    
    # Summary
    print(f"\n{'='*70}")
    print("Diagnostic Summary")
    print(f"{'='*70}")
    
    print(f"\nGreen Agent Controller:")
    print(f"  Root endpoint: {'✅' if green_results.get('root') else '❌'}")
    print(f"  Agent card: {'✅' if green_results.get('agent_card') else '❌'}")
    print(f"  POST requests: {'✅' if green_results.get('post') else '❌'}")
    
    print(f"\nWhite Agent Controller:")
    print(f"  Root endpoint: {'✅' if white_results.get('root') else '❌'}")
    print(f"  Agent card: {'✅' if white_results.get('agent_card') else '❌'}")
    print(f"  POST requests: {'✅' if white_results.get('post') else '❌'}")
    
    # Recommendations
    print(f"\n{'='*70}")
    print("Recommendations")
    print(f"{'='*70}")
    
    if not green_results.get('post') or not white_results.get('post'):
        print("\n❌ POST requests are failing (405 Method Not Allowed)")
        print("\nPossible causes:")
        print("1. Controller isn't properly proxying POST requests to the agent")
        print("2. Agent behind controller isn't running or accessible")
        print("3. Controller routing configuration issue")
        print("\nThings to check:")
        print("- Is the agent actually running? Check logs from 'run.sh'")
        print("- Is the controller able to start the agent? Check controller logs")
        print("- Verify the agent is listening on the port the controller expects")
        print("- Check if there are any firewall/network issues")
        print("\nTo debug:")
        print("1. Check controller logs for errors")
        print("2. Verify agent is running: curl http://localhost:9001/status (or 9002)")
        print("3. Test agent directly: curl -X POST http://localhost:9001/")
        print("4. Check if controller can reach agent internally")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

