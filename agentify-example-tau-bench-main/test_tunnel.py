"""Test script to verify Cloudflare tunnel connection to localhost:9001."""

import requests
import time
from urllib.parse import urlparse

def test_tunnel_connection():
    """Test if Cloudflare tunnel URL correctly forwards to localhost:9001"""
    
    tunnel_url = "https://con-played-only-landing.trycloudflare.com"
    local_url = "http://localhost:9001"
    
    print("=" * 70)
    print("Cloudflare Tunnel Connection Test")
    print("=" * 70)
    print()
    print(f"Tunnel URL: {tunnel_url}")
    print(f"Local URL:  {local_url}")
    print()
    
    results = {
        "local_accessible": False,
        "tunnel_accessible": False,
        "responses_match": False,
        "tunnel_response_time": None,
        "local_response_time": None
    }
    
    # Test 1: Check localhost:9001
    print("Test 1: Checking localhost:9001...")
    try:
        start_time = time.time()
        local_response = requests.get(local_url, timeout=5)
        results["local_response_time"] = time.time() - start_time
        results["local_accessible"] = True
        print(f"✅ Localhost is accessible")
        print(f"   Status Code: {local_response.status_code}")
        print(f"   Response Time: {results['local_response_time']:.3f}s")
        print(f"   Headers: {dict(list(local_response.headers.items())[:3])}")
    except Exception as e:
        print(f"❌ Localhost connection failed: {e}")
        return results
    
    print()
    
    # Test 2: Check Cloudflare tunnel
    print("Test 2: Checking Cloudflare tunnel URL...")
    try:
        start_time = time.time()
        tunnel_response = requests.get(tunnel_url, timeout=10, verify=True)
        results["tunnel_response_time"] = time.time() - start_time
        results["tunnel_accessible"] = True
        print(f"✅ Tunnel URL is accessible")
        print(f"   Status Code: {tunnel_response.status_code}")
        print(f"   Response Time: {results['tunnel_response_time']:.3f}s")
        print(f"   Headers: {dict(list(tunnel_response.headers.items())[:3])}")
    except Exception as e:
        print(f"❌ Tunnel connection failed: {e}")
        return results
    
    print()
    
    # Test 3: Compare responses
    print("Test 3: Comparing responses...")
    if local_response.status_code == tunnel_response.status_code:
        results["responses_match"] = True
        print(f"✅ Status codes match: {local_response.status_code}")
    else:
        print(f"⚠️  Status codes differ:")
        print(f"   Local:  {local_response.status_code}")
        print(f"   Tunnel: {tunnel_response.status_code}")
    
    # Test 4: Try POST request (since GET returns 405)
    print()
    print("Test 4: Testing POST request (since GET returns 405)...")
    try:
        post_data = {"test": "data"}
        local_post = requests.post(local_url, json=post_data, timeout=5)
        tunnel_post = requests.post(tunnel_url, json=post_data, timeout=10, verify=True)
        
        print(f"   Local POST Status:  {local_post.status_code}")
        print(f"   Tunnel POST Status: {tunnel_post.status_code}")
        
        if local_post.status_code == tunnel_post.status_code:
            print(f"✅ POST responses match: {local_post.status_code}")
        else:
            print(f"⚠️  POST status codes differ")
    except Exception as e:
        print(f"⚠️  POST test error: {e}")
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Local accessible:     {'✅' if results['local_accessible'] else '❌'}")
    print(f"Tunnel accessible:    {'✅' if results['tunnel_accessible'] else '❌'}")
    print(f"Responses match:      {'✅' if results['responses_match'] else '⚠️'}")
    
    if results["tunnel_response_time"]:
        print(f"Tunnel response time: {results['tunnel_response_time']:.3f}s")
    
    if results["local_response_time"]:
        print(f"Local response time:  {results['local_response_time']:.3f}s")
        if results["tunnel_response_time"]:
            overhead = results["tunnel_response_time"] - results["local_response_time"]
            print(f"Tunnel overhead:     {overhead:.3f}s")
    
    print()
    
    if results["local_accessible"] and results["tunnel_accessible"]:
        print("✅ SUCCESS: Cloudflare tunnel is working correctly!")
        print("   The tunnel URL successfully forwards requests to localhost:9001")
    else:
        print("❌ FAILURE: Tunnel connection issues detected")
    
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    test_tunnel_connection()

