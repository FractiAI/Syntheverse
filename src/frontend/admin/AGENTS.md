# Admin Interface Agents

## Purpose

Administrative interface for managing Syntheverse PoD submissions, evaluations, token allocations, and system monitoring.

## Key Modules

### Admin UI (`src/`)

- **HTML Scaffold**: Basic HTML structure for admin interface
- **Submission Management**: View and manage all PoD submissions
- **Evaluation Monitoring**: Review evaluation queue and results
- **Token Allocation Management**: Approve/reject token allocations
- **System Statistics**: Real-time system and blockchain statistics
- **Contributor Management**: User and contributor administration
- **Epoch Management**: Configure epochs and tier availability
- **Tokenomics Monitoring**: Track token distribution and balances

## Integration Points

- Admin interface connects to Layer 2 API for evaluation management
- Links to Layer 1 blockchain for allocation and statistics
- Uses PoC API for submission and archive management
- Integrates with frontend authentication and authorization
- Connects to tokenomics state for allocation monitoring

## Development Guidelines

- Implement proper admin authentication and authorization
- Use consistent UI patterns with other frontend applications
- Provide comprehensive audit logging for admin actions
- Ensure secure API communication with backend services
- Test admin functionality thoroughly before production use

## Common Patterns

- Administrative dashboard layout
- User management interfaces
- Submission moderation workflows
- Real-time statistics displays
- Audit and logging systems

## File Structure

```
admin/
├── src/
│   └── index.html            # Admin interface scaffold
├── README.md                 # Admin documentation
└── AGENTS.md                 # This documentation
```

## Cross-References

- **Parent**: [frontend/AGENTS.md](../AGENTS.md) - Frontend overview
- **Related**:
  - [poc-frontend/AGENTS.md](../poc-frontend/AGENTS.md) - Main dashboard
  - [api/poc-api/AGENTS.md](../../api/poc-api/AGENTS.md) - API integration
  - [core/layer2/AGENTS.md](../../core/layer2/AGENTS.md) - Layer 2 integration






