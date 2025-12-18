# Python Coding Standards

## Style Guide
- Follow PEP 8 style guide
- Use Black formatter for consistent formatting
- Maximum line length: 100 characters (prefer 88)
- Use 4 spaces for indentation (no tabs)

## Code Structure

### Imports
- Group imports: standard library, third-party, local
- Use absolute imports when possible
- Avoid wildcard imports (`from module import *`)
- Sort imports alphabetically within groups

### Type Hints
- Use type hints for function parameters and return values
- Use `Optional[T]` for nullable types
- Use `Dict`, `List`, `Tuple` from `typing` module
- Add type hints to public APIs

### Docstrings
- Use Google-style docstrings
- Include Args, Returns, Raises sections
- Document complex logic and algorithms
- Keep docstrings concise and accurate

### Error Handling
- Use specific exception types
- Create custom exceptions when appropriate
- Use context managers for resource management
- Log errors with appropriate levels

### Classes and Functions
- Keep classes focused and cohesive
- Use properties for computed attributes
- Prefer composition over inheritance
- Keep functions small and focused

### File Organization
```python
"""
Module docstring describing purpose.
"""

# Standard library imports
import os
import json
from pathlib import Path
from typing import Dict, Optional

# Third-party imports
from flask import Flask

# Local imports
from .utils import helper_function

# Constants
DEFAULT_CONFIG = {}

# Classes and functions
class MyClass:
    """Class docstring."""
    pass

def main():
    """Main function."""
    pass

if __name__ == "__main__":
    main()
```

## Syntheverse-Specific Patterns

### Environment Variables
- Use `python-dotenv` to load `.env` files
- Check for required environment variables at startup
- Provide clear error messages for missing variables
- Document required environment variables in README

### Path Handling
- Use `pathlib.Path` for file operations
- Use relative paths from project root
- Create directories with `mkdir(parents=True, exist_ok=True)`
- Validate paths before use

### Logging
- Use Python's `logging` module
- Set appropriate log levels
- Include context in log messages
- Use structured logging when appropriate

### Configuration
- Store configuration in environment variables
- Use configuration classes for complex settings
- Validate configuration on startup
- Provide sensible defaults








