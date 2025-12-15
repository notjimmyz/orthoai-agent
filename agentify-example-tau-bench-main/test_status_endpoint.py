"""Test script to verify /status endpoint works correctly."""

import requests
import json

def test_status_endpoint():
    """Test the /status endpoint on both localhost and tunnel"""
    
    print("=" * 70)
    print("Status Endpoint Test")
    print("=" * 70)
    print()
    
    test_urls = [
        ("http://localhost:9001/status", "Localhost"),
        ("https://con-played-only-landing.trycloudflare.com/status", "Cloudflare Tunnel")
    ]
    
    all_passed = True
    
    for url, name in test_urls:
        print(f"Testing {name}: {url}")
        print("-" * 70)
        
        try:
            response = requests.get(url, timeout=10, verify=True if "https" in url else False)
            
            if response.status_code == 200:
                print(f"✅ Status Code: {response.status_code}")
                try:
                    data = response.json()
                    print(f"✅ Response JSON:")
                    print(json.dumps(data, indent=2))
                    
                    # Verify expected fields
                    expected_fields = ["status", "agent", "url"]
                    missing_fields = [field for field in expected_fields if field not in data]
                    
                    if missing_fields:
                        print(f"⚠️  Missing fields: {missing_fields}")
                    else:
                        print("✅ All expected fields present")
                    
                    if data.get("status") == "ok":
                        print("✅ Status is 'ok'")
                    else:
                        print(f"⚠️  Status is '{data.get('status')}' (expected 'ok')")
                    
                except json.JSONDecodeError:
                    print(f"⚠️  Response is not valid JSON:")
                    print(response.text[:200])
                    
            else:
                print(f"❌ Status Code: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                all_passed = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            all_passed = False
        
        print()
    
    print("=" * 70)
    if all_passed:
        print("✅ All status endpoint tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 70)
    
    return all_passed

if __name__ == "__main__":
    success = test_status_endpoint()
    exit(0 if success else 1)

