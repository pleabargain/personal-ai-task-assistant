import pytest
import logging
import os
import sys
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Configure test logging
@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Set up logging for tests."""
    # Create test logs directory
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'tests')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(logs_dir, f'test_{timestamp}.log')
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Test logging initialized")
    return logger

@pytest.fixture
def mock_ollama_response():
    """Mock response from Ollama API."""
    return {
        "model": "test-model",
        "message": {
            "role": "assistant",
            "content": "This is a test response"
        }
    }

@pytest.fixture
def mock_ollama_models():
    """Mock list of available Ollama models."""
    return {
        "models": [
            {"name": "model1", "size": "1.1GB"},
            {"name": "model2", "size": "2.2GB"},
            {"name": "model3", "size": "3.3GB"}
        ]
    }
