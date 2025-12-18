# Environment Configuration Agents

## Purpose

Environment setup and configuration documentation for external services, API keys, and system dependencies.

## Key Modules

### API Configuration Guides

- **Groq API Setup**: `SETUP_GROQ.md` and `GET_GROQ_KEY.md` for AI service configuration
- **External Service Integration**: Guides for third-party API configuration

### Environment Variables

- **Required Variables**: Essential configuration for system operation
- **Optional Variables**: Additional configuration for extended features
- **Security Considerations**: Safe handling of API keys and secrets

### Setup Instructions

- **Groq API Key Acquisition**: Step-by-step guide for obtaining API access
- **Environment Variable Configuration**: Methods for setting configuration values
- **Troubleshooting**: Common configuration issues and solutions

## Integration Points

- Environment configuration used by all services in `src/`
- API keys required by RAG API and PoC evaluation systems
- Configuration referenced by startup scripts in `scripts/startup/`
- Documentation connects to deployment guides in `docs/deployment/`

## Development Guidelines

- Document all required environment variables
- Provide secure methods for API key management
- Include troubleshooting guides for common issues
- Update documentation when new dependencies are added
- Test configuration in multiple environments

## Common Patterns

- API key acquisition and setup
- Environment variable configuration
- Service integration documentation
- Troubleshooting and error resolution
- Security best practices for secrets

## Blueprint Alignment

### AI Integration Setup (Blueprint §5)
- **Blueprint §5**: "PoC archive trains and evolves Syntheverse AI" → `SETUP_GROQ.md` complete setup guide
- **Blueprint §5**: "Hydrogen holographic fractal lens" → Groq API integration for HHFE evaluation
- **GROQ_API_KEY**: Required for all LLM-powered services (RAG API, PoC evaluation, Layer 2)
- **Security Protocol**: Never commit `.env` files to repository (Blueprint-compliant)

### Configuration Architecture
- **Blueprint §5**: AI integration requires proper environment setup → Complete configuration ecosystem
- **Centralized Loading**: `src.core.utils.load_groq_api_key()` utility for secure key management
- **Multi-Service Support**: Configuration supports RAG API, PoC evaluation, and Layer 2 systems

### Documentation Standards
- **Blueprint Vision §0**: "Documentation shows rather than tells" → Step-by-step guides with examples
- **Blueprint Vision §0**: "Documentation stays current with code changes" → Active maintenance of setup guides
- **Complete Coverage**: `SETUP_GROQ.md`, `GET_GROQ_KEY.md`, `README.md` comprehensive documentation

### Status & Integration
- **✅ Fully Operational**: Groq API integration working in production systems
- **🔗 System Integration**: Required by `src/core/layer2/poc_server.py` and `src/api/rag_api/`
- **📋 Startup Integration**: Referenced by `scripts/startup/start_servers.py` system initialization
- **🧪 Testing**: Configuration validated in all test environments

## File Structure

```
environment/
├── SETUP_GROQ.md            # Groq API setup guide
├── GET_GROQ_KEY.md          # API key acquisition
├── README.md                 # Configuration overview
└── AGENTS.md                 # This documentation
```

## Required Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `GROQ_API_KEY` | Groq API authentication | Yes |
| `FLASK_ENV` | Flask environment mode | No |
| `PYTHONPATH` | Python module paths | No |

## Cross-References

- **Parent**: [config/AGENTS.md](../AGENTS.md) - Configuration overview
- **Related**:
  - [scripts/startup/AGENTS.md](../../scripts/startup/AGENTS.md) - Startup scripts integration
  - [src/core/layer2/AGENTS.md](../../../src/core/layer2/AGENTS.md) - PoC evaluation usage
  - [src/api/rag_api/AGENTS.md](../../../src/api/rag_api/AGENTS.md) - RAG API usage
