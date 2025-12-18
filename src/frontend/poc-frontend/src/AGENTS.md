# PoC Frontend Source Agents

## Purpose

Source code for the Next.js 14 PoC frontend application, organized using App Router architecture.

## Key Modules

### App Directory (`app/`)

Next.js 14 App Router pages:
- **`page.tsx`**: Landing page
- **`layout.tsx`**: Root layout with navigation
- **`globals.css`**: Global styles
- **`dashboard/page.tsx`**: System statistics dashboard
- **`submission/page.tsx`**: Contribution submission form
- **`explorer/page.tsx`**: Contribution browser with filtering
- **`registry/page.tsx`**: Chronological contribution timeline
- **`sandbox-map/page.tsx`**: Interactive network visualization
- **`recognition/page.tsx`**: Recognition system display
- **`tiers/page.tsx`**: Contributor tier information

### Components Directory (`components/`)

Reusable React components:
- **`navigation.tsx`**: Main navigation component
- **`sandbox-map-network.tsx`**: Network graph visualization
- **`ui/`**: shadcn/ui component library
  - `badge.tsx`, `button.tsx`, `card.tsx`, `input.tsx`, `label.tsx`

### Library Directory (`lib/`)

Utilities and API clients:
- **`api.ts`**: API client for backend communication
- **`utils.ts`**: Utility functions and helpers

## Integration Points

- **PoC API**: REST endpoints at localhost:5001
- **Backend Services**: Layer 2 evaluation engine and blockchain
- **Web3**: Blockchain registration integration
- **Real-time Updates**: Polling-based status updates

## Responsibilities

### Page Implementation
- Implement all user-facing pages with App Router
- Manage page-level state and data fetching
- Handle loading and error states
- Implement responsive layouts

### Component Development
- Build reusable, composable components
- Maintain consistent UI/UX patterns
- Implement accessibility features
- Optimize component performance

### API Integration
- Coordinate backend communication through API client
- Handle request/response transformations
- Implement error handling and retry logic
- Cache responses appropriately

## Interfaces

### API Client Interface
```typescript
// lib/api.ts
export const api = {
  submit: (data: FormData) => Promise<Response>
  getArchive: () => Promise<Contribution[]>
  getTokenomics: () => Promise<TokenomicsState>
  getSandboxMap: () => Promise<SandboxMap>
  register: (hash: string) => Promise<Response>
}
```

### Component Interfaces
- **Navigation**: Site-wide navigation with active state
- **SandboxMapNetwork**: Interactive graph visualization
- **UI Components**: Consistent design system components

## Dependencies

### Core Dependencies
- **Next.js 14**: React framework with App Router
- **React 18**: UI library
- **TypeScript**: Type safety

### UI Dependencies
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Component library
- **Lucide React**: Icon library

### Visualization
- **vis-network**: Network graph visualization
- **Chart libraries**: Data visualization (as needed)

## Development

### Setup
```bash
cd src/frontend/poc-frontend
npm install
npm run dev  # http://localhost:3001
```

### File Conventions
- **Pages**: `app/*/page.tsx` - Route pages
- **Layouts**: `app/*/layout.tsx` - Shared layouts
- **Components**: `components/*.tsx` - Reusable components
- **Client Components**: Mark with `'use client'` directive
- **Server Components**: Default, no directive needed

### Styling
- **Tailwind**: Use utility classes
- **CSS Modules**: For component-specific styles
- **Global Styles**: `globals.css` for site-wide styles

## Testing

### Test Strategy
- **Component Tests**: React Testing Library
- **Integration Tests**: Playwright for E2E
- **API Mocking**: MSW for API tests

### Test Execution
```bash
npm test           # Unit tests
npm run test:e2e   # E2E tests
```

## Blueprint Alignment

### Dashboard Implementation ([Blueprint §1.5](docs/Blueprint for Syntheverse))
- **Exploration Interface**: Pages provide comprehensive access to PoC archive, scores, and metallic amplifications
- **Real-time Display**: Components show live evaluation status and ecosystem impact
- **Network Visualization**: Sandbox map displays contribution relationships and system structure

### User Experience ([Blueprint §1](docs/Blueprint for Syntheverse))
- **Intuitive Submission**: Forms guide users through contribution upload and metadata entry
- **Status Tracking**: Real-time updates show evaluation progress and approval status
- **Dashboard Access**: Comprehensive views of scores, amplifications, and ecosystem participation

### Complete Workflow Support ([Blueprint §7](docs/Blueprint for Syntheverse))
- **Entry Points**: Clear pathways from landing page to submission interfaces
- **Progress Visibility**: Live status displays for evaluation, approval, and registration stages
- **Outcome Display**: Result pages show scores, qualifications, and token allocations

## Cross-References

- **Parent**: [poc-frontend/AGENTS.md](../AGENTS.md) - Frontend application overview
- **Related**:
  - [lib/api.ts](lib/api.ts) - API client implementation
  - [components/](components/) - Component library
  - [app/](app/) - Page implementations
  - [docs/QUICK_START_POC_UI.md](../../../../docs/QUICK_START_POC_UI.md) - User guide

