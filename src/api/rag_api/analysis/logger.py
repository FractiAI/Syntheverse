"""
Structured logging for embedding analysis operations.

Provides consistent logging across all analysis modules with appropriate
log levels, formatting, and output options.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def get_logger(name: str, log_file: Optional[str] = None,
               level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger for analysis operations.

    Args:
        name: Logger name (usually __name__)
        log_file: Optional log file path
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Don't configure if already configured
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def setup_analysis_logging(log_file: Optional[str] = None,
                          level: str = 'INFO') -> None:
    """
    Set up logging for the entire analysis module.

    Args:
        log_file: Optional log file path
        level: Logging level string ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    log_level = level_map.get(level.upper(), logging.INFO)

    # Configure root logger for analysis module
    analysis_logger = logging.getLogger('src.api.rag_api.analysis')
    analysis_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in analysis_logger.handlers[:]:
        analysis_logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    analysis_logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        analysis_logger.addHandler(file_handler)

    # Prevent duplicate messages
    analysis_logger.propagate = False


class AnalysisLogger:
    """
    Wrapper class for analysis-specific logging with structured output.
    """

    def __init__(self, name: str, log_file: Optional[str] = None):
        """
        Initialize analysis logger.

        Args:
            name: Logger name
            log_file: Optional log file path
        """
        self.logger = get_logger(name, log_file)

    def log_operation_start(self, operation: str, **kwargs):
        """Log the start of an analysis operation."""
        extra_info = f" ({kwargs})" if kwargs else ""
        self.logger.info(f"Starting {operation}{extra_info}")

    def log_operation_end(self, operation: str, duration: Optional[float] = None, **kwargs):
        """Log the end of an analysis operation."""
        duration_info = f" in {duration:.2f}s" if duration else ""
        extra_info = f" ({kwargs})" if kwargs else ""
        self.logger.info(f"Completed {operation}{duration_info}{extra_info}")

    def log_progress(self, operation: str, current: int, total: int, **kwargs):
        """Log progress of an ongoing operation."""
        percentage = (current / total) * 100 if total > 0 else 0
        extra_info = f" ({kwargs})" if kwargs else ""
        self.logger.info(f"{operation}: {current}/{total} ({percentage:.1f}%){extra_info}")

    def log_statistics(self, stats: dict):
        """Log computed statistics."""
        self.logger.info("Statistics computed:")
        for key, value in stats.items():
            if isinstance(value, float):
                self.logger.info(f"  {key}: {value:.4f}")
            else:
                self.logger.info(f"  {key}: {value}")

    def log_error(self, operation: str, error: Exception):
        """Log operation errors."""
        self.logger.error(f"Error in {operation}: {error}")

    def log_warning(self, message: str):
        """Log warnings."""
        self.logger.warning(message)
