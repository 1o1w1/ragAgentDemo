#!/usr/bin/env python3
"""Complete integration test for streaming API"""

import requests
import json
import sys

def test_get_streaming():
    """Test GET streaming API endpoint"""
    url = "http://localhost:8000/api/chat/stream"
    query = "什么是机器学习？"
    
    print(f"Test 1: GET streaming API with query: {query}")
    print("=" * 50)
    
    try:
        response = requests.get(url, params={"query": query}, stream=True, timeout=60)
        
        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            return False
        
        token_count = 0
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    data = json.loads(line[5:].strip())
                    if 'content' in data:
                        token_count += 1
                    elif 'status' in data and data['status'] == 'complete':
                        print(f"✓ Stream complete after {token_count} tokens")
                        return True
                    elif 'message' in data:
                        print(f"✗ Error: {data['message']}")
                        return False
        
        print(f"✗ Stream ended without completion signal")
        return False
        
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def test_post_streaming():
    """Test POST streaming API endpoint"""
    url = "http://localhost:8000/api/chat/stream"
    query = "什么是深度学习？"
    
    print(f"\nTest 2: POST streaming API with query: {query}")
    print("=" * 50)
    
    try:
        response = requests.post(url, json={"query": query}, stream=True, timeout=60)
        
        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            return False
        
        token_count = 0
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    data = json.loads(line[5:].strip())
                    if 'content' in data:
                        token_count += 1
                    elif 'status' in data and data['status'] == 'complete':
                        print(f"✓ Stream complete after {token_count} tokens")
                        return True
                    elif 'message' in data:
                        print(f"✗ Error: {data['message']}")
                        return False
        
        print(f"✗ Stream ended without completion signal")
        return False
        
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def test_error_handling():
    """Test error handling scenarios"""
    url = "http://localhost:8000/api/chat/stream"
    
    print(f"\nTest 3: Error handling scenarios")
    print("=" * 50)
    
    # Test empty query
    try:
        response = requests.get(url, params={"query": ""}, stream=True, timeout=10)
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data:'):
                        data = json.loads(line[5:].strip())
                        if 'message' in data:
                            print(f"✓ Empty query handled: {data['message']}")
                            break
                        elif 'status' in data and data['status'] == 'complete':
                            print(f"✓ Empty query handled (no error)")
                            break
        else:
            print(f"✓ Empty query returned status: {response.status_code}")
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False
    
    # Test invalid endpoint
    try:
        response = requests.get("http://localhost:8000/api/chat/invalid", timeout=5)
        if response.status_code == 404:
            print(f"✓ Invalid endpoint returns 404")
        else:
            print(f"✗ Invalid endpoint returns {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False
    
    return True

def test_health_endpoint():
    """Test health endpoint"""
    print(f"\nTest 4: Health endpoint")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                print(f"✓ Health endpoint returns OK")
                return True
            else:
                print(f"✗ Health endpoint returns unexpected data: {data}")
                return False
        else:
            print(f"✗ Health endpoint returns status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

if __name__ == "__main__":
    print("Integration Test Suite for Streaming API")
    print("=" * 50)
    
    # Run all tests
    test1 = test_get_streaming()
    test2 = test_post_streaming()
    test3 = test_error_handling()
    test4 = test_health_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"  GET streaming API: {'✓ PASS' if test1 else '✗ FAIL'}")
    print(f"  POST streaming API: {'✓ PASS' if test2 else '✗ FAIL'}")
    print(f"  Error handling: {'✓ PASS' if test3 else '✗ FAIL'}")
    print(f"  Health endpoint: {'✓ PASS' if test4 else '✗ FAIL'}")
    
    all_passed = test1 and test2 and test3 and test4
    print(f"\nOverall result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    
    sys.exit(0 if all_passed else 1)