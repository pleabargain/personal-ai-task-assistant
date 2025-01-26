import pytest
import logging
from unittest.mock import patch, MagicMock
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.schema import AgentFinish
from task_manager import (
    create_agent,
    extract_core_tasks,
    get_last_human_message,
    parse_llm_result,
    planner,
    task_executor,
    project_updater,
    replanner,
    run_paa,
)

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_state():
    """Create a mock state for testing."""
    return {
        "messages": [
            SystemMessage(content="You are a helpful AI assistant."),
            HumanMessage(content="Test task")
        ],
        "plan": ["Step 1", "Step 2", "Step 3"],
        "goals": "Test goal",
        "past_actions": [],
        "current_task": "Step 1",
        "response": "",
        "context": {"model_id": "test-model"},
        "current_node": "planner"
    }

@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response."""
    return {
        "content": '''
        {
            "goals": "Complete test task",
            "plan": [
                "Step 1: First action",
                "Step 2: Second action",
                "Step 3: Final action"
            ]
        }
        ''',
        "role": "assistant"
    }

def test_create_agent():
    """Test agent creation."""
    logger.info("Testing create_agent")
    try:
        mock_llm = MagicMock()
        agent = create_agent(mock_llm)
        
        assert "llm" in agent
        assert "tools" in agent
        assert "prompt" in agent
        logger.debug("Agent created successfully")
    except Exception as e:
        logger.error(f"Error in create_agent test: {str(e)}")
        raise

def test_extract_core_tasks():
    """Test core task extraction from plan."""
    logger.info("Testing extract_core_tasks")
    plan = ["Step 1", "Step 2", "Step 3"]
    
    try:
        tasks = extract_core_tasks(plan)
        assert len(tasks) == 3
        logger.debug(f"Extracted tasks: {tasks}")
    except Exception as e:
        logger.error(f"Error in extract_core_tasks test: {str(e)}")
        raise

def test_get_last_human_message(mock_state):
    """Test retrieving last human message."""
    logger.info("Testing get_last_human_message")
    try:
        message = get_last_human_message(mock_state["messages"])
        assert message is not None
        assert message.content == "Test task"
        logger.debug(f"Retrieved message: {message.content}")
    except Exception as e:
        logger.error(f"Error in get_last_human_message test: {str(e)}")
        raise

def test_parse_llm_result(mock_llm_response):
    """Test parsing LLM result."""
    logger.info("Testing parse_llm_result")
    try:
        result = parse_llm_result(mock_llm_response)
        assert "goals" in result
        assert "plan" in result
        assert len(result["plan"]) == 3
        logger.debug(f"Parsed result: {result}")
    except Exception as e:
        logger.error(f"Error in parse_llm_result test: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_planner(mock_state, mock_llm_response):
    """Test planner functionality."""
    logger.info("Testing planner")
    
    mock_llm = MagicMock()
    mock_llm.return_value = mock_llm_response
    
    with patch('llm.create_llm', return_value=mock_llm):
        try:
            result = planner(mock_state)
            assert result["current_node"] == "planner"
            assert len(result["plan"]) > 0
            assert result["goals"] != ""
            logger.debug(f"Planner result: {result}")
        except Exception as e:
            logger.error(f"Error in planner test: {str(e)}")
            raise

def test_task_executor(mock_state):
    """Test task executor functionality."""
    logger.info("Testing task_executor")
    
    mock_llm = MagicMock()
    mock_llm.return_value = {
        "content": '''
        {
            "action": "Task executed",
            "next_step": "Continue with plan"
        }
        ''',
        "role": "assistant"
    }
    
    with patch('llm.create_llm', return_value=mock_llm):
        try:
            result = task_executor(mock_state)
            assert result["current_node"] == "task_executor"
            assert len(result["past_actions"]) > 0
            logger.debug(f"Task executor result: {result}")
        except Exception as e:
            logger.error(f"Error in task_executor test: {str(e)}")
            raise

def test_project_updater(mock_state):
    """Test project updater functionality."""
    logger.info("Testing project_updater")
    try:
        result = project_updater(mock_state)
        assert result["current_node"] == "project_updater"
        assert "response" in result
        logger.debug(f"Project updater result: {result}")
    except Exception as e:
        logger.error(f"Error in project_updater test: {str(e)}")
        raise

def test_replanner(mock_state):
    """Test replanner functionality."""
    logger.info("Testing replanner")
    
    mock_llm = MagicMock()
    mock_llm.return_value = {
        "content": '''
        {
            "decision": "COMPLETE",
            "reasoning": "All tasks have been completed successfully."
        }
        ''',
        "role": "assistant"
    }
    
    with patch('llm.create_llm', return_value=mock_llm):
        try:
            result = replanner(mock_state)
            assert isinstance(result, AgentFinish)
            logger.debug(f"Replanner result: {result}")
        except Exception as e:
            logger.error(f"Error in replanner test: {str(e)}")
            raise

@pytest.mark.asyncio
async def test_run_paa():
    """Test the main PAA execution flow."""
    logger.info("Testing run_paa")
    
    mock_llm = MagicMock()
    mock_llm.return_value = {
        "content": '''
        {
            "goals": "Complete test task",
            "plan": ["Step 1", "Step 2", "Step 3"],
            "current_node": "planner"
        }
        ''',
        "role": "assistant"
    }
    
    with patch('llm.create_llm', return_value=mock_llm):
        try:
            async for status in run_paa("Test task", "test-model"):
                assert "current_node" in status
                logger.debug(f"PAA status: {status}")
        except Exception as e:
            logger.error(f"Error in run_paa test: {str(e)}")
            raise

def test_error_handling():
    """Test error handling across different components."""
    logger.info("Testing error handling")
    
    # Test planner error
    with patch('llm.create_llm', side_effect=Exception("Test error")):
        with pytest.raises(Exception) as exc_info:
            planner({"context": {"model_id": "test"}, "messages": []})
        logger.debug(f"Planner error caught: {exc_info.value}")
    
    # Test task executor error
    with patch('llm.create_llm', side_effect=Exception("Test error")):
        result = task_executor({"context": {"model_id": "test"}, "current_task": "test"})
        assert "error" in result["response"]
        logger.debug(f"Task executor error handled: {result}")
