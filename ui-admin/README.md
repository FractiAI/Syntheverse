# Admin UI

Basic administrative interface for managing Syntheverse PoD submissions, evaluations, and token allocations.

## Status

🚧 **In Development** - Basic HTML scaffold created. Administrative features are currently available through the main Web UI and CLI tools.

## Current Implementation

This directory contains a basic HTML scaffold. Administrative functionality is currently available through:
- **Web UI** (`ui_web/`) - View submissions and status
- **CLI Tools** - Direct access to Layer 1 and Layer 2 APIs
- **Layer 1 Node** - Blockchain management and statistics

## Features (Planned)

- View all PoD submissions
- Review and approve/reject submissions
- Monitor evaluation queue
- Manage token allocations
- View system statistics
- Manage contributors
- Epoch and tier management
- Tokenomics monitoring

## Technology Stack (Planned)

- **Frontend**: React/Vue.js (TBD)
- **Backend API**: FastAPI integration with Layer 2 components
- **Authentication**: Admin authentication and authorization
- **Dashboard**: Real-time statistics and monitoring

## Current Administrative Access

### Via Web UI
```bash
cd ../ui_web
python app.py
```
Access at: http://localhost:5000
- View all submissions
- See evaluation results
- Monitor epoch status

### Via CLI
```bash
# View Layer 1 statistics
cd ../layer1
python -c "from node import SyntheverseNode; n = SyntheverseNode(); print(n.get_node_status())"

# View Layer 2 statistics
cd ../layer2
python -c "from pod_server import PODServer; s = PODServer(); print(s.get_tokenomics_statistics())"
```

## Future Development

This UI will be developed as a comprehensive admin dashboard with:
- User management
- Submission moderation
- Token allocation management
- System configuration
- Analytics and reporting
- Audit logs

## Related

- [Web UI](../ui_web/README.md) - Current web interface
- [Layer 1](../layer1/README.md) - Blockchain management
- [Layer 2](../layer2/README.md) - PoD evaluator
- [Service Management](../SERVICE_MANAGEMENT.md) - Service control
