#!/usr/bin/env python3
"""
Test script to send a simple query to the RAG API.
"""

import requests
import json
import sys

RAG_API_URL = "http://localhost:8000"

def test_rag_api():
    """Test the RAG API with a simple query."""
    
    print("=" * 70)
    print("Testing RAG API")
    print("=" * 70)
    
    # Step 1: Health check
    print("\n[1] Checking RAG API health...")
    try:
        health_response = requests.get(f"{RAG_API_URL}/health", timeout=10)
        print(f"   Status Code: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ Health check passed")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Chunks loaded: {health_data.get('chunks_loaded', 0)}")
            print(f"   PDFs loaded: {health_data.get('pdfs_loaded', 0)}")
            print(f"   Default LLM: {health_data.get('default_llm', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {health_response.text}")
            return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Health check timed out")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Could not connect to RAG API at {RAG_API_URL}")
        print(f"   Make sure the RAG API server is running")
        return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Step 2: Simple query test
    print("\n[2] Sending test query to RAG API...")
    test_query = "What is the Syntheverse PoD protocol?"
    
    try:
        query_payload = {
            "query": test_query,
            "top_k": 3,
            "llm_model": "ollama"  # Use ollama since it's available
        }
        
        print(f"   Query: {test_query}")
        print(f"   Sending request (timeout: 60s)...")
        
        response = requests.post(
            f"{RAG_API_URL}/query",
            json=query_payload,
            timeout=60
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Query successful")
            print(f"\n   Response:")
            print(f"   - Answer length: {len(result.get('answer', ''))} characters")
            print(f"   - Sources found: {len(result.get('sources', []))}")
            
            # Show preview of answer
            answer = result.get('answer', '')
            if answer:
                preview = answer[:300] + "..." if len(answer) > 300 else answer
                print(f"\n   Answer preview:")
                print(f"   {preview}")
            
            # Show sources
            sources = result.get('sources', [])
            if sources:
                print(f"\n   Sources:")
                for i, source in enumerate(sources[:3], 1):
                    print(f"   {i}. {source.get('title', 'Unknown')} (score: {source.get('score', 0):.4f})")
            
            return True
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Query timed out after 60 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error during query")
        return False
    except Exception as e:
        print(f"   ❌ Query error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rag_api()
    sys.exit(0 if success else 1)
