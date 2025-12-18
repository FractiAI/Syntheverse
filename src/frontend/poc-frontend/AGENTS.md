# PoC Frontend Agents

## Purpose

Modern Next.js 14 application with App Router providing the main PoC dashboard, submission interface, explorer, registry, and sandbox map visualization.

## Key Modules

### Pages (`src/app/`)

- **`dashboard/page.tsx`**: System statistics and overview
- **`submission/page.tsx`**: Contribution submission interface
- **`submission/[hash]/page.tsx`**: Individual contribution details
- **`explorer/page.tsx`**: Contribution browsing and filtering
- **`registry/page.tsx`**: Chronological contribution timeline
- **`sandbox-map/page.tsx`**: Interactive network visualization

### Components (`src/components/`)

- **`navigation.tsx`**: Main navigation component
- **`sandbox-map-network.tsx`**: Network graph visualization
- **`ui/`**: shadcn/ui components (button, card, etc.)

### Utilities (`src/lib/`)

- **`api.ts`**: API client for backend communication
- **`utils.ts`**: Utility functions

## Integration Points

- **PoC API**: Flask API server for backend communication
- **vis-network**: Graph visualization library
- **Web3**: Blockchain integration for certificate registration
- **Real-time Updates**: Polling for status updates

## Development Guidelines

### Next.js Patterns

- Use Server Components by default
- Mark Client Components with `'use client'`
- Use App Router file-based routing
- Implement proper error boundaries and loading states

### API Integration

- Create API client utilities in `lib/api.ts`
- Handle loading and error states
- Implement retry logic for network requests
- Cache responses appropriately

### State Management

- Use React hooks for local state
- Use Context API for shared state
- Minimize prop drilling
- Keep state close to usage

### Styling

- Use Tailwind CSS utility classes
- Follow shadcn/ui component patterns
- Maintain design system consistency
- Responsive design for mobile

## Common Patterns

- Component composition with shadcn/ui
- API client pattern for backend communication
- Real-time updates via polling
- Error boundaries for error handling
- Loading states for async operations
- TypeScript for type safety








