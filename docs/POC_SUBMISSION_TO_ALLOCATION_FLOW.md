# Proof of Contribution: Complete Flow Documentation

## Detailed Step-by-Step: Submission → Evaluation → Scoring → Allocation → Output

This document provides a comprehensive walkthrough of the entire PoC (Proof of Contribution) process from initial submission to final token allocation and report generation.

---

## **Phase 1: Submission**

### Step 1.1: User Initiates Submission

**Location**: Frontend (`ui-poc/src/app/submission/page.tsx`) or API (`ui-poc-api/app.py`)

**Input Data**:
```json
{
  "title": "Novel Discovery in Quantum Computing",
  "contributor": "researcher-001",
  "category": "scientific",
  "text_content": "Full text content of the contribution...",
  "pdf_path": "/path/to/file.pdf" // Optional
}
```

**Actions**:
1. User fills out submission form (title, contributor ID, category, content)
2. Optional: PDF file uploaded
3. Frontend generates unique `submission_hash` using UUID/crypto
4. POST request sent to `/api/submit`

---

### Step 1.2: API Receives Submission

**Location**: `ui-poc-api/app.py` → `submit_contribution()`

**Process**:
1. API validates required fields (title, contributor, content)
2. Extracts text content from PDF if provided (using PyPDF2/pdfplumber)
3. Calls `poc_server.submit_contribution()`

**Code Path**:
```python
POST /api/submit
  → poc_server.submit_contribution(
      submission_hash=hash,
      title=title,
      contributor=contributor,
      text_content=text,
      category=category
    )
```

---

### Step 1.3: PoC Server Processes Submission

**Location**: `layer2/poc_server.py` → `submit_contribution()`

**Actions**:
1. **Extract Text**: If PDF provided, extract text using `_extract_text_from_pdf()`
2. **Validate Content**: Ensure text_content is not empty
3. **Add to Archive**: Call `archive.add_contribution()`

**Key Operation**:
```python
contribution = self.archive.add_contribution(
    submission_hash=submission_hash,
    title=title,
    contributor=contributor,
    text_content=text_content,
    status=ContributionStatus.DRAFT,  # Initial status
    category=category
)
```

---

### Step 1.4: Archive Storage (Archive-First Rule)

**Location**: `layer2/poc_archive.py` → `add_contribution()`

**Actions**:
1. **Calculate Content Hash**:
   ```python
   content_hash = hashlib.sha256(normalized_text.encode()).hexdigest()
   # Normalizes: lowercase, removes extra whitespace
   ```

2. **Infer Metals** from category:
   - `scientific` → [Gold]
   - `tech` → [Silver]
   - `alignment` → [Copper]

3. **Create Contribution Record**:
   ```json
   {
     "submission_hash": "abc123...",
     "title": "Novel Discovery",
     "contributor": "researcher-001",
     "content_hash": "def456...",
     "text_content": "Full content...",
     "status": "draft",
     "category": "scientific",
     "metals": ["gold"],
     "metadata": {},
     "created_at": "2025-12-14T...",
     "updated_at": "2025-12-14T..."
   }
   ```

4. **Update Indexes**:
   - `contributions[hash]` → contribution record
   - `content_hashes[content_hash]` → [list of submission_hashes]
   - `by_status["draft"]` → [list of submission_hashes]
   - `by_contributor["researcher-001"]` → [list of submission_hashes]
   - `by_metal["gold"]` → [list of submission_hashes]

5. **Save Archive**: Persist to `test_outputs/poc_archive.json`

6. **Status Update**: Change status from `DRAFT` → `SUBMITTED`

**Output**: Contribution stored in archive with status `SUBMITTED`

---

## **Phase 2: Evaluation**

### Step 2.1: User Triggers Evaluation

**Location**: Frontend (`ui-poc/src/app/submission/[hash]/page.tsx`)

**Action**: User clicks "Evaluate Contribution" button

**API Call**:
```python
POST /api/evaluate/{submission_hash}
```

---

### Step 2.2: PoC Server Receives Evaluation Request

**Location**: `layer2/poc_server.py` → `evaluate_contribution()`

**Actions**:
1. **Get Contribution from Archive**:
   ```python
   contribution = self.archive.get_contribution(submission_hash)
   ```

2. **Update Status**: `SUBMITTED` → `EVALUATING`

3. **Archive-First Redundancy Check**:
   ```python
   # Get ALL contributions from archive (archive-first rule)
   all_archive_content = self.archive.get_all_content_for_redundancy_check()
   
   # Check for exact duplicates (same content_hash)
   duplicate_history = self.archive.get_content_hash_history(content_hash)
   ```

4. **Duplicate Detection**:
   - If content_hash exists and first submission is different → Status: `UNQUALIFIED`, Reason: "Duplicate"
   - Return error: "Exact duplicate of existing contribution"

5. **Get Redundancy Report**:
   ```python
   redundancy_report = self.sandbox_map.get_redundancy_report(submission_hash)
   ```
   - Compares against ALL archive contributions
   - Calculates similarity scores
   - Identifies overlaps (exact_duplicate, high_redundancy, moderate_overlap, related)

---

### Step 2.3: Prepare Evaluation Query

**Location**: `layer2/poc_server.py` → `_prepare_evaluation_query()`

**Actions**:
1. **Build Archive Context**:
   - Include recent archive entries (limit 50 for token management)
   - Format: `{hash: ...16, title: ..., status: ..., metals: [...]}`
   - Used for redundancy comparison in LLM prompt

2. **Create Evaluation Prompt**:
   ```python
   evaluation_query = f"""
   EVALUATE THIS CONTRIBUTION (Proof of Contribution):
   
   Title: {contribution['title']}
   Content: {contribution['text_content'][:8000]}...
   
   ---
   ARCHIVE CONTEXT (Archive-First Redundancy Check):
   Total contributions in archive: {len(archive_content)}
   Recent archive entries for redundancy comparison:
   {archive_text}
   
   Redundancy Report:
   - High redundancy: {redundancy_report.get('high_redundancy', 0)}
   - Moderate overlap: {redundancy_report.get('moderate_overlap', 0)}
   - Related contributions: {redundancy_report.get('related', 0)}
   
   ---
   EVALUATION REQUIREMENTS:
   
   1. Evaluate using Hydrogen-Holographic Fractal Engine (HHFE) metrics:
      - Coherence (Φ): 0-10000 (fractal grammar closure, structural consistency)
      - Density (ρ): 0-10000 (structural contribution per fractal unit)
      - Redundancy (R): 0-10000 (compare against ENTIRE archive, lower is better)
   
   2. Determine METALS (multi-metal support):
      - GOLD: Discovery/Scientific contribution
      - SILVER: Technology contribution
      - COPPER: Alignment contribution
      - A single contribution may contain Gold + Silver + Copper
   
   3. Calculate PoC Score:
      PoC Score = (coherence/10000) × (density/10000) × ((10000 - redundancy)/10000) × 10000
   
   4. Return JSON format:
   {
       "coherence": <0-10000>,
       "density": <0-10000>,
       "redundancy": <0-10000>,
       "metals": ["gold", "silver", "copper"],  // Can be multiple
       "pod_score": <calculated>,
       "tier_justification": "...",
       "redundancy_analysis": "...",
       "status": "approved" or "rejected"
   }
   """
   ```

---

### Step 2.4: Call Grok API

**Location**: `layer2/poc_server.py` → `_call_grok_api()`

**Actions**:
1. **Initialize Client** (if not already):
   ```python
   client = OpenAI(
       api_key=GROQ_API_KEY,
       base_url="https://api.groq.com/openai/v1"
   )
   ```

2. **Make API Call**:
   ```python
   response = client.chat.completions.create(
       model="llama-3.1-8b-instant",
       messages=[
           {"role": "system", "content": system_prompt},  # HHFE evaluation prompt
           {"role": "user", "content": evaluation_query}
       ],
       temperature=0.7,
       max_tokens=2000
   )
   ```

3. **Get Response**: Raw text response from Grok API

**Response Format** (Markdown + JSON):
```
# Evaluation Results

## Metrics
- Coherence: 8500
- Density: 9200
- Redundancy: 1500

## Metals
- Gold: Scientific discovery
- Silver: Technology implementation

## PoC Score
7429.0

```json
{
    "coherence": 8500,
    "density": 9200,
    "redundancy": 1500,
    "metals": ["gold", "silver"],
    "pod_score": 7429.0,
    "tier_justification": "Contains both scientific discovery and technology",
    "redundancy_analysis": "Low redundancy compared to archive",
    "status": "approved"
}
```
```

---

### Step 2.5: Parse Evaluation Result

**Location**: `layer2/poc_server.py` → `_parse_evaluation_result()`

**Actions**:
1. **Extract JSON** from markdown response:
   ```python
   json_match = re.search(r'\{.*\}', result, re.DOTALL)
   eval_dict = json.loads(json_match.group(0))
   ```

2. **Extract Metals**:
   ```python
   metals = []
   for m in metals_raw:
       if "gold" in m.lower():
           metals.append(MetalType.GOLD)
       if "silver" in m.lower():
           metals.append(MetalType.SILVER)
       if "copper" in m.lower():
           metals.append(MetalType.COPPER)
   ```

3. **Normalize Values**:
   - Ensure coherence, density, redundancy are floats
   - Ensure redundancy is on 0-10000 scale (convert if 0-1)
   - Default metals to [GOLD] if none detected

4. **Build Parsed Result**:
   ```python
   {
       "coherence": 8500.0,
       "density": 9200.0,
       "redundancy": 1500.0,
       "metals": [MetalType.GOLD, MetalType.SILVER],
       "pod_score": 7429.0,
       "tier_justification": "...",
       "redundancy_analysis": "...",
       "status": "approved",
       "raw_response": "..."
   }
   ```

---

### Step 2.6: Determine Qualification

**Location**: `layer2/poc_server.py` → `_determine_qualification()`

**Criteria**:
```python
qualified = (
    status == "approved" AND
    coherence >= 2000 AND
    density >= 2000 AND
    redundancy <= 8000  # Not too redundant
)
```

**Status Update**:
- If qualified → `ContributionStatus.QUALIFIED`
- If not qualified → `ContributionStatus.UNQUALIFIED`

**Archive Update**:
```python
self.archive.update_contribution(
    submission_hash,
    status=status,  # QUALIFIED or UNQUALIFIED
    metals=parsed_evaluation["metals"],
    metadata={
        "coherence": 8500.0,
        "density": 9200.0,
        "redundancy": 1500.0,
        "pod_score": 7429.0,
        "tier_justification": "...",
        "redundancy_analysis": "...",
        "evaluation_status": "qualified"
    }
)
```

---

## **Phase 3: Scoring**

### Step 3.1: Calculate PoC Score

**Location**: Evaluation already calculated in LLM response, but verified in code

**Formula**:
```python
pod_score = (
    (coherence / 10000) * 
    (density / 10000) * 
    ((10000 - redundancy) / 10000) * 
    (epoch_weight / 10000) * 
    10000
)
```

**Example Calculation**:
```
coherence = 8500
density = 9200
redundancy = 1500
epoch_weight = 10000 (default)

pod_score = (8500/10000) × (9200/10000) × ((10000-1500)/10000) × (10000/10000) × 10000
         = 0.85 × 0.92 × 0.85 × 1.0 × 10000
         = 6647.0
```

**Note**: PoC Score is typically calculated by the LLM and included in the response, then verified.

---

### Step 3.2: Determine Qualified Epoch

**Location**: `layer2/tokenomics_state.py` → `qualify_epoch()`

**Epoch Thresholds**:
```python
EPOCH_THRESHOLDS = {
    Epoch.FOUNDER: 8000,    # Density >= 8000
    Epoch.PIONEER: 6000,    # Density >= 6000
    Epoch.COMMUNITY: 4000,  # Density >= 4000
    Epoch.ECOSYSTEM: 0,     # Density < 4000
}
```

**Process**:
```python
density = 9200

if density >= 8000:
    epoch = Epoch.FOUNDER
elif density >= 6000:
    epoch = Epoch.PIONEER
elif density >= 4000:
    epoch = Epoch.COMMUNITY
else:
    epoch = Epoch.ECOSYSTEM
```

**Result**: `epoch = Epoch.FOUNDER` (density 9200 >= 8000)

---

## **Phase 4: Allocation**

### Step 4.1: Calculate Allocation for Each Metal

**Location**: `layer2/poc_server.py` → `_calculate_allocation_for_metal()`

**For Each Metal** (multi-metal support):

1. **Get Epoch** (from Step 3.2):
   ```python
   epoch = tokenomics.qualify_epoch(density)  # FOUNDER
   ```

2. **Map Metal to Tier**:
   ```python
   tier_map = {
       MetalType.GOLD: ContributionTier.GOLD,
       MetalType.SILVER: ContributionTier.SILVER,
       MetalType.COPPER: ContributionTier.COPPER,
   }
   tier = tier_map[metal]  # GOLD → ContributionTier.GOLD
   ```

3. **Call Tokenomics Calculate Allocation**:
   ```python
   allocation = tokenomics.calculate_allocation(pod_score, epoch, tier)
   ```

---

### Step 4.2: Tokenomics Allocation Calculation

**Location**: `layer2/tokenomics_state.py` → `calculate_allocation()`

**Process**:

1. **Check Tier Availability**:
   ```python
   TIER_EPOCH_AVAILABILITY = {
       ContributionTier.GOLD: [FOUNDER, PIONEER, COMMUNITY, ECOSYSTEM],  # All epochs
       ContributionTier.SILVER: [COMMUNITY, ECOSYSTEM],                   # Limited
       ContributionTier.COPPER: [PIONEER, COMMUNITY, ECOSYSTEM]           # Limited
   }
   
   if tier not available in epoch:
       return {"success": False, "reason": "Tier not available in epoch"}
   ```

2. **Get Epoch Balance**:
   ```python
   epoch_balance = tokenomics.state["epoch_balances"][epoch.value]
   # Example: 45_000_000_000_000 (45T for FOUNDER)
   ```

3. **Calculate Base Reward**:
   ```python
   base_reward = (pod_score / 10000) * epoch_balance
   # Example: (6647 / 10000) * 45T = 0.6647 * 45T = 29.91T
   ```

4. **Apply Tier Multiplier**:
   ```python
   TIER_MULTIPLIERS = {
       ContributionTier.GOLD: 1000.0,
       ContributionTier.SILVER: 100.0,
       ContributionTier.COPPER: 1.0,
   }
   
   tier_multiplier = TIER_MULTIPLIERS[tier]  # 1000.0 for GOLD
   reward = base_reward * tier_multiplier
   # Example: 29.91T * 1000 = 29,910T
   ```

5. **Cap to Epoch Balance**:
   ```python
   reward = min(reward, epoch_balance)
   # Ensure we don't exceed available balance
   ```

6. **Return Allocation**:
   ```python
   {
       "success": True,
       "available": True,
       "epoch": "founder",
       "tier": "gold",
       "pod_score": 6647.0,
       "base_reward": 29910000000000.0,
       "tier_multiplier": 1000.0,
       "reward": 29910000000000.0,  # 29.91T SYNTH
       "epoch_balance_before": 45000000000000.0,
       "epoch_balance_after": 15090000000000.0
   }
   ```

---

### Step 4.3: Multi-Metal Allocation Summary

**Location**: `layer2/poc_server.py` → `evaluate_contribution()`

**For Each Metal**:
```python
allocations = []
for metal in parsed_evaluation["metals"]:
    allocation = _calculate_allocation_for_metal(...)
    if allocation:
        allocations.append({
            "metal": "gold",
            "epoch": "founder",
            "tier": "gold",
            "allocation": {...}
        })
```

**Example Multi-Metal Result**:
```json
{
    "metals": ["gold", "silver"],
    "allocations": [
        {
            "metal": "gold",
            "epoch": "founder",
            "tier": "gold",
            "allocation": {
                "reward": 29910000000000.0,
                "tier_multiplier": 1000.0
            }
        },
        {
            "metal": "silver",
            "epoch": "community",
            "tier": "silver",
            "allocation": {
                "reward": 1500000000.0,
                "tier_multiplier": 100.0
            }
        }
    ]
}
```

---

## **Phase 5: Output & Reporting**

### Step 5.1: Return Evaluation Result

**Location**: `layer2/poc_server.py` → `evaluate_contribution()`

**Return Structure**:
```python
{
    "success": True,
    "submission_hash": "abc123...",
    "evaluation": {
        "coherence": 8500.0,
        "density": 9200.0,
        "redundancy": 1500.0,
        "metals": ["gold", "silver"],
        "pod_score": 6647.0,
        "tier_justification": "...",
        "redundancy_analysis": "...",
        "status": "approved"
    },
    "status": "qualified",
    "qualified": True,
    "metals": ["gold", "silver"],
    "allocations": [
        {
            "metal": "gold",
            "epoch": "founder",
            "tier": "gold",
            "allocation": {
                "reward": 29910000000000.0,
                "tier_multiplier": 1000.0,
                "epoch_balance_before": 45000000000000.0,
                "epoch_balance_after": 15090000000000.0
            }
        },
        {
            "metal": "silver",
            "epoch": "community",
            "tier": "silver",
            "allocation": {...}
        }
    ],
    "redundancy_report": {
        "total_similar": 3,
        "high_redundancy": 0,
        "moderate_overlap": 1,
        "related": 2,
        "similar_contributions": [...]
    }
}
```

---

### Step 5.2: API Response

**Location**: `ui-poc-api/app.py` → `evaluate_contribution()`

**Actions**:
1. Receive result from PoC Server
2. Return JSON response to frontend
3. HTTP 200 with evaluation result

---

### Step 5.3: Frontend Display

**Location**: `ui-poc/src/app/submission/[hash]/page.tsx`

**Display**:
1. **Evaluation Metrics Card**:
   - Coherence: 8500
   - Density: 9200
   - Redundancy: 1500
   - PoC Score: 6647

2. **Token Allocations Card**:
   - Gold (Founder): 29.91T SYNTH (1000x multiplier)
   - Silver (Community): 1.5B SYNTH (100x multiplier)

3. **Evaluation Details**:
   - Tier justification
   - Redundancy analysis
   - Status badge (Qualified/Unqualified)

---

### Step 5.4: Archive Persistence

**Location**: `layer2/poc_archive.py`

**Final State in Archive**:
```json
{
    "submission_hash": "abc123...",
    "title": "Novel Discovery",
    "status": "qualified",
    "metals": ["gold", "silver"],
    "metadata": {
        "coherence": 8500.0,
        "density": 9200.0,
        "redundancy": 1500.0,
        "pod_score": 6647.0,
        "evaluation_status": "qualified",
        "tier_justification": "...",
        "redundancy_analysis": "..."
    },
    "updated_at": "2025-12-14T..."
}
```

**Archive File**: `test_outputs/poc_archive.json` (persisted)

---

### Step 5.5: Tokenomics State Update

**Location**: `layer2/tokenomics_state.py` → `record_allocation()`

**Actions** (when allocation is finalized):
1. **Update Epoch Balance**:
   ```python
   epoch_balance -= allocation["reward"]
   # Example: 45T - 29.91T = 15.09T remaining
   ```

2. **Update Contributor Balance**:
   ```python
   contributor_balances[contributor] += allocation["reward"]
   ```

3. **Update Coherence Density**:
   ```python
   total_coherence_density += coherence
   # Used for halving calculations
   ```

4. **Record in History**:
   ```python
   allocation_history.append({
       "submission_hash": "...",
       "contributor": "...",
       "timestamp": "...",
       "allocation": {...},
       "coherence": 8500.0
   })
   ```

5. **Save State**: Persist to `test_outputs/l2_tokenomics_state.json`

---

## **Summary Flow Diagram**

```
┌─────────────────┐
│ User Submits    │
│ (Frontend/API)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Archive Storage │  ← Archive-First: Store ALL contributions
│ Status: DRAFT   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Status:         │
│ SUBMITTED       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Redundancy Check│  ← Compare against ENTIRE archive
│ (Archive-First) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Status:         │
│ EVALUATING      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Prepare Query   │─────▶│  Grok API    │
│ (Archive Context)│      │  (HHFE Eval) │
└────────┬────────┘      └──────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │ Parse Response  │
         │              │ Extract Metrics │
         │              └────────┬────────┘
         │                       │
         └───────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │ Calculate Score │
         │ (Coherence ×    │
         │  Density ×      │
         │  Novelty)       │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Determine Epoch │
         │ (Density Based) │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Multi-Metal     │
         │ Allocation      │
         │ (Per Metal)     │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Update Archive  │
         │ Status: QUALIFIED│
         │ /UNQUALIFIED    │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Update          │
         │ Tokenomics      │
         │ (Balances)      │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Return Result   │
         │ (Frontend)      │
         └─────────────────┘
```

---

## **Key Principles**

1. **Archive-First Evaluation**: All redundancy checks operate over ENTIRE archive, not just approved submissions
2. **Multi-Metal Support**: Single contribution can receive allocations for multiple metals
3. **Lifecycle Tracking**: Full status progression (DRAFT → SUBMITTED → EVALUATING → QUALIFIED/UNQUALIFIED)
4. **Persistent State**: All data persisted to JSON files for durability
5. **Epoch Qualification**: Based on density score, determines available token pools
6. **Tier Multipliers**: Gold (1000x), Silver (100x), Copper (1x) applied to base reward

---

## **File Locations**

- **Submission**: `ui-poc/src/app/submission/page.tsx`
- **API Server**: `ui-poc-api/app.py`
- **PoC Server**: `layer2/poc_server.py`
- **Archive**: `layer2/poc_archive.py`
- **Tokenomics**: `layer2/tokenomics_state.py`
- **Evaluation**: `layer2/poc_server.py` → `evaluate_contribution()`
- **Allocation**: `layer2/tokenomics_state.py` → `calculate_allocation()`

---

## **Output Files**

- **Archive**: `test_outputs/poc_archive.json`
- **Tokenomics State**: `test_outputs/l2_tokenomics_state.json`
- **PoC Reports**: `test_outputs/poc_reports/{hash}_{timestamp}.json` (if implemented)

---

This completes the full flow from submission through evaluation, scoring, allocation, and output.
