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








