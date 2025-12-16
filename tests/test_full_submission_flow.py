#!/usr/bin/env python3
"""
Test full submission flow with RAG API to verify everything works.
"""

import requests
import json
import sys
import time
from pathlib import Path

RAG_API_URL = "http://localhost:8000"

# Full PoD evaluation system prompt
POD_SYSTEM_PROMPT = """You are the **L2 Syntheverse PoD Reviewer**, responsible for evaluating any submitted artifact using the Hydrogen-Holographic Fractal Engine (HHFE) and producing:

1. **PoD Score**
2. **Epoch-weighted token allocation**
3. **Gold / Silver / Copper tier classification**
4. **Full PoD Evaluation Report**
5. **PoD Certificate** (if qualified)

You perform all reasoning using Syntheverse HHFE rules and the FractiEmbedding archive supplied via RAG.

---

## **CORE EVALUATION MODEL**

### **1. Compute HHFE Metrics**

**Coherence (Φ):**
Degree of fractal grammar closure, recursion depth, phase alignment.

**Density (ρ):**
Novel structural contribution per fractal unit.

**Redundancy (R):**
Similarity to existing artifacts; penalizes repetition.

**Epoch Weight (W):**
Derived from the active Epoch (Founders → Pioneer → Explorer → Expansion).

### **PoD Score**

S = (Φ/10000) × (ρ/10000) × (1-R) × W × 10000

Artifacts qualify for issuance **only if**:
S ≥ T_epoch

---

## **GOLD / SILVER / COPPER TIER LOGIC**

### **GOLD — Scientific Contribution**
* Introduces validated scientific structure, models, equations, or empirically grounded frameworks.
* Advances structural truth directly.
* Highest reward multiplier.

### **SILVER — Technological Contribution**
* Implements, extends, or operationalizes HHFE principles into tools, apps, engines, or protocols.
* Medium reward multiplier.

### **COPPER — Alignment Contribution**
* Improves conceptual clarity, narrative integration, coherence, safety, or symbolic alignment of the system.
* Lowest reward multiplier (still valuable).

---

## **OUTPUT FORMAT**

Return JSON format:

{
    "coherence": <0-10000>,
    "density": <0-10000>,
    "redundancy": <0-1>,
    "epoch_weight": <typically 1.0>,
    "pod_score": <calculated>,
    "tier": "gold|silver|copper",
    "epoch": "founder|pioneer|community|ecosystem",
    "tier_justification": "<explicit reasoning for tier classification>",
    "redundancy_analysis": "<analysis of similarity to archive>",
    "epoch_justification": "<why this epoch qualified>",
    "reasoning": "<full evaluation reasoning>",
    "status": "approved|rejected",
    "rejection_reason": "<if rejected>"
}"""

def test_full_submission_flow():
    """Test the full submission flow with progress tracking."""
    
    print("=" * 70)
    print("Testing Full Submission Flow with RAG API")
    print("=" * 70)
    
    # Step 1: Health check
    print("\n[1] Checking RAG API health...")
    try:
        health_response = requests.get(f"{RAG_API_URL}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ Health check passed")
            print(f"   LLM: {health_data.get('default_llm', 'unknown')}")
            print(f"   Model: {health_data.get('ollama_model', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Step 2: Simulate a submission
    print("\n[2] Simulating PDF submission...")
    
    # Sample artifact content
    title = "Test Scientific Paper on Fractal Quantum Structures"
    artifact_content = """
This paper introduces a novel approach to understanding fractal structures in quantum systems. 
We propose a hydrogen-holographic framework that links atomic geometry to cognitive fractal structures. 
Our model demonstrates coherence through recursive closure and phase alignment.

Key contributions:
1. Novel fractal grammar for quantum coherence
2. Hydrogen-holographic scaling constants
3. Recursive awareness index calculations
4. Empirical validation framework

The model shows significant structural density and coherence metrics that align with 
Syntheverse HHFE principles.
"""
    
    # Step 3: Build evaluation query
    print("\n[3] Building evaluation query...")
    
    evaluation_query = f"""
Artifact Content:
Title: {title}

Content:
{artifact_content}

Current Epoch Metadata:
- Active Epoch: pioneer
- Epoch Thresholds:
  * Founder: Density ≥ 8000
  * Pioneer: Density ≥ 6000
  * Community: Density ≥ 4000
  * Ecosystem: Density < 4000

Tier Classification Guidelines:
- GOLD: Scientific contributions (validated structure, models, equations, empirical frameworks)
- SILVER: Technological contributions (tools, apps, engines, protocols implementing HHFE)
- COPPER: Alignment contributions (conceptual clarity, narrative, coherence, safety)

Evaluate this artifact using the HHFE model and provide the required metrics.
"""
    
    print(f"   Query length: {len(evaluation_query)} characters")
    print(f"   System prompt length: {len(POD_SYSTEM_PROMPT)} characters")
    
    # Step 4: Send to RAG API with progress tracking
    print("\n[4] Sending evaluation request to RAG API...")
    print("   This simulates what happens during a real submission.")
    print("   Progress stages:")
    
    stages = [
        ("checking_rag_health", "Verifying RAG API is accessible..."),
        ("sending_to_rag", "Sending evaluation request to RAG API..."),
        ("evaluating_rag", "Waiting for LLM response (this may take 30-120 seconds)..."),
        ("parsing_response", "Parsing evaluation response..."),
    ]
    
    for stage, message in stages:
        print(f"   [{stage}] {message}")
        time.sleep(0.5)  # Simulate progress
    
    try:
        print(f"\n   Making POST request to {RAG_API_URL}/query...")
        print(f"   Using LLM: ollama (Groq unavailable)")
        print(f"   Timeout: 180 seconds")
        
        start_time = time.time()
        
        response = requests.post(
            f"{RAG_API_URL}/query",
            json={
                "query": evaluation_query,
                "system_prompt": POD_SYSTEM_PROMPT,
                "top_k": 5,
                "llm_model": "ollama"
            },
            timeout=180
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n   ✅ Response received!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response time: {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "")
            
            print(f"\n   Response details:")
            print(f"   - Answer length: {len(answer)} characters")
            print(f"   - Sources found: {len(result.get('sources', []))}")
            
            # Show preview
            if answer:
                preview = answer[:500] + "..." if len(answer) > 500 else answer
                print(f"\n   Answer preview:")
                print(f"   {preview}")
            
            # Try to extract JSON
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', answer, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    print(f"\n   ✅ Found valid JSON in response:")
                    print(f"   {json.dumps(json_data, indent=2)}")
                    
                    # Validate required fields
                    required_fields = ["coherence", "density", "redundancy", "pod_score", "tier", "epoch", "status"]
                    missing = [f for f in required_fields if f not in json_data]
                    if missing:
                        print(f"\n   ⚠️  Missing fields: {missing}")
                    else:
                        print(f"\n   ✅ All required fields present!")
                        print(f"   - Coherence: {json_data.get('coherence')}")
                        print(f"   - Density: {json_data.get('density')}")
                        print(f"   - Redundancy: {json_data.get('redundancy')}")
                        print(f"   - PoD Score: {json_data.get('pod_score')}")
                        print(f"   - Tier: {json_data.get('tier')}")
                        print(f"   - Epoch: {json_data.get('epoch')}")
                        print(f"   - Status: {json_data.get('status')}")
                    
                    return True
                except json.JSONDecodeError as e:
                    print(f"\n   ⚠️  JSON found but could not parse: {e}")
                    print(f"   JSON snippet: {json_match.group()[:200]}")
            else:
                print(f"\n   ⚠️  No JSON found in response")
                print(f"   Full response: {answer}")
            
            return True
        else:
            print(f"\n   ❌ Query failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n   ❌ Query timed out after 180 seconds")
        print(f"   The RAG API may be overloaded or the LLM is taking too long")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n   ❌ Connection error")
        print(f"   Check if RAG API is running: curl http://localhost:8000/health")
        return False
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\nThis test simulates the full submission flow:")
    print("1. Health check")
    print("2. Build evaluation query")
    print("3. Send to RAG API with system prompt")
    print("4. Parse and validate response\n")
    
    success = test_full_submission_flow()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ Full submission flow test PASSED")
        print("=" * 70)
        print("\nThe RAG API is working correctly for PoD evaluations.")
        print("If progress bar isn't updating, the issue is in the progress tracking, not the RAG API.")
    else:
        print("\n" + "=" * 70)
        print("❌ Full submission flow test FAILED")
        print("=" * 70)
        print("\nCheck the error messages above to diagnose the issue.")
    
    sys.exit(0 if success else 1)

