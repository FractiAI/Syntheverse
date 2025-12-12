#!/usr/bin/env python3
"""
Test script to send a PoD-style evaluation query to the RAG API.
This simulates what the L2 PoD server sends.
"""

import requests
import json
import sys

RAG_API_URL = "http://localhost:8000"

# Simplified version of the PoD evaluation system prompt
POD_SYSTEM_PROMPT = """You are the **L2 Syntheverse PoD Reviewer**, responsible for evaluating any submitted artifact using the Hydrogen-Holographic Fractal Engine (HHFE).

Evaluate this artifact and provide:
1. Coherence (Φ): 0-10000
2. Density (ρ): 0-10000
3. Redundancy (R): 0-1
4. PoD Score (S): calculated using formula S = (Φ/10000) × (ρ/10000) × (1-R) × W × 10000
5. Tier classification: gold|silver|copper
6. Epoch qualification: founder|pioneer|community|ecosystem

Return JSON format:
{
    "coherence": <0-10000>,
    "density": <0-10000>,
    "redundancy": <0-1>,
    "epoch_weight": <typically 1.0>,
    "pod_score": <calculated>,
    "tier": "gold|silver|copper",
    "epoch": "founder|pioneer|community|ecosystem",
    "status": "approved|rejected",
    "reasoning": "<brief explanation>"
}"""

def test_pod_evaluation_query():
    """Test the RAG API with a PoD evaluation-style query."""
    
    print("=" * 70)
    print("Testing RAG API with PoD Evaluation Query")
    print("=" * 70)
    
    # Step 1: Health check
    print("\n[1] Checking RAG API health...")
    try:
        health_response = requests.get(f"{RAG_API_URL}/health", timeout=10)
        if health_response.status_code == 200:
            print(f"   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Step 2: PoD evaluation query
    print("\n[2] Sending PoD evaluation query to RAG API...")
    
    # Sample artifact content (simplified)
    evaluation_query = """
Artifact Content:
Title: Test Scientific Paper on Fractal Structures

Content:
This paper introduces a novel approach to understanding fractal structures in quantum systems. We propose a hydrogen-holographic framework that links atomic geometry to cognitive fractal structures. Our model demonstrates coherence through recursive closure and phase alignment.

Current Epoch Metadata:
- Active Epoch: pioneer
- Epoch Thresholds:
  * Founder: Density ≥ 8000
  * Pioneer: Density ≥ 6000
  * Community: Density ≥ 4000
  * Ecosystem: Density < 4000

Evaluate this artifact using the HHFE model and provide the required metrics.
"""
    
    try:
        query_payload = {
            "query": evaluation_query,
            "system_prompt": POD_SYSTEM_PROMPT,
            "top_k": 5,
            "llm_model": "ollama"  # Use ollama since it's available
        }
        
        print(f"   Query length: {len(evaluation_query)} characters")
        print(f"   System prompt length: {len(POD_SYSTEM_PROMPT)} characters")
        print(f"   Sending request (timeout: 180s - this may take 30-120 seconds)...")
        
        import time
        start_time = time.time()
        
        response = requests.post(
            f"{RAG_API_URL}/query",
            json=query_payload,
            timeout=180
        )
        
        elapsed = time.time() - start_time
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response time: {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Query successful")
            print(f"\n   Response:")
            print(f"   - Answer length: {len(result.get('answer', ''))} characters")
            print(f"   - Sources found: {len(result.get('sources', []))}")
            
            # Show preview of answer
            answer = result.get('answer', '')
            if answer:
                preview = answer[:500] + "..." if len(answer) > 500 else answer
                print(f"\n   Answer preview:")
                print(f"   {preview}")
            
            # Try to extract JSON if present
            import re
            json_match = re.search(r'\{[^{}]*\}', answer, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    print(f"\n   ✅ Found JSON in response:")
                    print(f"   {json.dumps(json_data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"\n   ⚠️  JSON found but could not parse")
            
            return True
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Query timed out after 180 seconds")
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
    success = test_pod_evaluation_query()
    sys.exit(0 if success else 1)
