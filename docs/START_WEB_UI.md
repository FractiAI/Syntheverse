# Start Web UI for PoC Submissions

## Quick Start

The web UI is now running! 

### Access the Web Interface

🌐 **Open your browser and go to:**
```
http://localhost:5000
```

## What You Can Do

### 1. Submit Documents
- Upload PDF files directly in the browser
- Enter your Contributor ID
- Select category (Scientific/Tech/Alignment)
- Get instant PoC evaluation and scoring

### 2. View Epoch Status
- See current epoch and token balances
- View all 4 epochs (Founder, Pioneer, Community, Ecosystem)
- Monitor coherence density and halving count
- See available tiers per epoch

### 3. View Submissions
- See all submitted documents
- View evaluation scores (coherence, density, novelty)
- See token allocations if approved
- Track submission status

## Features

✅ **Modern Web Interface** - Clean, responsive design
✅ **Real-time Updates** - Auto-refreshes every 10 seconds
✅ **File Upload** - Drag and drop or click to select PDFs
✅ **Status Dashboard** - Comprehensive epoch and tokenomics view
✅ **Submission History** - All PoC submissions with details

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Troubleshooting

### Port Already in Use
If port 5000 is busy, edit `ui_web/app.py` and change:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
to a different port (e.g., `port=5001`)

### RAG API Not Running
The web UI will work but evaluations may be less accurate. Start RAG API:
```bash
cd rag-api/api && python rag_api.py
```

## Next Steps

1. Open http://localhost:5000 in your browser
2. Upload a PDF document
3. Enter your contributor ID
4. Select category and submit
5. View the results in the Status and Submissions tabs!

