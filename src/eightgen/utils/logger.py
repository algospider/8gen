"""Structured logging configuration for 8Gen."""

import logging
from rich.logging import RichHandler


def get_logger(name: str = "eightgen", level: str = "INFO") -> logging.Logger:
    """Get a configured logger with Rich handler."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RichHandler(
            rich_tracebacks=True,
            show_time=False,
            show_path=False,
            markup=True
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
