# Core Utilities

## Purpose

Shared utility functions for the Syntheverse core system, providing centralized environment and configuration management.

## Key Modules

### Environment Loader (`env_loader.py`)

Centralized environment variable and API key management:

- **`load_groq_api_key()`**: Load GROQ_API_KEY from environment or .env file
- **`load_env_variable(name)`**: Generic environment variable loader with fallback
- **`validate_api_key(key)`**: Validate API key format and presence

## Integration Points

- Used by Layer 2 evaluation engine (`core/layer2/poc_server.py`)
- Used by RAG API (`api/rag_api/`)
- Used by PoC API for LLM operations
- References `.env` file in project root

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for LLM services |
| `FLASK_ENV` | No | Flask environment (development/production) |
| `NODE_ENV` | No | Node.js environment |

## Usage Examples

```python
from src.core.utils import load_groq_api_key

# Load GROQ API key
api_key = load_groq_api_key()
if not api_key:
    raise ValueError("GROQ_API_KEY not configured")

# Use in LLM client
client = Groq(api_key=api_key)
```

## Development Guidelines

- Always use centralized loaders for consistency
- Never hardcode API keys or secrets
- Log loading failures without exposing key values
- Support both environment variables and .env files

## File Structure

```
utils/
├── __init__.py           # Package exports
└── env_loader.py         # Environment configuration
```

## Cross-References

- **Parent**: [core/AGENTS.md](../AGENTS.md) - Core logic overview
- **Configuration**: [config/environment/AGENTS.md](../../../config/environment/AGENTS.md) - Setup guides
- **Related**:
  - [core/layer2/AGENTS.md](../layer2/AGENTS.md) - Layer 2 usage
  - [api/rag_api/AGENTS.md](../../api/rag_api/AGENTS.md) - RAG API usage

