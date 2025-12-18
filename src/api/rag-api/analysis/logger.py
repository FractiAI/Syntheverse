"""
Logger utility for the RAG analysis module.

Provides structured logging with configurable output levels and formatting.
"""

import logging
import sys
from typing import Optional
from pathlib import Path


def setup_analysis_logging(log_level: str = "INFO",
                          log_file: Optional[str] = None,
                          console: bool = True) -> logging.Logger:
    """
    Set up logging configuration for analysis operations.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
        console: Whether to enable console logging

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('rag_analysis')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Add console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "rag_analysis") -> logging.Logger:
    """
    Get a logger instance with the standard analysis configuration.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(f"{name}")


class AnalysisLogger:
    """
    Enhanced logger with analysis-specific methods.
    """

    def __init__(self, base_logger: logging.Logger):
        self.logger = base_logger

    def log_progress(self, current: int, total: int, message: str = "Processing"):
        """Log progress with percentage."""
        percentage = (current / total) * 100 if total > 0 else 0
        self.logger.info(f"{message}: {current}/{total} ({percentage:.1f}%)")

    def log_analysis_start(self, analysis_type: str, item_count: int):
        """Log the start of an analysis operation."""
        self.logger.info(f"Starting {analysis_type} analysis on {item_count} items")

    def log_analysis_complete(self, analysis_type: str, duration: Optional[float] = None):
        """Log the completion of an analysis operation."""
        duration_str = f" in {duration:.2f}s" if duration else ""
        self.logger.info(f"Completed {analysis_type} analysis{duration_str}")

    def log_warning_with_suggestion(self, warning: str, suggestion: str):
        """Log a warning with a suggested fix."""
        self.logger.warning(f"{warning}. Suggestion: {suggestion}")

    def log_error_with_context(self, error: str, context: dict):
        """Log an error with additional context information."""
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        self.logger.error(f"{error}. Context: {context_str}")