# Frontend Development Standards

## Next.js 14 App Router

### File Structure
- `app/` - App router pages and layouts
- `components/` - Reusable UI components
- `lib/` - Utility functions and API clients
- `public/` - Static assets

### Routing
- Use App Router file-based routing
- Create route groups with `(group)` syntax
- Use dynamic routes with `[param]`
- Implement loading and error boundaries

### Server vs Client Components
- Use Server Components by default
- Mark Client Components with `'use client'`
- Use Client Components for interactivity
- Minimize client-side JavaScript

### Data Fetching
```typescript
// Server Component
export default async function Page() {
  const data = await fetch('/api/data')
  return <div>{data}</div>
}

// Client Component
'use client'
export function InteractiveComponent() {
  const [state, setState] = useState()
  return <button onClick={() => setState('clicked')}>Click</button>
}
```

## Component Patterns

### shadcn/ui Integration
- Use shadcn/ui components as base
- Customize components as needed
- Maintain design system consistency
- Follow component composition patterns

### State Management
- Use React hooks for local state
- Use Context for shared state
- Implement proper state updates
- Avoid unnecessary re-renders

### Styling
- Use Tailwind CSS utility classes
- Follow design system tokens
- Use CSS modules for component styles
- Maintain responsive design

## Syntheverse Frontend Components

### PoC Dashboard
- Display system statistics
- Show contribution metrics
- Real-time updates via polling
- Interactive charts and visualizations

### Submission Interface
- File upload handling
- Progress tracking
- Status updates
- Error display

### Sandbox Map
- Network visualization
- Interactive filtering
- Contribution relationships
- Real-time updates

### Registry View
- Chronological timeline
- Contribution details
- Multi-metal display
- Blockchain registration

## API Integration

### API Client Pattern
```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'

export async function fetchContributions() {
  const res = await fetch(`${API_BASE}/api/archive/contributions`)
  if (!res.ok) throw new Error('Failed to fetch')
  return res.json()
}
```

### Error Handling
- Handle network errors gracefully
- Display user-friendly error messages
- Implement retry logic
- Show loading states

### Real-time Updates
- Use polling for status updates
- Implement WebSocket if needed
- Cache API responses appropriately
- Invalidate cache on updates

## Performance Optimization

### Code Splitting
- Use dynamic imports for large components
- Lazy load routes when possible
- Optimize bundle size
- Use Next.js Image component

### Caching
- Use Next.js caching strategies
- Implement client-side caching
- Cache API responses appropriately
- Invalidate cache on mutations



