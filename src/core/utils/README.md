# Core Utilities

Shared utility functions and common operations supporting the Syntheverse Layer 2 evaluation engine.

## Overview

This module provides essential utility functions used across the core business logic, including environment configuration loading, common data processing operations, and shared helper functions.

## Key Utilities

### Environment Management
- `load_groq_api_key()`: Secure GROQ API key loading from environment
- Configuration validation and error handling
- Environment variable management

### Data Processing
- Common data transformation functions
- Validation helpers
- Serialization utilities

### Shared Operations
- Logging utilities
- Error handling patterns
- Common algorithmic functions

## Usage

```python
from src.core.utils import load_groq_api_key

# Load API key securely
api_key = load_groq_api_key()

# Use in LLM operations
# ... evaluation logic ...
```

## Integration Points

- **Layer 2 Engine**: Provides utilities for evaluation operations
- **API Services**: Supplies configuration loading for external services
- **Blockchain Layer**: Offers common functions for contract interactions
- **All Core Modules**: Shared utilities across the business logic layer

## Dependencies

- Python standard library
- Environment variable access
- Configuration file parsing

## Testing

```bash
# Run utility tests
cd src/core/utils
python -m pytest tests/
```

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed component documentation
- [FRACTAL.md](FRACTAL.md) - Fractal analysis and patterns
- [Core Overview](../AGENTS.md) - Parent module documentation
