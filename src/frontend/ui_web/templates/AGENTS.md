# Legacy Web Interface Templates

## Purpose

HTML templates for the legacy web interface components of the Syntheverse system.

## Key Files

### Certificate Registration Template (`register_certificate.html`)

Template for blockchain certificate registration interface:

- Certificate registration form
- Blockchain integration display
- Transaction status feedback
- User guidance for registration process

## Integration Points

- **Parent Directory**: [../AGENTS.md](../AGENTS.md) - Legacy web interface module
- **Frontend Layer**: [../../../AGENTS.md](../../AGENTS.md) - Frontend components
- **Blockchain Layer**: [../../../blockchain/AGENTS.md](../../../blockchain/AGENTS.md) - Certificate registration

## Development Guidelines

- Maintain compatibility with legacy Flask routing
- Ensure template variables are properly documented
- Follow consistent HTML structure and styling
- Include error handling for template rendering

## File Structure

```
templates/
├── register_certificate.html    # Certificate registration template
└── AGENTS.md                   # This documentation
```
