# Syntheverse PoC Frontend

Clean, simple, calm, research-grade frontend for the Proof of Contribution system.

## Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Accessible component library
- **TanStack Table** - Powerful table/data grid
- **Recharts** - Chart visualization

## Views

### 1. Contributor Dashboard (`/dashboard`)

Overview of contributions, tokenomics, and system status:
- Key metrics (total contributions, contributors, distributed tokens)
- Contribution status charts
- Metal distribution visualization
- Epoch distribution breakdown

### 2. Submissions Explorer (`/explorer`)

Browse and search all contributions:
- TanStack Table with sorting, filtering, pagination
- Search across all fields
- Click to view detail
- Status and metal badges

### 3. Submission Detail (`/submission/[hash]`)

Detailed view of a single contribution:
- Full metadata and information
- Evaluation metrics (Coherence, Density, Redundancy, PoC Score)
- Multi-metal allocations
- Content preview
- Evaluation details

### 4. Contribution Registry (`/registry`)

Append-only chronological log:
- Chronological timeline view
- Registry index numbers
- Quick stats
- Click to view detail

### 5. Submit Contribution (`/submission`)

Submit new contributions:
- Form with title, contributor, category
- PDF file upload support
- Text content input
- Archive-first submission

## API Integration

The frontend expects a backend API at `http://localhost:5001` (configurable via `NEXT_PUBLIC_API_URL`).

### Required API Endpoints

```
GET  /api/archive/statistics
GET  /api/archive/contributions
GET  /api/archive/contributions/:hash
POST /api/submit
POST /api/evaluate/:hash
GET  /api/sandbox-map
GET  /api/tokenomics/epoch-info
GET  /api/tokenomics/statistics
```

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:5001
```

3. Run development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
npm start
```

## Design Principles

- **Clean**: Minimal, uncluttered interface
- **Simple**: Clear navigation and workflows
- **Calm**: Muted colors, good spacing
- **Research-grade**: Professional, data-focused
- **Fast**: Optimized performance

## Architecture

```
ui-poc/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── dashboard/          # Contributor Dashboard
│   │   ├── explorer/           # Submissions Explorer
│   │   ├── submission/         # Submit & Detail views
│   │   └── registry/           # Contribution Registry
│   ├── components/             # React components
│   │   ├── ui/                 # shadcn/ui components
│   │   └── navigation.tsx      # Navigation bar
│   └── lib/                    # Utilities
│       ├── api.ts              # API client
│       └── utils.ts            # Helper functions
```

## Next Steps

1. **Backend Integration**: Create API server (Flask/FastAPI) that connects to PoC server
2. **Sandbox Map**: Add visualization component for sandbox map
3. **PDF Handling**: Implement PDF text extraction in backend
4. **Real-time Updates**: Add WebSocket support for live evaluation updates
