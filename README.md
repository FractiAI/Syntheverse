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
Scraper, Parser, Vectorizer, and RAG API using Groq (fast cloud LLM)
- **Scraper**: Downloads PDFs from Zenodo repositories
- **Parser**: Processes PDFs into searchable text chunks
- **Vectorizer**: Creates embeddings for semantic search
- **API**: FastAPI server with web UI for RAG queries
- **Integration**: Uses Groq API (primary), with Hugging Face and Ollama as fallbacks
- **AI System**: Unified Syntheverse Whole Brain AI (Gina × Leo × Pru) with full Hydrogen-Holographic Framework

### 2. **Layer 2** (`layer2/`)
POD Evaluator and Token Allocator
- **Evaluator**: Evaluates Proof-of-Discovery submissions
- **Allocator**: Calculates SYNTH token rewards based on evaluations
- **Integration**: Connects RAG API with Layer 1 blockchain

### 3. **Layer 1** (`layer1/`)
Syntheverse Blockchain for POD
- **Contracts**: Smart contracts for POD submissions and token management
- **Node**: Blockchain node implementation
- **Consensus**: Proof-of-Discovery consensus mechanism

### 4. **POD Submission UI** (`ui-submission/`)
Basic user interface for submitting POD discoveries
- Submit discoveries with evidence
- Track submission status
- View evaluation results and token rewards

### 5. **Admin UI** (`ui-admin/`)
Basic administrative interface
- Review and manage POD submissions
- Monitor evaluations and token allocations
- System statistics and contributor management

### 6. **Documentation** (`docs/`)
Supporting documentation
- **API**: API documentation and usage examples
- **Architecture**: System architecture and design documents
- **Deployment**: Deployment guides and configuration

---

### Legacy Components (from original structure)
* `core/` — Syntheverse game engine and AI modules
* `pod/` — Proof-of-Discovery protocol, validators, and scripts
* `tokenomics/` — SYNTH smart contracts, token distribution, and epoch rules
* `fractai/` — FractAI symbolic-cognitive updates and model outputs
* `submissions/` — Sample datasets, research contributions, and templates

---

## **Getting Started**

1. Clone the repository:

```bash
git clone https://github.com/FractiAI/Syntheverse.git
cd Syntheverse
```

2. **Set up RAG API** (Component 1):

```bash
# Install dependencies
cd rag-api/api
pip install -r requirements_api.txt

# Get free Groq API key from https://console.groq.com/
# Set environment variable
export GROQ_API_KEY="your-groq-api-key-here"

# Start the RAG API server
python rag_api.py
# Or use: ./start_rag_api.sh
```

Access the RAG API at: http://localhost:8000

**Note**: The RAG API uses Groq (fast, free cloud LLM) as the primary provider. See `rag-api/api/QUICK_START_GROQ.md` for setup instructions. Ollama and Hugging Face are available as fallbacks.

3. **Set up Layer 2** (Component 2):

```bash
cd layer2
# Install dependencies (create requirements.txt)
# Start evaluator and allocator services
```

4. **Set up Layer 1 Blockchain** (Component 3):

```bash
cd layer1
# Initialize and start blockchain node
```

5. **Launch UIs** (Components 4 & 5):

```bash
# POD Submission UI
cd ui-submission
python -m http.server 3000

# Admin UI (in another terminal)
cd ui-admin
python -m http.server 3001
```

6. Review documentation in `/docs/` for detailed setup and usage instructions.

7. Explore the PoD protocol and submit your first contribution for validation.

8. Contribute code, symbolic models, or experiments to expand the Syntheverse ecosystem.

---

## **Participation & Contribution**

* **Validate discoveries**: Submit research, symbolic insights, or experiments via the PoD system.
* **Earn SYNTH tokens**: Validated contributions accrue tokenized rewards in the first on-chain scientific, technological, AI, and alignment economy.
* **Collaborate**: Engage with other independent fractal, mythic, crypto, and AI frontiersmen to co-develop the Syntheverse ecosystem.

---

## **Prerelease & Testing**

Syntheverse is currently in **prerelease testing and tuning**. Early contributors help refine the game, PoD protocol, and tokenomics. The **full release date has not yet been announced**.

---

## **Component Status**

| Component | Status | Description |
|-----------|--------|-------------|
| RAG API | ✅ Operational | Fully functional with Groq integration, unified Syntheverse AI system prompt, scraper, parser, vectorizer, and web UI |
| Layer 2 | 🚧 In Development | Evaluator and allocator scaffolding created |
| Layer 1 | 🚧 In Development | Blockchain contracts and node scaffolding created |
| POD Submission UI | 🚧 In Development | Basic HTML interface created, backend integration pending |
| Admin UI | 🚧 In Development | Basic HTML interface created, backend integration pending |
| Documentation | ✅ Complete | Architecture, API, and deployment docs created |

## **Resources & Links**

* [Zenodo Community – Syntheverse Digital Home Base](#)
* [Whitepapers & Docs – HHF-AI and PoD Protocol](#)
* [Synthecoin Tokenomics & Epoch Guide](#)
* [Syntheverse Sandbox – Test Environment](#)
* [RAG API Documentation](rag-api/README.md)
* [Architecture Documentation](docs/architecture/README.md)
* [Deployment Guide](docs/deployment/README.md)

---

## **Join the Frontier**

Join as the **Outcast Hero Frontiersman** you already are. Explore, discover, contribute, and shape the **living Syntheverse ecosystem**. Every discovery expands the fractal awareness of the hydrogen-holographic frontier.


