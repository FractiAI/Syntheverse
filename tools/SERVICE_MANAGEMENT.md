# Syntheverse Service Management

## Quick Commands

### Start All Services
```bash
./start_all_services.sh start
```

### Stop All Services
```bash
./stop_all_services.sh
```

### Restart All Services
```bash
./start_all_services.sh restart
```

### Check Status
```bash
./start_all_services.sh status
```

## Services Managed

1. **RAG API Server** (Port 8000)
   - Handles PoD evaluations using the Syntheverse RAG API
   - Health check: http://localhost:8000/health
   - Logs: `/tmp/syntheverse_rag_api.log`

2. **PoD Submission UI** (Port 5000)
   - Web interface for submitting documents
   - Includes L1 (Blockchain) and L2 (PoD Server) components
   - UI: http://localhost:5000
   - Logs: `/tmp/syntheverse_pod_ui.log`

## Architecture

```
┌─────────────────┐
│  PoD UI (5000)  │  ← User Interface
│  (Flask)        │
└────────┬────────┘
         │
         ├──→ L1 Blockchain (SyntheverseNode)
         │    - Blocks, Transactions
         │    - SYNTH Token Contract
         │    - PoD Contract
         │
         └──→ L2 PoD Server
              │
              └──→ RAG API (8000)
                   - Evaluation
                   - Knowledge Base
```

## Troubleshooting

### Services Won't Start

1. **Check if ports are in use:**
   ```bash
   lsof -i:5000
   lsof -i:8000
   ```

2. **Check logs:**
   ```bash
   tail -f /tmp/syntheverse_rag_api.log
   tail -f /tmp/syntheverse_pod_ui.log
   ```

3. **Manual start (for debugging):**
   ```bash
   # RAG API
   cd rag-api/api
   python3 rag_api.py
   
   # PoD UI (in another terminal)
   cd ui_web
   python3 app.py
   ```

### Service Hanging

If a submission seems to hang:

1. **Check RAG API is responding:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check server logs** for timeout or error messages

3. **Restart services:**
   ```bash
   ./start_all_services.sh restart
   ```

## Service Dependencies

- **PoD UI** depends on **RAG API** for evaluations
- Start order: RAG API first, then PoD UI
- The script handles this automatically

## Notes

- L1 and L2 are integrated into the PoD UI process (not separate servers)
- All blockchain and PoD server logic runs within the Flask app
- Services run in background with logs in `/tmp/`

