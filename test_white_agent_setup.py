#!/usr/bin/env python3
"""Test script to verify white agent setup is working correctly."""

import asyncio
import httpx
import json
import sys
from pathlib import Path

async def test_agent_direct(port, agent_name):
    """Test agent directly on its port"""
    print(f"\n{'='*70}")
    print(f"1. Testing Agent Directly (port {port})")
    print(f"{'='*70}")
    
    base_url = f"http://localhost:{port}"
    results = {}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test /status
        try:
            response = await client.get(f"{base_url}/status")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ /status endpoint: {data.get('status')}")
                results['status'] = True
            else:
                print(f"   ❌ /status endpoint: Status {response.status_code}")
                results['status'] = False
        except Exception as e:
            print(f"   ❌ /status endpoint: {e}")
            results['status'] = False
        
        # Test /port
        try:
            response = await client.get(f"{base_url}/port")
            if response.status_code == 200:
                data = response.json()
                detected_port = data.get('port')
                print(f"   ✅ /port endpoint: Port {detected_port}")
                results['port_endpoint'] = True
                results['detected_port'] = detected_port
            else:
                print(f"   ❌ /port endpoint: Status {response.status_code}")
                results['port_endpoint'] = False
        except Exception as e:
            print(f"   ❌ /port endpoint: {e}")
            results['port_endpoint'] = False
        
        # Test agent card
        try:
            response = await client.get(f"{base_url}/.well-known/agent-card.json")
            if response.status_code == 200:
                card = response.json()
                print(f"   ✅ Agent card: {card.get('name')}")
                print(f"      URL: {card.get('url')}")
                results['agent_card'] = True
            else:
                print(f"   ❌ Agent card: Status {response.status_code}")
                results['agent_card'] = False
        except Exception as e:
            print(f"   ❌ Agent card: {e}")
            results['agent_card'] = False
    
    return results


async def test_controller(controller_port, agent_id=None):
    """Test agent through controller"""
    print(f"\n{'='*70}")
    print(f"2. Testing Through Controller (port {controller_port})")
    print(f"{'='*70}")
    
    base_url = f"http://localhost:{controller_port}"
    results = {}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Get agent ID if not provided
        if not agent_id:
            try:
                response = await client.get(f"{base_url}/agents")
                if response.status_code == 200:
                    agents = response.json()
                    agent_ids = list(agents.keys())
                    if agent_ids:
                        agent_id = agent_ids[0]
                        print(f"   Found agent ID: {agent_id}")
                    else:
                        print("   ❌ No agents found")
                        return results
                else:
                    print(f"   ❌ Failed to get agents: {response.status_code}")
                    return results
            except Exception as e:
                print(f"   ❌ Error getting agents: {e}")
                return results
        
        # Test agent card through controller
        try:
            url = f"{base_url}/to_agent/{agent_id}/.well-known/agent-card.json"
            response = await client.get(url)
            if response.status_code == 200:
                card = response.json()
                print(f"   ✅ Agent card through controller: {card.get('name')}")
                results['controller_agent_card'] = True
            else:
                print(f"   ❌ Agent card through controller: Status {response.status_code}")
                print(f"      URL: {url}")
                results['controller_agent_card'] = False
        except Exception as e:
            print(f"   ❌ Agent card through controller: {e}")
            results['controller_agent_card'] = False
        
        # Test POST through controller
        try:
            url = f"{base_url}/to_agent/{agent_id}/"
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
            response = await client.post(url, json=jsonrpc_payload)
            if response.status_code == 200:
                print(f"   ✅ POST request through controller: Accepted")
                results['controller_post'] = True
            elif response.status_code == 405:
                print(f"   ❌ POST request through controller: 405 Method Not Allowed")
                results['controller_post'] = False
            else:
                print(f"   ⚠️  POST request through controller: Status {response.status_code}")
                results['controller_post'] = response.status_code != 405
        except Exception as e:
            print(f"   ❌ POST request through controller: {e}")
            results['controller_post'] = False
    
    return results, agent_id


async def test_ngrok(ngrok_url, agent_id):
    """Test agent through ngrok"""
    print(f"\n{'='*70}")
    print(f"3. Testing Through Ngrok")
    print(f"{'='*70}")
    print(f"   URL: {ngrok_url}")
    
    results = {}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test agent card through ngrok
        try:
            url = f"{ngrok_url}/to_agent/{agent_id}/.well-known/agent-card.json"
            response = await client.get(url, headers={"ngrok-skip-browser-warning": "true"})
            if response.status_code == 200:
                card = response.json()
                print(f"   ✅ Agent card through ngrok: {card.get('name')}")
                results['ngrok_agent_card'] = True
            else:
                print(f"   ❌ Agent card through ngrok: Status {response.status_code}")
                results['ngrok_agent_card'] = False
        except Exception as e:
            print(f"   ❌ Agent card through ngrok: {e}")
            results['ngrok_agent_card'] = False
    
    return results


async def check_controller_status(controller_port):
    """Check controller status"""
    print(f"\n{'='*70}")
    print(f"4. Controller Status")
    print(f"{'='*70}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"http://localhost:{controller_port}/status")
            if response.status_code == 200:
                status = response.json()
                print(f"   Running agents: {status.get('running_agents', 0)}")
                print(f"   Maintained agents: {status.get('maintained_agents', 0)}")
                return status
            else:
                print(f"   ❌ Failed to get status: {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("White Agent Setup Test")
    print("="*70)
    
    # Configuration
    AGENT_PORT = 9003
    CONTROLLER_PORT = 8010
    NGROK_URL = "https://55c3b2b7f0c1.ngrok-free.app"  # Update this with your ngrok URL
    
    # Test 1: Agent directly
    direct_results = await test_agent_direct(AGENT_PORT, "White Agent")
    
    # Test 2: Controller status
    controller_status = await check_controller_status(CONTROLLER_PORT)
    
    # Test 3: Through controller
    controller_results, agent_id = await test_controller(CONTROLLER_PORT)
    
    # Test 4: Through ngrok (if agent_id found)
    ngrok_results = {}
    if agent_id:
        ngrok_results = await test_ngrok(NGROK_URL, agent_id)
    
    # Summary
    print(f"\n{'='*70}")
    print("Test Summary")
    print(f"{'='*70}")
    
    print(f"\nDirect Agent Tests:")
    print(f"  Status endpoint: {'✅' if direct_results.get('status') else '❌'}")
    print(f"  Port endpoint: {'✅' if direct_results.get('port_endpoint') else '❌'}")
    if direct_results.get('detected_port'):
        print(f"    Detected port: {direct_results['detected_port']}")
    print(f"  Agent card: {'✅' if direct_results.get('agent_card') else '❌'}")
    
    print(f"\nController Tests:")
    print(f"  Agent card: {'✅' if controller_results.get('controller_agent_card') else '❌'}")
    print(f"  POST requests: {'✅' if controller_results.get('controller_post') else '❌'}")
    
    print(f"\nNgrok Tests:")
    print(f"  Agent card: {'✅' if ngrok_results.get('ngrok_agent_card') else '❌'}")
    
    # Overall status
    all_passed = (
        direct_results.get('status') and
        direct_results.get('port_endpoint') and
        direct_results.get('agent_card') and
        controller_results.get('controller_agent_card') and
        ngrok_results.get('ngrok_agent_card')
    )
    
    if all_passed:
        print(f"\n✅ All tests passed! Your agent is ready for AgentBeats.")
        print(f"\nSubmit this URL to AgentBeats:")
        print(f"  {NGROK_URL}/to_agent/{agent_id}/")
        return 0
    else:
        print(f"\n❌ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

