"""
Logging utilities
"""
import logging
import os
from datetime import datetime
from utils.config import LOGS_DIR, LOG_FORMAT, LOG_DATE_FORMAT


def setup_logger(name: str, log_file: str = None, level=logging.INFO) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Optional log file name (will be saved in logs directory)
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        log_path = os.path.join(LOGS_DIR, log_file)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_training_log_file() -> str:
    """Get a timestamped log file name for training."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"training_{timestamp}.log"


def get_app_log_file() -> str:
    """Get log file name for application."""
    return "app.log"


# Create default loggers
app_logger = setup_logger("app", get_app_log_file())
training_logger = setup_logger("training")
