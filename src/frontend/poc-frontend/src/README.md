# PoC Frontend Source Code

Next.js 14 React/TypeScript implementation of the Syntheverse Proof-of-Contribution dashboard and user interface.

## Overview

This directory contains the main user-facing application built with Next.js, providing a modern, responsive interface for contribution exploration, submission management, and ecosystem interaction.

## Application Structure

### Pages (App Router)
```
src/
├── app/                    # Next.js 13+ app directory
│   ├── dashboard/         # User dashboard page
│   ├── submission/        # Contribution submission
│   ├── archive/           # Contribution archive browser
│   ├── sandbox-map/       # Interactive knowledge network
│   ├── registry/          # Contribution timeline
│   ├── profile/           # User profile management
│   ├── admin/             # Administrative functions
│   ├── api/               # API routes
│   └── layout.tsx         # Root layout component
```

### Components Architecture
```
components/
├── ui/                    # Reusable UI components
│   ├── Button.tsx        # Button component
│   ├── Card.tsx          # Card container
│   ├── Modal.tsx         # Modal dialog
│   └── Table.tsx         # Data table
├── forms/                # Form components
│   ├── SubmissionForm.tsx
│   ├── LoginForm.tsx
│   └── ProfileForm.tsx
├── dashboard/            # Dashboard-specific components
│   ├── ContributionList.tsx
│   ├── ScoreDisplay.tsx
│   ├── MetallicAmplification.tsx
│   └── ActivityFeed.tsx
└── shared/               # Shared application components
    ├── Header.tsx
    ├── Footer.tsx
    └── Navigation.tsx
```

## State Management

### Global State (Zustand)
```typescript
interface AppState {
  user: User | null;
  contributions: Contribution[];
  sandboxData: SandboxNode[];
  ui: {
    theme: 'light' | 'dark';
    sidebarOpen: boolean;
    loading: boolean;
  };
  filters: {
    metal: MetalFilter;
    dateRange: DateRange;
    tags: string[];
  };
}

// Store definition
export const useAppStore = create<AppState>()((set, get) => ({
  user: null,
  contributions: [],
  sandboxData: [],
  ui: {
    theme: 'light',
    sidebarOpen: false,
    loading: false
  },
  filters: {
    metal: 'all',
    dateRange: { start: null, end: null },
    tags: []
  },

  // Actions
  setUser: (user) => set({ user }),
  setContributions: (contributions) => set({ contributions }),
  updateFilters: (filters) => set((state) => ({
    filters: { ...state.filters, ...filters }
  })),
  toggleTheme: () => set((state) => ({
    ui: { ...state.ui, theme: state.ui.theme === 'light' ? 'dark' : 'light' }
  }))
}));
```

### Server State (React Query)
```typescript
// API hooks
export const useContributions = (filters: ContributionFilters) => {
  return useQuery({
    queryKey: ['contributions', filters],
    queryFn: () => api.getContributions(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useSandboxData = () => {
  return useQuery({
    queryKey: ['sandbox'],
    queryFn: () => api.getSandboxData(),
    refetchInterval: 30 * 1000, // Refresh every 30 seconds
  });
};

// Mutations
export const useSubmitContribution = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SubmissionData) => api.submitContribution(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contributions'] });
      toast.success('Contribution submitted successfully!');
    },
  });
};
```

## API Integration

### API Client
```typescript
class SyntheverseAPI {
  private baseURL = process.env.NEXT_PUBLIC_API_URL;

  // Authentication
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    return response.json();
  }

  // Contributions
  async getContributions(filters?: ContributionFilters): Promise<Contribution[]> {
    const params = new URLSearchParams(filters as any);
    const response = await fetch(`${this.baseURL}/contributions?${params}`);
    return response.json();
  }

  async submitContribution(data: FormData): Promise<SubmissionResponse> {
    const response = await fetch(`${this.baseURL}/contributions`, {
      method: 'POST',
      body: data,
    });
    return response.json();
  }

  // Sandbox
  async getSandboxData(): Promise<SandboxData> {
    const response = await fetch(`${this.baseURL}/sandbox`);
    return response.json();
  }

  // User
  async getProfile(): Promise<UserProfile> {
    const response = await fetch(`${this.baseURL}/user/profile`);
    return response.json();
  }
}

export const api = new SyntheverseAPI();
```

## UI/UX Features

### Responsive Design
```typescript
// Responsive hook
export const useBreakpoint = () => {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('mobile');

  useEffect(() => {
    const updateBreakpoint = () => {
      const width = window.innerWidth;
      if (width >= 1280) setBreakpoint('desktop');
      else if (width >= 768) setBreakpoint('tablet');
      else setBreakpoint('mobile');
    };

    updateBreakpoint();
    window.addEventListener('resize', updateBreakpoint);
    return () => window.removeEventListener('resize', updateBreakpoint);
  }, []);

  return breakpoint;
};
```

### Theme System
```typescript
// Theme provider
const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { theme } = useAppStore();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return <>{children}</>;
};
```

### Loading States
```tsx
const ContributionList: React.FC = () => {
  const { data: contributions, isLoading, error } = useContributions();

  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorMessage
        title="Failed to load contributions"
        message="Please try again later"
        onRetry={() => window.location.reload()}
      />
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {contributions?.map((contribution) => (
        <ContributionCard key={contribution.id} contribution={contribution} />
      ))}
    </div>
  );
};
```

## Development

### Local Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

### Environment Configuration
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:5001
NEXT_PUBLIC_SANDBOX_UPDATE_INTERVAL=30000
NEXT_PUBLIC_MAX_FILE_SIZE=104857600
```

## Testing Strategy

### Unit Tests
```typescript
// Component testing
import { render, screen } from '@testing-library/react';
import { ContributionCard } from './ContributionCard';

const mockContribution = {
  id: '1',
  title: 'Test Contribution',
  score: 8500,
  metal: 'Gold' as const,
  author: 'Test Author'
};

test('displays contribution information', () => {
  render(<ContributionCard contribution={mockContribution} />);

  expect(screen.getByText('Test Contribution')).toBeInTheDocument();
  expect(screen.getByText('Gold')).toBeInTheDocument();
  expect(screen.getByText('8,500')).toBeInTheDocument();
});
```

### Integration Tests
```typescript
// E2E testing with Playwright
import { test, expect } from '@playwright/test';

test('complete contribution submission', async ({ page }) => {
  await page.goto('/submission');

  // Fill form
  await page.fill('[data-testid="title"]', 'Test Contribution');
  await page.fill('[data-testid="description"]', 'Test description');

  // Upload file
  await page.setInputFiles('[data-testid="file-upload"]', 'test-file.pdf');

  // Submit
  await page.click('[data-testid="submit-button"]');

  // Verify success
  await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
});
```

### Performance Testing
```typescript
// Performance monitoring
import { reportWebVitals } from 'web-vitals';

export function WebVitals() {
  reportWebVitals((metric) => {
    // Send to analytics
    console.log(metric);
  });
}
```

## Deployment

### Build Optimization
- **Static Generation**: Dashboard pages pre-rendered at build time
- **Image Optimization**: Next.js automatic image optimization
- **Code Splitting**: Automatic route-based code splitting
- **Bundle Analysis**: Webpack bundle analyzer integration

### CDN Integration
```typescript
// next.config.js
module.exports = {
  images: {
    loader: 'cloudinary',
    path: 'https://res.cloudinary.com/syntheverse/image/upload/',
  },
  assetPrefix: process.env.NODE_ENV === 'production' ? 'https://cdn.syntheverse.com' : '',
};
```

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed component documentation
- [FRACTAL.md](FRACTAL.md) - Fractal analysis and patterns
- [Next.js Documentation](https://nextjs.org/docs) - Framework reference
- [Component Library](../../components/README.md) - Shared component documentation
