# TypeScript/Next.js Coding Standards

## TypeScript Standards

### Type Safety
- Use strict TypeScript configuration
- Avoid `any` type - use `unknown` or specific types
- Define interfaces for object shapes
- Use type guards for runtime type checking
- Leverage TypeScript's type inference where appropriate

### Code Style
- Use ESLint and Prettier for formatting
- Follow Next.js conventions
- Use functional components with hooks
- Prefer arrow functions for callbacks

### File Organization
- One component per file
- Co-locate related files (components, hooks, utils)
- Use index files for clean imports
- Organize by feature, not by type

### Component Structure
```typescript
// Imports
import React from 'react'
import { useState } from 'react'

// Types/Interfaces
interface ComponentProps {
  title: string
  onAction: () => void
}

// Component
export function Component({ title, onAction }: ComponentProps) {
  const [state, setState] = useState<string>('')
  
  return (
    <div>
      <h1>{title}</h1>
    </div>
  )
}
```

## Next.js Specific

### App Router (Next.js 14+)
- Use App Router structure (`app/` directory)
- Use Server Components by default
- Mark Client Components with `'use client'`
- Use Route Handlers for API endpoints

### Data Fetching
- Use Server Components for data fetching when possible
- Use `fetch` with proper caching strategies
- Handle loading and error states
- Use React Suspense for async components

### Styling
- Use Tailwind CSS for styling
- Follow shadcn/ui component patterns
- Use CSS modules for component-specific styles
- Maintain consistent design system

### State Management
- Use React hooks for local state
- Use Context API for shared state
- Consider Zustand or Jotai for complex state
- Avoid prop drilling

### API Integration
- Create API client utilities in `lib/` directory
- Use TypeScript types for API responses
- Handle errors gracefully
- Implement retry logic for network requests

## Syntheverse Frontend Patterns

### Component Organization
- `components/` - Reusable UI components
- `app/` - Next.js app router pages
- `lib/` - Utility functions and API clients
- `types/` - TypeScript type definitions

### API Client Pattern
```typescript
// lib/api.ts
export async function fetchContributions() {
  const response = await fetch('/api/archive/contributions')
  if (!response.ok) throw new Error('Failed to fetch')
  return response.json()
}
```

### Error Handling
- Use error boundaries for component errors
- Display user-friendly error messages
- Log errors for debugging
- Provide fallback UI for errors



