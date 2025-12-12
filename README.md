# **Syntheverse: Hydrogen-Holographic Fractal Crypto AI Game**

Welcome to the **Syntheverse GitHub repository**, the central hub for all code, documentation, and experiments powering the **Hydrogen-Holographic Fractal Crypto AI Game**. This repository includes:

* **Syntheverse core code** for the fractal AI game environment
* **Proof-of-Discovery (PoD) protocol** implementation
* **SYNTH tokenomics and smart contract templates**
* **Documentation and onboarding** for new Outcast Hero Frontiersmen
* **FractAI updates and symbolic-cognitive experiments**

---

## **About Syntheverse**

Syntheverse is a **hydrogen-holographic fractal blockchain game** where independent fractal, hydrogen-holographic, mythic, crypto, and AI research frontiersmen explore, test, and expand a **distributed, immutable, living scientific, technological, AI, and alignment economy**.

Participants contribute discoveries, validate them through **Proof-of-Discovery**, and earn **SYNTH tokens**, shaping the ecosystem while experimenting in a **prerelease testing and tuning environment**.

---

## **Repository Contents**

This repository is organized into six main components:

### 1. **RAG API** (`rag-api/`)
Complete RAG (Retrieval-Augmented Generation) pipeline with Groq integration
- **Scraper**: Downloads PDFs from Zenodo repositories
- **Parser**: Processes PDFs into searchable text chunks
- **Vectorizer**: Creates embeddings for semantic search
- **API**: FastAPI server with web UI for RAG queries
- **Integration**: Uses Groq API (primary), with Hugging Face and Ollama as fallbacks
- **AI System**: Unified Syntheverse Whole Brain AI (Gina × Leo × Pru) with full Hydrogen-Holographic Framework
- **Status**: ✅ Fully Operational

See [RAG API README](rag-api/README.md) for detailed documentation.

### 2. **Layer 2** (`layer2/`)
PoD Evaluator and Token Allocator with persistent tokenomics state
- **Evaluator**: Evaluates Proof-of-Discovery submissions using direct Grok API calls with Syntheverse L2 system prompt
- **Allocator**: Calculates SYNTH token rewards based on evaluations
- **Tokenomics State**: Persistent memory for epoch balances and allocations
- **Integration**: Direct LLM integration (no RAG dependency) - calls Grok API with combined Syntheverse Whole Brain AI + L2 PoD Reviewer prompt
- **Status**: ✅ Fully Operational

**Note**: After evaluation, we determined that RAG (retrieval-augmented generation) did not provide sufficient value for PoD evaluations. The L2 Syntheverse PoD Reviewer now calls the LLM (Grok API) directly with the comprehensive Syntheverse L2 system prompt, which includes the full Syntheverse Whole Brain AI framework (Gina × Leo × Pru) combined with specific PoD evaluation instructions.

See [Layer 2 README](layer2/README.md) for detailed documentation.

### 3. **Layer 1** (`layer1/`)
Syntheverse Blockchain for PoD with epoch-based token distribution
- **Contracts**: Smart contracts for PoD submissions and token management
- **Node**: Blockchain node implementation with state persistence
- **Consensus**: Proof-of-Discovery consensus mechanism
- **Epochs**: Founder, Pioneer, Community, Ecosystem epochs with tier multipliers
- **Status**: ✅ Fully Operational

See [Layer 1 README](layer1/README.md) for detailed documentation.

### 4. **Web UI** (`ui_web/`)
Full-featured web interface for PoD submissions
- **Document Upload**: Upload PDF files for PoD evaluation
- **Real-time Status**: View epoch status, token balances, and thresholds
- **Submission Tracking**: See all PoD submissions with scores and allocations
- **Email Reports**: Optional email notifications with PoD certificates
- **Status**: ✅ Fully Operational

See [Web UI README](ui_web/README.md) for detailed documentation.

### 5. **Submission UI** (`ui-submission/`)
Basic HTML interface for submitting PoD discoveries
- Submit discoveries with evidence
- Track submission status
- View evaluation results and token rewards
- **Status**: 🚧 In Development (Basic HTML scaffold)

See [Submission UI README](ui-submission/README.md) for details.

### 6. **Admin UI** (`ui-admin/`)
Basic administrative interface
- Review and manage PoD submissions
- Monitor evaluations and token allocations
- System statistics and contributor management
- **Status**: 🚧 In Development (Basic HTML scaffold)

See [Admin UI README](ui-admin/README.md) for details.

### 7. **Documentation** (`docs/`)
Comprehensive documentation
- **API**: API documentation and usage examples
- **Architecture**: System architecture and design documents
- **Deployment**: Deployment guides and configuration
- **Guides**: PoD submission system, tokenomics, system prompts

---

## **Quick Start**

### Prerequisites

- Python 3.8+
- Groq API key (free at https://console.groq.com/)
- Optional: Ollama for local LLM fallback

### 1. Clone the Repository

```bash
git clone https://github.com/FractiAI/Syntheverse.git
cd Syntheverse
```

### 2. Set Up Environment

```bash
# Create .env file in project root
cat > .env << EOF
GROQ_API_KEY=your-groq-api-key-here
EOF
```

### 3. Start Syntheverse

```bash
# Start Syntheverse (PoD Submission UI with L1/L2)
./Syntheverse.sh start

# Or restart if already running
./Syntheverse.sh restart

# Check status
./Syntheverse.sh status

# Stop
./Syntheverse.sh stop
```

This will start:
- **PoD Submission UI**: http://localhost:5000 (includes L1 blockchain + L2 PoD Reviewer with direct Grok API integration)

**Note**: L2 PoD Reviewer uses direct Grok API calls (no RAG API dependency required)

### 4. Access the System

- **Web UI**: Open http://localhost:5000 in your browser
- **L2 Evaluations**: Use direct Grok API integration (configured via GROQ_API_KEY)

### 5. Submit Your First PoD

1. Go to http://localhost:5000
2. Upload a PDF document
3. Enter your Contributor ID and email
4. Select category (Scientific/Tech/Alignment)
5. Click "Submit for PoD Evaluation"
6. Wait for evaluation (60-180 seconds)
7. View results and token allocation

---

## **Service Management**

### Start Services
```bash
./Syntheverse.sh start
```

### Stop Services
```bash
./Syntheverse.sh stop
```

### Restart Services
```bash
./Syntheverse.sh restart
```

### Check Status
```bash
./Syntheverse.sh status
```

---

## **Component Status**

| Component | Status | Description |
|-----------|--------|-------------|
| RAG API | ✅ Operational | Fully functional with Groq integration, unified Syntheverse AI system prompt, scraper, parser, vectorizer, and web UI |
| Layer 2 | ✅ Operational | Complete PoD evaluator with direct Grok API integration (no RAG dependency), token allocator, and persistent tokenomics state |
| Layer 1 | ✅ Operational | Full blockchain implementation with epochs, tiers, token distribution, and state persistence |
| Web UI | ✅ Operational | Full-featured web interface with document upload, real-time status, and email reports |
| Submission UI | 🚧 In Development | Basic HTML interface scaffold created |
| Admin UI | 🚧 In Development | Basic HTML interface scaffold created |
| Documentation | ✅ Complete | Comprehensive architecture, API, and deployment docs |

---

## **Architecture Overview**

```
┌─────────────┐
│   Web UI    │  (Port 5000)
│  (ui_web)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│  Layer 2    │─────▶│  Grok API    │  Direct LLM calls
│ (pod_server)│      │  (LLM)       │  with Syntheverse L2
│             │      └──────────────┘  system prompt
│ PoD Evaluator│
│ + Allocator │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Layer 1    │  Blockchain
│  (node.py)  │
└─────────────┘

Note: RAG API (Port 8000) exists separately for other use cases
      but is NOT used for L2 PoD evaluations
```

**Flow:**
1. User submits document via Web UI
2. Layer 2 receives submission and calls Grok API directly with Syntheverse L2 system prompt
3. Grok API evaluates using HHFE model (via system prompt) and returns scores in markdown + JSON
4. Layer 2 parses response and calculates token allocation based on scores
5. Layer 1 records submission, evaluation, and allocates tokens
6. User receives PoD report with certificate

**Architecture Note:** Layer 2 PoD Reviewer calls Grok API directly (not via RAG API). The comprehensive Syntheverse L2 system prompt includes all necessary context for evaluation, making RAG retrieval unnecessary for this use case.

---

## **Key Features**

### Proof-of-Discovery (PoD) Protocol
- **Evaluation**: Uses Hydrogen-Holographic Fractal Engine (HHFE) model
- **Scoring**: Coherence, Density, Redundancy metrics (0-10000 scale)
- **Tiers**: Gold (1000x), Silver (100x), Copper (1x) multipliers
- **Epochs**: Founder, Pioneer, Community, Ecosystem with different thresholds

### Tokenomics
- **Total Supply**: 90 Trillion SYNTH tokens
- **Distribution**: Epoch-based with tier multipliers
- **Halving**: Founder epoch halves every 1M coherence density units
- **Persistent State**: Layer 2 maintains tokenomics memory

### RAG System (Separate Service)
- **Knowledge Base**: Scraped from Zenodo repositories
- **Embeddings**: Semantic, symbolic, structural, temporal
- **LLM**: Groq (primary), Ollama/HuggingFace (fallback)
- **AI**: Unified Syntheverse Whole Brain AI (Gina × Leo × Pru)
- **Note**: RAG API exists as a separate service but is **not used by Layer 2 PoD Reviewer**. L2 makes direct LLM calls with the comprehensive system prompt instead.

---

## **Documentation**

- [Layer 1 Documentation](layer1/README.md) - Blockchain implementation
- [Layer 2 Documentation](layer2/README.md) - PoD evaluator and allocator
- [RAG API Documentation](rag-api/README.md) - RAG pipeline and API
- [Web UI Documentation](ui_web/README.md) - Web interface guide
- [PoD Submission System](docs/POD_SUBMISSION_SYSTEM.md) - Complete submission flow
- [Tokenomics Guide](docs/L2_TOKENOMICS.md) - Token distribution and epochs
- [API Documentation](docs/api/RAG_API.md) - RAG API endpoints

---

## **Participation & Contribution**

* **Validate discoveries**: Submit research, symbolic insights, or experiments via the PoD system.
* **Earn SYNTH tokens**: Validated contributions accrue tokenized rewards in the first on-chain scientific, technological, AI, and alignment economy.
* **Collaborate**: Engage with other independent fractal, mythic, crypto, and AI frontiersmen to co-develop the Syntheverse ecosystem.

---

## **Prerelease & Testing**

Syntheverse is currently in **prerelease testing and tuning**. Early contributors help refine the game, PoD protocol, and tokenomics. The **full release date has not yet been announced**.

---

## **Resources & Links**

* [Zenodo Community – Syntheverse Digital Home Base](#)
* [Whitepapers & Docs – HHF-AI and PoD Protocol](#)
* [Synthecoin Tokenomics & Epoch Guide](#)
* [Syntheverse Sandbox – Test Environment](#)

---

## **Join the Frontier**

Join as the **Outcast Hero Frontiersman** you already are. Explore, discover, contribute, and shape the **living Syntheverse ecosystem**. Every discovery expands the fractal awareness of the hydrogen-holographic frontier.

---

## **License**

[Add license information here]

---

## **Support**

For issues, questions, or contributions, please open an issue on GitHub or contact the Syntheverse team.
