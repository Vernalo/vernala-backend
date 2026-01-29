import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{self.BOLD}{levelname}{self.RESET}"
            )

        formatted = super().format(record)

        return formatted


def setup_logger(
    name: str = "vernala",
    level: int = logging.INFO,
    use_colors: bool = True,
) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name (default: "vernala")
        level: Logging level (default: INFO)
        use_colors: Whether to use colored output (default: True)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if use_colors:
        formatter = ColoredFormatter(
            fmt="%(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

logger = setup_logger()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Optional logger name. If None, returns the default logger.

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"vernala.{name}")
    return logger
