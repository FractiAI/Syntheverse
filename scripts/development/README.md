# Development Scripts

## Purpose

Scripts for development workflow, service management, and testing during development.

## Scripts

### Service Management

- **`start_poc_ui.sh`**: Start PoC UI development environment (Next.js frontend + PoC API)
- **`stop_poc_ui.sh`**: Stop PoC UI services
- **`start_all_services.sh`**: Start all system services (RAG API + Legacy Web UI)
- **`stop_all_services.sh`**: Stop all system services
- **`stop_Syntheverse.sh`**: Stop Syntheverse services
- **`Syntheverse.sh`**: Main Syntheverse startup script (Legacy Web UI)

### Testing and Submission

- **`submit_pod.py`**: Submit PoD for testing (legacy PoD system)
- **`ui_pod_submission.py`**: UI for PoD submission (legacy PoD system)

## Usage

### Start PoC UI Development Environment

```bash
cd scripts/development
./start_poc_ui.sh
```

This starts:
- PoC API on http://localhost:5001
- Next.js Frontend on http://localhost:3001

### Stop PoC UI Services

```bash
cd scripts/development
./stop_poc_ui.sh
```

### Start All Services (Legacy)

```bash
cd scripts/development
./start_all_services.sh
```

This starts:
- RAG API on http://localhost:8000
- Legacy Web UI on http://localhost:5000

### Submit Test Contribution (Legacy PoD)

```bash
cd scripts/development
python submit_pod.py --submit paper.pdf --contributor researcher-001 --category scientific
```

## Integration

- Scripts orchestrate multiple services
- Manage service lifecycle
- Support development workflow
- Enable testing and validation
- Paths are relative to project root (scripts navigate correctly)

