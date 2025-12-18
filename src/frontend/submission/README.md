# PoD Submission UI

Basic HTML interface for submitting Proof-of-Discovery (PoD) contributions to Syntheverse.

## Status

🚧 **In Development** - Basic HTML scaffold created. The main web interface is implemented in `ui_web/` which provides full functionality.

## Current Implementation

This directory contains a basic HTML scaffold. For full PoD submission functionality, use the **Web UI** (`ui_web/`) which provides:
- Document upload
- Real-time evaluation
- Status tracking
- Email reports
- PoD certificates

## Features (Planned)

- Submit PoD discoveries
- Upload evidence and documentation
- Track submission status
- View evaluation results
- Check token rewards

## Technology Stack (Planned)

- **Frontend**: React/Vue.js (TBD)
- **Backend API**: Integration with Layer 2 evaluator via Web UI
- **Storage**: Integration with Layer 1 blockchain

## Usage

Currently, use the main Web UI:

```bash
cd ../ui_web
python app.py
```

Access at: http://localhost:5000

## Future Development

This UI will be developed as a standalone submission interface with:
- Simplified submission flow
- Mobile-friendly design
- Progressive Web App (PWA) support
- Offline submission queue

## Related

- [Web UI](../ui_web/README.md) - Full-featured web interface (recommended)
- [Layer 2](../layer2/README.md) - PoC evaluator backend
- [PoC Submission System](../docs/POC_SUBMISSION_SYSTEM.md) - Complete submission flow
