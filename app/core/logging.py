import logging
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = """
Time: %(asctime)s
Logger: %(name)s
Level: %(levelname)s
File: %(filename)s:%(lineno)d
Message: %(message)s
----------------------------------------"""

def setup_logger(name: str, log_file: str = None, level=logging.INFO) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.
    
    Args:
        name: Name of the logger
        log_file: Optional file path for logging
        level: Logging level
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    simple_formatter = logging.Formatter(LOG_FORMAT)
    detailed_formatter = logging.Formatter(DETAILED_FORMAT)
    
    # Console handler (simple format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (detailed format)
    if log_file:
        file_handler = logging.FileHandler(logs_dir / log_file)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create specific loggers
autogen_logger = setup_logger(
    "autogen",
    f"autogen_{datetime.now().strftime('%Y%m%d')}.log"
)

api_logger = setup_logger(
    "api",
    f"api_{datetime.now().strftime('%Y%m%d')}.log"
) 