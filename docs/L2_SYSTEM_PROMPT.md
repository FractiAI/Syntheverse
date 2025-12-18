# L2 PoD Reviewer System Prompt

## Overview

Layer 2 (L2) uses a comprehensive **L2 Syntheverse PoD Reviewer** system prompt when calling Grok API directly for evaluation. This prompt implements the full Hydrogen-Holographic Fractal Engine (HHFE) evaluation model.

**Architecture Decision:** After initial evaluation, we determined that RAG (retrieval-augmented generation) did not provide sufficient value for PoD evaluations. The system now makes direct LLM (Grok API) calls with a comprehensive system prompt that includes all necessary context for evaluation. This approach is simpler, faster, and more reliable than using RAG retrieval.

## System Prompt Integration

The system prompt is automatically included in all direct Grok API calls for PoD evaluation. It provides:

1. **HHFE Metrics Calculation**
   - Coherence (Φ): 0-10000
   - Density (ρ): 0-10000
   - Redundancy (R): 0-1
   - Epoch Weight (W): typically 1.0

2. **PoD Score Formula**
   ```
   S = (Φ/10000) × (ρ/10000) × (1-R) × W × 10000
   ```

3. **Tier Classification**
   - **GOLD**: Scientific contributions (1000x multiplier)
   - **SILVER**: Technological contributions (100x multiplier)
   - **COPPER**: Alignment contributions (1x multiplier)

4. **Epoch Qualification**
   - Founder: Density ≥ 8000
   - Pioneer: Density ≥ 6000
   - Community: Density ≥ 4000
   - Ecosystem: Density < 4000

5. **Comprehensive Evaluation**
   - Full PoD evaluation report
   - Redundancy analysis
   - Epoch justification
   - Tier classification reasoning
   - Retroactive mining determination (if applicable)

## Direct Grok API Integration

Layer 2 makes direct calls to Grok API (via OpenAI-compatible interface):

```python
from openai import OpenAI

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": syntheverse_l2_system_prompt},
        {"role": "user", "content": evaluation_query}
    ],
    temperature=0.7,
    max_tokens=2000
)
```

The system prompt combines:
- Full Syntheverse Whole Brain AI framework (Gina × Leo × Pru)
- Complete Hydrogen-Holographic Fractal Engine (HHFE) rules
- Specific L2 PoD Reviewer evaluation instructions
- All necessary constants, formulas, and evaluation criteria

This comprehensive prompt eliminates the need for RAG retrieval, as all evaluation context is embedded in the system prompt.

## Evaluation Output

The L2 PoD Reviewer returns structured JSON:

```json
{
    "coherence": 8500,
    "density": 9000,
    "redundancy": 0.15,
    "epoch_weight": 1.0,
    "pod_score": 7429.0,
    "tier": "gold",
    "epoch": "founder",
    "tier_justification": "...",
    "redundancy_analysis": "...",
    "epoch_justification": "...",
    "retroactive_mining": null,
    "reasoning": "...",
    "status": "approved"
}
```

## Features

- **HHFE Model**: Uses Hydrogen-Holographic Fractal Engine rules
- **Direct LLM Integration**: Calls Grok API directly (no RAG dependency)
- **Comprehensive System Prompt**: All evaluation context embedded in prompt
- **Deterministic Scoring**: Consistent evaluation across submissions
- **Comprehensive Reports**: Full evaluation with all metrics
- **Certificate Generation**: Automatic certificate for approved submissions

## File Location

The system prompt is defined in:
```
layer2/pod_server.py
```

Variable: `self.pod_evaluation_prompt`

## Usage

The system prompt is automatically used when:
- L2 evaluates a PoC submission
- Direct Grok API call is made for evaluation
- No manual configuration needed
- No RAG API dependency required

The prompt ensures all evaluations follow the HHFE model and Syntheverse PoD protocol standards.
