# Admin Interface Source Code

React/TypeScript source code for the Syntheverse administrative dashboard and system management interface.

## Overview

This directory contains the implementation code for the admin interface, providing system administrators with tools to monitor, manage, and configure the Syntheverse platform.

## Component Structure

### Dashboard Components
- **AdminDashboard.tsx**: Main admin dashboard with system metrics
- **UserManagement.tsx**: User account and permission management
- **ContributionModeration.tsx**: PoC contribution review and approval interface
- **SystemMetrics.tsx**: Real-time system performance and usage statistics

### Configuration Components
- **SystemConfig.tsx**: System-wide configuration management
- **EpochManagement.tsx**: Tokenomics epoch control and threshold settings
- **ContractManagement.tsx**: Blockchain contract interaction and monitoring
- **APIManagement.tsx**: API endpoint configuration and rate limiting

### Monitoring Components
- **LogViewer.tsx**: System log aggregation and filtering
- **PerformanceMonitor.tsx**: Application performance metrics and alerts
- **SecurityDashboard.tsx**: Security events and threat monitoring
- **BackupStatus.tsx**: Data backup and recovery status

## State Management

### Redux Store Structure
```typescript
interface AdminState {
  users: User[];
  contributions: Contribution[];
  system: {
    metrics: SystemMetrics;
    config: SystemConfig;
    logs: LogEntry[];
  };
  blockchain: {
    contracts: Contract[];
    transactions: Transaction[];
  };
}
```

### Custom Hooks
```typescript
// System monitoring hook
const useSystemMetrics = () => {
  const [metrics, setMetrics] = useState<SystemMetrics>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      const data = await adminAPI.getSystemMetrics();
      setMetrics(data);
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Update every 30s

    return () => clearInterval(interval);
  }, []);

  return metrics;
};

// User management hook
const useUserManagement = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const userData = await adminAPI.getUsers();
      setUsers(userData);
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (userId: string, role: UserRole) => {
    await adminAPI.updateUserRole(userId, role);
    await loadUsers(); // Refresh user list
  };

  return { users, loading, loadUsers, updateUserRole };
};
```

## API Integration

### Admin API Client
```typescript
class AdminAPI {
  private baseURL = '/api/admin';

  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await fetch(`${this.baseURL}/metrics`);
    return response.json();
  }

  async getUsers(): Promise<User[]> {
    const response = await fetch(`${this.baseURL}/users`);
    return response.json();
  }

  async approveContribution(contributionId: string): Promise<void> {
    await fetch(`${this.baseURL}/contributions/${contributionId}/approve`, {
      method: 'POST'
    });
  }

  async updateSystemConfig(config: SystemConfig): Promise<void> {
    await fetch(`${this.baseURL}/config`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
  }
}

export const adminAPI = new AdminAPI();
```

## Security Features

### Authentication & Authorization
- **Role-Based Access**: Admin, Moderator, Viewer permission levels
- **Session Management**: Secure session handling with automatic logout
- **API Authentication**: JWT token validation for admin endpoints

### Audit Logging
- **Action Tracking**: All admin actions logged with user context
- **Change History**: Configuration and permission change tracking
- **Security Events**: Failed login attempts and suspicious activity logging

## Development

### Local Development Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

### Code Organization
```
src/
├── components/          # React components
│   ├── dashboard/      # Dashboard components
│   ├── users/          # User management
│   ├── system/         # System configuration
│   └── shared/         # Shared components
├── hooks/              # Custom React hooks
├── services/           # API service layer
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── styles/             # CSS/SCSS styles
```

## Testing

### Component Testing
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { AdminDashboard } from './AdminDashboard';

test('displays system metrics', async () => {
  render(<AdminDashboard />);

  expect(screen.getByText('System Metrics')).toBeInTheDocument();
  expect(await screen.findByText('Active Users: 1,234')).toBeInTheDocument();
});
```

### Integration Testing
```typescript
test('user role update workflow', async () => {
  // Test complete user role update flow
  render(<UserManagement />);

  const userRow = screen.getByText('john@example.com');
  fireEvent.click(userRow);

  const roleSelect = screen.getByLabelText('Role');
  fireEvent.change(roleSelect, { target: { value: 'admin' } });

  const saveButton = screen.getByText('Save Changes');
  fireEvent.click(saveButton);

  await waitFor(() => {
    expect(screen.getByText('Role updated successfully')).toBeInTheDocument();
  });
});
```

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed component documentation
- [FRACTAL.md](FRACTAL.md) - Fractal analysis and patterns
- [Admin Interface](../../AGENTS.md) - Interface overview documentation
