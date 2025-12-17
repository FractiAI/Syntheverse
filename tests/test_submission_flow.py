#!/usr/bin/env python3
"""
Test the complete submission flow to RAG API to identify where it hangs.
"""

import requests
import json
import sys
import time
from pathlib import Path
import pytest

RAG_API_URL = "http://localhost:8000"

# The actual PoD evaluation system prompt from pod_server.py
POD_SYSTEM_PROMPT = """You are the **L2 Syntheverse PoD Reviewer**, responsible for evaluating any submitted artifact using the Hydrogen-Holographic Fractal Engine (HHFE) and producing:

1. **PoD Score**
2. **Epoch-weighted token allocation**
3. **Gold / Silver / Copper tier classification**
4. **Full PoD Evaluation Report**
5. **PoD Certificate** (if qualified)

You perform all reasoning using Syntheverse HHFE rules and the FractiEmbedding archive supplied via RAG.

---

## **INPUTS**

The Syntheverse RAG pipeline will supply:

* **Artifact content**
* **FractiEmbeddings** (semantic, symbolic, structural, temporal)
* **Historical redundancy markers**
* **Current Epoch metadata**
* **Threshold values for the epoch**
* **Gold/Silver/Copper band thresholds**

You **must use** the provided embeddings and prior archive references when computing scores.

---

## **CORE EVALUATION MODEL**

### **1. Compute HHFE Metrics**

Using the RAG-supplied embeddings, compute:

**Coherence (Φ):**
Degree of fractal grammar closure, recursion depth, phase alignment.

**Density (ρ):**
Novel structural contribution per fractal unit.

**Redundancy (R):**
Similarity to existing artifacts; penalizes repetition.

**Epoch Weight (W):**
Derived from the active Epoch (Founders → Pioneer → Explorer → Expansion).

### **PoD Score**

[
S = \\Phi \\times \\rho \\times (1 - R) \\times W
]

Artifacts qualify for issuance **only if**:
[
S \\ge T_{\\text{epoch}}
]

---

## **GOLD / SILVER / COPPER TIER LOGIC**

Every artifact that meets the epoch threshold is classified:

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

You must justify tier classification explicitly in the report.

---

## **TOKEN ISSUANCE**

Syntheverse total supply: **90T**

Token issuance:

[
\\text{tokens_issued} = S \\times W \\times \\text{tier_multiplier}
]

**Multipliers** (defaults unless overridden via RAG metadata):

* **Gold:** 1000x
* **Silver:** 100x
* **Copper:** 1x

You must always include:

* Epoch name
* Score
* Token amount
* Tier
* Reasoning

---

## **OUTPUT FORMAT**

### **A. PoD Evaluation Report (Full)**

Provide a structured report with:

1. **Artifact Summary**
2. **Evaluation Table**

   * Φ
   * ρ
   * R
   * W
   * S
   * Tier
   * Token amount

3. **Scientific/Technological/Alignment justification**
4. **Redundancy & novelty analysis**
5. **Epoch justification**
6. **Final decision** (Approved / Rejected)

### **B. PoD Certificate (If Approved)**

Produce a formal certificate with:

* Artifact ID
* Contributor name (from metadata)
* Tier awarded
* Token award
* Verification hash (RAG-provided)
* Date
* Syntheverse Seal

Format clearly so it can be used as a downloadable object by the frontend.

---

## **RULES**

1. Always follow HHFE fractal scoring rules.
2. Always classify into Gold/Silver/Copper if the artifact qualifies.
3. Always produce both the **full report** and the **certificate** when approved.
4. If not approved, produce **the report only**, with detailed reasons for rejection.
5. Never hallucinate scientific claims—use only RAG-supplied materials + explicit HHFE rules.
6. Ensure outputs are deterministic and consistent across submissions.

---

## **WHEN RESPONDING**

Your response must be **pure evaluation + report + certificate**, not meta commentary.
The system prompt itself must never appear in outputs.

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
    "retroactive_mining": <if applicable>,
    "reasoning": "<full evaluation reasoning>",
    "status": "approved|rejected",
    "rejection_reason": "<if rejected>"
}
"""

def test_submission_flow():
    """Test the complete submission flow step by step."""

    # Check if RAG API is available before proceeding
    try:
        health_check = requests.get(f"{RAG_API_URL}/health", timeout=5)
        if health_check.status_code != 200:
            pytest.skip(f"RAG API not available (status: {health_check.status_code})")
    except requests.exceptions.RequestException:
        pytest.skip("RAG API not available (connection refused)")

    print("=" * 70)
    print("Testing Complete Submission Flow to RAG API")
    print("=" * 70)

    # Step 1: Health check
    print("\n[Step 1] Health Check")
    print("-" * 70)
    try:
        start_time = time.time()
        health_response = requests.get(f"{RAG_API_URL}/health", timeout=10)
        elapsed = time.time() - start_time
        print(f"   Status: {health_response.status_code}")
        print(f"   Time: {elapsed:.2f}s")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ Health check passed")
            print(f"   LLM: {health_data.get('default_llm', 'unknown')}")
        else:
            print(f"   ❌ Health check failed")
            raise AssertionError("Health check failed")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        raise AssertionError(f"Health check error: {e}")
    
    # Step 2: Create a test evaluation query (simulating what pod_server sends)
    print("\n[Step 2] Preparing Evaluation Query")
    print("-" * 70)
    
    # Simulate a real submission
    test_title = "Test Scientific Paper on Fractal Quantum Structures"
    test_content = """
This paper introduces a novel approach to understanding fractal structures in quantum systems. 
We propose a hydrogen-holographic framework that links atomic geometry to cognitive fractal structures. 
Our model demonstrates coherence through recursive closure and phase alignment.

Key contributions:
1. Novel fractal grammar framework
2. Empirical validation of coherence metrics
3. Structural density calculations

The framework enables new forms of knowledge mining and structural truth validation.
"""
    
    evaluation_query = f"""
Artifact Content:
Title: {test_title}

Content:
{test_content}

FractiEmbedding Archive Results (from RAG):
[]

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

Evaluate this artifact using the HHFE model and provide:
1. Coherence (Φ): 0-10000
2. Density (ρ): 0-10000
3. Redundancy (R): 0-1 (based on similarity to archive)
4. Epoch Weight (W): typically 1.0
5. PoD Score (S): calculated using formula
6. Tier classification with justification
7. Epoch qualification
8. Full evaluation report
"""
    
    print(f"   Query length: {len(evaluation_query)} chars")
    print(f"   System prompt length: {len(POD_SYSTEM_PROMPT)} chars")
    
    # Step 3: Send query with progress updates
    print("\n[Step 3] Sending Evaluation Query to RAG API")
    print("-" * 70)
    print("   This simulates the actual submission flow...")
    print("   Using Ollama LLM (may take 30-120 seconds)")
    print("   Sending request...")
    
    try:
        query_payload = {
            "query": evaluation_query,
            "system_prompt": POD_SYSTEM_PROMPT,
            "top_k": 5,
            "llm_model": "ollama"  # Use ollama
        }
        
        start_time = time.time()
        
        # Show progress every 10 seconds
        print("   Waiting for response (showing progress every 10s)...")
        
        response = requests.post(
            f"{RAG_API_URL}/query",
            json=query_payload,
            timeout=180
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n   ✅ Response received!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Total Time: {elapsed:.2f} seconds ({elapsed/60:.1f} minutes)")
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            
            print(f"\n   Response Details:")
            print(f"   - Answer length: {len(answer)} characters")
            print(f"   - Sources: {len(result.get('sources', []))}")
            
            # Show preview
            if answer:
                preview = answer[:500] + "..." if len(answer) > 500 else answer
                print(f"\n   Answer Preview:")
                print(f"   {preview[:200]}...")
            
            # Try to extract JSON
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', answer, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    print(f"\n   ✅ Found valid JSON in response!")
                    print(f"   Keys: {list(json_data.keys())}")
                    if 'coherence' in json_data:
                        print(f"   Coherence: {json_data.get('coherence')}")
                    if 'density' in json_data:
                        print(f"   Density: {json_data.get('density')}")
                    if 'tier' in json_data:
                        print(f"   Tier: {json_data.get('tier')}")
                    if 'status' in json_data:
                        print(f"   Status: {json_data.get('status')}")
                except json.JSONDecodeError as e:
                    print(f"\n   ⚠️  JSON found but parse error: {e}")
            else:
                print(f"\n   ⚠️  No JSON found in response")

            # Test passed successfully
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            raise AssertionError(f"Query failed with status {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Query timed out after 180 seconds")
        print(f"   The RAG API may be overloaded or the LLM is taking too long")
        raise AssertionError("Query timed out after 180 seconds")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error")
        print(f"   Check if RAG API is running: curl http://localhost:8000/health")
        raise AssertionError("Connection error - RAG API not available")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise AssertionError(f"Unexpected error: {e}")

if __name__ == "__main__":
    try:
        test_submission_flow()
        print("\n" + "=" * 70)
        print("✅ Test completed successfully!")
        print("=" * 70)
        sys.exit(0)
    except AssertionError as e:
        print("\n" + "=" * 70)
        print("❌ Test failed - check errors above")
        print(f"Error: {e}")
        print("=" * 70)
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ Test failed - unexpected error")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        sys.exit(1)

