import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
def setup_logging():
    """
    Set up logging configuration for the application.
    
    Returns:
        tuple: (logger, log_paths) where log_paths is a dict containing paths to log files
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Define log file paths
    app_log_path = os.path.join(logs_dir, f'app_{timestamp}.log')
    error_log_path = os.path.join(logs_dir, f'error_{timestamp}.log')
    log_paths = {
        'app_log': app_log_path,
        'error_log': error_log_path
    }
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Create handlers
    file_handler = logging.FileHandler(app_log_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    error_file_handler = logging.FileHandler(error_log_path)
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_file_handler)
    root_logger.addHandler(console_handler)
    
    # Log initial message
    root_logger.info("Logging system initialized")
    return root_logger, log_paths
