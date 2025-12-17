# Frontend Applications

## Purpose

Frontend applications for the Syntheverse system, providing user interfaces for contribution submission, exploration, and system interaction.

## Components

### PoC Frontend (`poc-frontend/`)

Next.js 14 application with App Router.

**Features:**
- Dashboard with system statistics
- Contribution submission interface
- Explorer for browsing contributions
- Registry with chronological timeline
- Sandbox map with interactive visualization

**Technology:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui

**Status:** ✅ Operational

### Legacy Web (`web-legacy/`)

Flask web interface (legacy system).

**Features:**
- Full-featured PoD/PoT/PoA submission system
- Real-time status display
- Certificate registration
- Artifact viewing

**Status:** ✅ Operational (Legacy)

### Submission UI (`submission/`)

Basic HTML interface for submitting contributions.

**Status:** 🚧 In Development

### Admin UI (`admin/`)

Administrative interface for system management.

**Status:** 🚧 In Development

## Integration

- PoC Frontend connects to PoC API (Flask)
- Legacy Web is self-contained Flask application
- APIs provide REST endpoints for data
- Web3 integration for blockchain registration

## Usage

### PoC Frontend

```bash
cd src/frontend/poc-frontend
npm install
npm run dev
```

Access at: http://localhost:3001

### Legacy Web

```bash
cd src/frontend/web-legacy
pip install -r requirements.txt
python app.py
```

Access at: http://localhost:5000

## Documentation

- [PoC Frontend README](poc-frontend/README.md)
- [Legacy Web README](web-legacy/README.md)



