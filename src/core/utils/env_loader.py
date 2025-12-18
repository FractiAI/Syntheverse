"""
Environment Variable Loading Utilities
Centralized utilities for loading environment variables, especially API keys.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def find_project_root() -> Path:
    """
    Find the project root directory by looking for .env file or .git directory.

    Returns:
        Path to project root directory
    """
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / ".env").exists() or (current / ".git").exists():
            return current
        current = current.parent

    # Fallback to current working directory if we can't find project root
    logger.warning("Could not find project root, using current working directory")
    return Path.cwd()


def load_groq_api_key() -> Optional[str]:
    """
    Load GROQ_API_KEY from .env file or environment variables.

    Checks multiple locations in order of priority:
        1. Project root .env file
        2. Current working directory .env
        3. Environment variable GROQ_API_KEY
        4. Home directory .env (fallback)

    Returns:
        API key string if found, None otherwise

    Note:
        This function loads the .env file if found, but doesn't fail if not found.
        Callers should handle the case where the key is None.
    """
    # Check if already set in environment
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        # Validate format (should start with 'gsk_' or 'sk-')
        if api_key.startswith(('gsk_', 'sk-')):
            logger.debug("GROQ_API_KEY found in environment variables")
            return api_key
        else:
            logger.warning("GROQ_API_KEY found but doesn't appear to be a valid format (should start with 'gsk_' or 'sk-')")

    # Try to load from .env files
    possible_paths = [
        find_project_root() / ".env",  # Project root
        Path.cwd() / ".env",           # Current working directory
        Path.home() / ".env",          # Home directory (fallback)
    ]

    for env_path in possible_paths:
        if env_path.exists():
            try:
                # Load .env file if python-dotenv is available
                try:
                    from dotenv import load_dotenv
                    if load_dotenv(env_path):
                        # Check if it set GROQ_API_KEY
                        api_key = os.getenv('GROQ_API_KEY')
                        if api_key:
                            if api_key.startswith(('gsk_', 'sk-')):
                                logger.info(f"Loaded GROQ_API_KEY from {env_path}")
                                return api_key
                            else:
                                logger.warning(f"GROQ_API_KEY loaded from {env_path} but invalid format")
                except ImportError:
                    # Fallback: manual .env parsing if python-dotenv not available
                    logger.debug("python-dotenv not available, using manual parsing")
                    try:
                        with open(env_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    if '=' in line:
                                        key, value = line.split('=', 1)
                                        if key.strip() == 'GROQ_API_KEY':
                                            api_key = value.strip().strip('"\'')
                                            if api_key.startswith(('gsk_', 'sk-')):
                                                logger.info(f"Loaded GROQ_API_KEY from {env_path} (manual parsing)")
                                                return api_key
                                            else:
                                                logger.warning(f"GROQ_API_KEY loaded from {env_path} but invalid format")
                    except Exception as e:
                        logger.debug(f"Could not parse {env_path}: {e}")

            except Exception as e:
                logger.debug(f"Error loading {env_path}: {e}")

    logger.debug("GROQ_API_KEY not found in any location")
    return None


def validate_groq_api_key(api_key: str) -> bool:
    """
    Validate that a GROQ API key appears to be in the correct format.

    Args:
        api_key: The API key to validate

    Returns:
        True if the key appears valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False

    # Should start with 'gsk_' (Groq) or 'sk-' (OpenAI format)
    return api_key.startswith(('gsk_', 'sk-')) and len(api_key.strip()) > 20

