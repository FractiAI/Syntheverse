#!/usr/bin/env python3
"""
Quick test to see if RAG API is responding and how long it takes.
"""

import requests
import time
import sys

RAG_API_URL = "http://localhost:8000"

def test_rag_response_time():
    """Test RAG API response time with a simple query."""
    
    print("Testing RAG API response time...")
    print(f"URL: {RAG_API_URL}")
    
    # Test 1: Health check
    print("\n[1] Health check...")
    try:
        start = time.time()
        health = requests.get(f"{RAG_API_URL}/health", timeout=5)
        elapsed = time.time() - start
        print(f"   Status: {health.status_code}")
        print(f"   Time: {elapsed:.2f}s")
        if health.status_code != 200:
            print(f"   ❌ Health check failed")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Simple query
    print("\n[2] Simple query (timeout: 30s)...")
    try:
        start = time.time()
        response = requests.post(
            f"{RAG_API_URL}/query",
            json={
                "query": "What is Syntheverse?",
                "top_k": 3,
                "llm_model": "ollama"
            },
            timeout=30
        )
        elapsed = time.time() - start
        print(f"   Status: {response.status_code}")
        print(f"   Time: {elapsed:.2f}s")
        if response.status_code == 200:
            result = response.json()
            print(f"   Answer length: {len(result.get('answer', ''))} chars")
            print(f"   ✅ Query successful")
        else:
            print(f"   ❌ Query failed: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Query timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"   ❌ Query error: {e}")
        return False
    
    # Test 3: Check if there are pending requests
    print("\n[3] Checking for pending requests...")
    try:
        # Try another quick health check
        health2 = requests.get(f"{RAG_API_URL}/health", timeout=2)
        print(f"   Health check still responsive: {health2.status_code}")
    except Exception as e:
        print(f"   ⚠️  Health check slow: {e}")
    
    return True

if __name__ == "__main__":
    success = test_rag_response_time()
    sys.exit(0 if success else 1)
