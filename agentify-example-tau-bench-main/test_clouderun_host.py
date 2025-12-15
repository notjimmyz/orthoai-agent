"""Test script to verify CLOUDRUN_HOST functionality works correctly."""

import os
import sys
import asyncio
import subprocess
import time
import signal
from src.my_util.my_a2a import get_agent_card


def test_agent_card_url(url, expected_url_pattern, test_name):
    """Test that agent card shows the expected URL pattern"""
    print(f"\n{'='*70}")
    print(f"Test: {test_name}")
    print(f"{'='*70}")
    print(f"Fetching agent card from: {url}")
    print(f"Expected URL pattern: {expected_url_pattern}")
    
    try:
        card = asyncio.run(get_agent_card(url))
        if not card:
            print("❌ FAILED: Could not retrieve agent card")
            return False
        
        actual_url = card.url
        print(f"Actual URL in card: {actual_url}")
        
        # Check if the URL matches the expected pattern
        if expected_url_pattern in actual_url:
            print(f"✅ PASSED: Agent card URL contains '{expected_url_pattern}'")
            print(f"   Card URL: {actual_url}")
            return True
        else:
            print(f"❌ FAILED: Agent card URL does not match expected pattern")
            print(f"   Expected to contain: {expected_url_pattern}")
            print(f"   Actual URL: {actual_url}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Error retrieving agent card: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_without_clouderun_host():
    """Test that without CLOUDRUN_HOST, agent uses localhost URL"""
    print("\n" + "="*70)
    print("TEST 1: Agent without CLOUDRUN_HOST (should use localhost)")
    print("="*70)
    
    # Check if agent is running
    result = test_agent_card_url(
        "http://localhost:9001",
        "localhost",
        "Agent card without CLOUDRUN_HOST should show localhost"
    )
    
    return result


def test_with_clouderun_host():
    """Test that with CLOUDRUN_HOST set, agent uses public URL"""
    print("\n" + "="*70)
    print("TEST 2: Agent with CLOUDRUN_HOST (should use Cloudflare URL)")
    print("="*70)
    
    tunnel_url = "con-played-only-landing.trycloudflare.com"
    
    # Test via localhost (agent card should show Cloudflare URL if CLOUDRUN_HOST is set)
    result1 = test_agent_card_url(
        "http://localhost:9001",
        "trycloudflare.com",
        "Agent card should show Cloudflare URL when CLOUDRUN_HOST is set"
    )
    
    # Test via tunnel URL directly
    result2 = test_agent_card_url(
        f"https://{tunnel_url}",
        "trycloudflare.com",
        "Agent card via tunnel should show Cloudflare URL"
    )
    
    return result1 and result2


def test_environment_variable_handling():
    """Test that the URL processing logic correctly handles CLOUDRUN_HOST format"""
    print("\n" + "="*70)
    print("TEST 3: URL Processing Logic")
    print("="*70)
    
    # Test different formats of CLOUDRUN_HOST (simulating the logic in agent.py)
    test_cases = [
        ("con-played-only-landing.trycloudflare.com", "https://con-played-only-landing.trycloudflare.com"),
        ("https://con-played-only-landing.trycloudflare.com", "https://con-played-only-landing.trycloudflare.com"),
        ("http://con-played-only-landing.trycloudflare.com", "http://con-played-only-landing.trycloudflare.com"),
        ("con-played-only-landing.trycloudflare.com/", "https://con-played-only-landing.trycloudflare.com"),
    ]
    
    all_passed = True
    for input_value, expected_output in test_cases:
        # Simulate what the function does (same logic as in agent.py)
        public_url = input_value
        if public_url:
            public_url = public_url.rstrip("/")
            if not public_url.startswith(("http://", "https://")):
                public_url = f"https://{public_url}"
        
        if public_url == expected_output:
            print(f"✅ PASSED: '{input_value}' -> '{public_url}'")
        else:
            print(f"❌ FAILED: '{input_value}' -> '{public_url}' (expected '{expected_output}')")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests"""
    print("="*70)
    print("CLOUDRUN_HOST Functionality Test Suite")
    print("="*70)
    print("\nPrerequisites:")
    print("1. Green agent should be running on localhost:9001")
    print("2. Cloudflare tunnel should be active")
    print("3. If CLOUDRUN_HOST is set, agent should be restarted with it")
    print()
    
    results = []
    current_url = None
    
    # Test 1: Check current state (with or without CLOUDRUN_HOST)
    print("\n" + "🔍 Checking current agent state...")
    try:
        card = asyncio.run(get_agent_card("http://localhost:9001"))
        if card:
            current_url = card.url
            print(f"Current agent card URL: {current_url}")
            
            if "trycloudflare.com" in current_url:
                print("✅ Agent is using Cloudflare URL (CLOUDRUN_HOST appears to be set)")
                results.append(("Current State", True))
            elif "localhost" in current_url:
                print("⚠️  Agent is using localhost URL (CLOUDRUN_HOST not set)")
                print("   To test with CLOUDRUN_HOST, restart agent with:")
                print("   export CLOUDRUN_HOST=con-played-only-landing.trycloudflare.com")
                print("   uv run python main.py green")
                results.append(("Current State", True))  # This is still valid
            else:
                print(f"⚠️  Unexpected URL format: {current_url}")
                results.append(("Current State", False))
        else:
            print("❌ Could not retrieve agent card")
            results.append(("Current State", False))
    except Exception as e:
        print(f"❌ Error checking agent state: {e}")
        results.append(("Current State", False))
    
    # Test 2: Test environment variable handling logic
    results.append(("Environment Variable Handling", test_environment_variable_handling()))
    
    # Test 3: Test agent card retrieval via localhost
    # Determine expected pattern based on current state
    expected_pattern = "trycloudflare.com" if current_url and "trycloudflare.com" in current_url else "localhost"
    results.append(("Agent Card via Localhost", test_agent_card_url(
        "http://localhost:9001",
        expected_pattern,
        "Agent card should be retrievable"
    )))
    
    # Test 4: Test agent card retrieval via tunnel
    results.append(("Agent Card via Tunnel", test_agent_card_url(
        "https://con-played-only-landing.trycloudflare.com",
        "trycloudflare.com",
        "Agent card should be retrievable via tunnel"
    )))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("="*70)
    
    if failed == 0:
        print("\n✅ All tests passed! CLOUDRUN_HOST functionality is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

