import pytest
import logging
from unittest.mock import patch, MagicMock
from llm import create_llm, list_available_models

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_messages():
    """Sample messages for testing."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
        {"role": "user", "content": "How are you?"}
    ]

def test_create_llm_success(mock_ollama_response):
    """Test successful creation and use of LLM instance."""
    logger.info("Testing create_llm with successful response")
    
    with patch('ollama.chat', return_value=mock_ollama_response):
        llm = create_llm("test-model")
        messages = [{"role": "user", "content": "test message"}]
        
        try:
            response = llm(messages)
            assert response["content"] == "This is a test response"
            assert response["role"] == "assistant"
            logger.debug(f"LLM response: {response}")
        except Exception as e:
            logger.error(f"Error in create_llm test: {str(e)}")
            raise

def test_create_llm_error():
    """Test error handling in LLM creation and use."""
    logger.info("Testing create_llm error handling")
    
    with patch('ollama.chat', side_effect=Exception("Test error")):
        llm = create_llm("test-model")
        messages = [{"role": "user", "content": "test message"}]
        
        with pytest.raises(RuntimeError) as exc_info:
            llm(messages)
        
        logger.debug(f"Expected error raised: {exc_info.value}")
        assert "Error communicating with Ollama" in str(exc_info.value)

def test_list_available_models_success(mock_ollama_models):
    """Test successful retrieval of available models."""
    logger.info("Testing list_available_models with successful response")
    
    with patch('ollama.list', return_value=mock_ollama_models):
        try:
            models = list_available_models()
            assert len(models) == 3
            assert "model1" in models
            assert "model2" in models
            assert "model3" in models
            logger.debug(f"Retrieved models: {models}")
        except Exception as e:
            logger.error(f"Error in list_available_models test: {str(e)}")
            raise

def test_list_available_models_error():
    """Test error handling in model listing."""
    logger.info("Testing list_available_models error handling")
    
    with patch('ollama.list', side_effect=Exception("Test error")):
        with pytest.raises(RuntimeError) as exc_info:
            list_available_models()
        
        logger.debug(f"Expected error raised: {exc_info.value}")
        assert "Error listing Ollama models" in str(exc_info.value)

@pytest.mark.asyncio
async def test_llm_async_compatibility():
    """Test LLM compatibility with async operations."""
    logger.info("Testing LLM async compatibility")
    
    with patch('ollama.chat', return_value={"message": {"content": "async test", "role": "assistant"}}):
        llm = create_llm("test-model")
        messages = [{"role": "user", "content": "async test"}]
        
        try:
            # Ensure the LLM can be used in an async context
            response = llm(messages)
            assert response["content"] == "async test"
            assert response["role"] == "assistant"
            logger.debug(f"Async LLM response: {response}")
        except Exception as e:
            logger.error(f"Error in async compatibility test: {str(e)}")
            raise

def test_llm_with_streaming():
    """Test LLM with streaming option."""
    logger.info("Testing LLM with streaming option")
    
    mock_stream_response = [
        {"message": {"content": "part1", "role": "assistant"}},
        {"message": {"content": "part2", "role": "assistant"}},
    ]
    
    with patch('ollama.chat', return_value={"message": {"content": "part1part2", "role": "assistant"}}):
        llm = create_llm("test-model")
        messages = [{"role": "user", "content": "stream test"}]
        
        try:
            response = llm(messages)
            assert response["content"] == "part1part2"
            assert response["role"] == "assistant"
            logger.debug(f"Streaming LLM response: {response}")
        except Exception as e:
            logger.error(f"Error in streaming test: {str(e)}")
            raise
