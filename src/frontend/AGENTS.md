# Frontend Agents

## Purpose

The `frontend/` directory contains all frontend applications for the Syntheverse system.

## Key Modules

### PoC Frontend (`poc-frontend/`)

Next.js 14 application with App Router:
- **Dashboard**: System statistics and overview
- **Submission**: Contribution submission interface
- **Explorer**: Contribution browsing and filtering
- **Registry**: Chronological contribution timeline
- **Sandbox Map**: Interactive network visualization

**Technology Stack:**
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- shadcn/ui components
- vis-network for graph visualization

### Legacy Web (`web-legacy/`)

Flask web interface (legacy):
- Full-featured PoD/PoT/PoA submission system
- Real-time status display
- Certificate registration
- Artifact viewing

### Submission UI (`submission/`)

Basic HTML interface for submissions

### Admin UI (`admin/`)

Administrative interface for system management

## Integration Points

- PoC Frontend connects to PoC API (Flask)
- APIs provide REST endpoints for data
- Web3 integration for blockchain registration
- Real-time updates via polling

## Development Guidelines

### Next.js Patterns

- Use Server Components by default
- Mark Client Components with `'use client'`
- Use App Router file-based routing
- Implement proper error boundaries

### API Integration

- Create API client utilities in `lib/`
- Handle loading and error states
- Implement retry logic
- Cache responses appropriately

### State Management

- Use React hooks for local state
- Use Context API for shared state
- Minimize prop drilling
- Keep state close to usage

## Common Patterns

- Component composition with shadcn/ui
- Tailwind CSS for styling
- TypeScript for type safety
- API client pattern for backend communication
- Real-time updates via polling

## File Structure

```
frontend/
├── poc-frontend/             # Main Next.js application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # Reusable components
│   │   └── lib/             # Utilities and API clients
│   ├── package.json
│   └── tailwind.config.js
├── web-legacy/               # Legacy Flask interface
│   └── templates/            # Jinja2 templates
├── submission/               # Basic submission interface
│   └── src/                  # HTML/CSS/JS
├── admin/                    # Admin interface
│   └── src/                  # Admin components
└── ui_web/                   # Additional web interfaces
```

## Ports & Access

| Application | Port | Purpose |
|-------------|------|---------|
| PoC Frontend | 3001 | Main dashboard and submission |
| Legacy Web | 5002 | Legacy Flask interface |
| Admin UI | - | Administrative functions |

## Blueprint Alignment

### UI Layer Implementation ([Blueprint §3](docs/Blueprint for Syntheverse))
- **Next.js Dashboard**: `poc-frontend/` implements the main user interface with modern React architecture
- **Flask API Bridge**: `web-legacy/` provides legacy compatibility and additional interface options
- **Multi-Interface Support**: Comprehensive frontend ecosystem supporting various user interaction patterns

### Dashboard Interaction ([Blueprint §1.5](docs/Blueprint for Syntheverse))
- **PoC Archive Exploration**: Browse contributions, scores, and metallic amplifications through interactive interfaces
- **Ecosystem Impact Visualization**: Dashboard displays contribution networks and system-wide effects
- **Real-time Updates**: Live status tracking of submissions, evaluations, and allocations
- **Multi-Metal Display**: Visual representation of Gold/Silver/Copper qualifications and rewards

### Experience Walkthrough Implementation ([Blueprint §1](docs/Blueprint for Syntheverse))
- **Submission Interface**: `poc-frontend/` submission pages enable contribution uploads and initial processing
- **Evaluation Display**: Real-time status updates showing hydrogen holographic scoring progress
- **Registration Portal**: Web3 integration for $200 on-chain registration and "I was here first" recognition
- **Tier Participation**: Interface foundation for Copper/Silver/Gold alignment contribution options

### Complete Workflow Support ([Blueprint §7](docs/Blueprint for Syntheverse))
1. **Community Discovery**: Interface guides users from Zenodo communities to Syntheverse ecosystem
2. **PoC Submission**: Intuitive forms for contribution uploads and metadata collection
3. **Evaluation Monitoring**: Live dashboards showing evaluation progress and dimensional scores
4. **Human Review**: Status displays for approval workflow and ecosystem alignment verification
5. **Blockchain Registration**: Web3 interfaces for $200 payment and on-chain anchoring
6. **Dashboard Exploration**: Comprehensive exploration of scores, amplifications, and ecosystem impact
7. **Alignment Options**: Clear pathways for optional Copper/Silver/Gold tier participation

### Financial Framework Integration ([Blueprint §4](docs/Blueprint for Syntheverse))
- **Free Submissions**: All evaluation submissions processed at no cost through user-friendly interfaces
- **Registration Fees**: Clear $200 payment flows for approved PoC blockchain anchoring
- **Tier System**: Intuitive displays and pathways for alignment contribution packages

### AI Integration Visualization ([Blueprint §5](docs/Blueprint for Syntheverse))
- **Archive Access**: Interfaces provide access to stored contributions training the Syntheverse AI
- **Fractal Display**: Visual representations of hydrogen holographic evaluation results
- **Ecosystem Evolution**: Dashboards show how contributions expand and enhance the AI system

### Governance & Transparency ([Blueprint §6](docs/Blueprint for Syntheverse))
- **Human Oversight Display**: Clear indication of human approval requirements and status
- **Allocation Transparency**: Visible SYNTH token distributions and metallic amplification calculations
- **Operator Communication**: Interface pathways for ecosystem governance and communication

### Implementation Status
- **✅ Fully Operational**: Complete Next.js dashboard with submission, exploration, and registration interfaces
- **🟡 Enhanced**: Real-time updates, Web3 integration, and multi-interface support
- **📋 Blueprint Complete**: Full UI layer implementation supporting end-to-end user experience

## Cross-References

- **Blueprint Document**: [docs/Blueprint for Syntheverse](../../docs/Blueprint for Syntheverse) - Central system vision
- **Quick Start Guide**: [docs/QUICK_START_POC_UI.md](../../docs/QUICK_START_POC_UI.md) - User onboarding
- **System Overview**: [docs/POC_SYSTEM_SUMMARY.md](../../docs/POC_SYSTEM_SUMMARY.md) - Complete system description
- **Parent**: [src/AGENTS.md](../AGENTS.md) - Source code organization
- **Children**:
  - [poc-frontend/AGENTS.md](poc-frontend/AGENTS.md) - Main application
  - [web-legacy/AGENTS.md](web-legacy/AGENTS.md) - Legacy interface
  - [submission/AGENTS.md](submission/AGENTS.md) - Submission UI
  - [admin/AGENTS.md](admin/AGENTS.md) - Admin interface
- **Related**:
  - [api/poc-api/AGENTS.md](../api/poc-api/AGENTS.md) - API integration
  - [api/rag_api/AGENTS.md](../api/rag_api/AGENTS.md) - RAG web UI
  - [docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md](../../docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md) - Complete workflow




