import ollama
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def create_llm(model_id: str):
    """
    Creates an Ollama chat instance for the specified model.
    
    Args:
        model_id (str): The name of the Ollama model to use
        
    Returns:
        A callable that implements the chat interface
    """
    def chat_with_ollama(messages: list[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Implements chat functionality using Ollama.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            kwargs: Additional arguments for Ollama chat
            
        Returns:
            Dict containing the response message
        """
        try:
            # Convert LangChain messages to Ollama format
            ollama_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    # For raw dictionaries, ensure role is set
                    if 'content' in msg:
                        ollama_messages.append({
                            'role': msg.get('role', 'user'),  # Default to user if role not specified
                            'content': msg['content']
                        })
                else:
                    # For LangChain messages, convert type to role
                    content = msg.content if hasattr(msg, 'content') else str(msg)
                    role = 'assistant' if hasattr(msg, 'type') and msg.type == 'ai' else \
                          'system' if hasattr(msg, 'type') and msg.type == 'system' else 'user'
                    ollama_messages.append({
                        'role': role,
                        'content': content
                    })

            response = ollama.chat(
                model=model_id,
                messages=ollama_messages,
                stream=False
            )
            return {
                "content": response["message"]["content"],
                "role": "assistant"
            }
        except Exception as e:
            raise RuntimeError(f"Error communicating with Ollama: {str(e)}")
    
    return chat_with_ollama

def list_available_models() -> list[str]:
    """
    Lists all available Ollama models.
    
    Returns:
        List of model names
    """
    try:
        models = ollama.list()
        return [model.get("name", model.get("model", "unknown")) for model in models["models"]]
    except Exception as e:
        logger.error(f"Failed to list Ollama models: {str(e)}", exc_info=True)
        raise RuntimeError(f"Error listing Ollama models: {str(e)}")
