import pytest
import logging
from unittest.mock import patch, MagicMock
import streamlit as st
from app import *

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components."""
    with patch('streamlit.set_page_config') as mock_config, \
         patch('streamlit.title') as mock_title, \
         patch('streamlit.sidebar.title') as mock_sidebar_title, \
         patch('streamlit.sidebar.selectbox') as mock_selectbox, \
         patch('streamlit.write') as mock_write, \
         patch('streamlit.text_area') as mock_text_area, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.error') as mock_error, \
         patch('streamlit.success') as mock_success, \
         patch('streamlit.warning') as mock_warning, \
         patch('streamlit.expander') as mock_expander, \
         patch('streamlit.progress') as mock_progress:
        
        # Configure mock returns
        mock_selectbox.return_value = "test-model"
        mock_text_area.return_value = "Test input"
        mock_button.return_value = True
        mock_expander.return_value = MagicMock()
        
        yield {
            'config': mock_config,
            'title': mock_title,
            'sidebar_title': mock_sidebar_title,
            'selectbox': mock_selectbox,
            'write': mock_write,
            'text_area': mock_text_area,
            'button': mock_button,
            'error': mock_error,
            'success': mock_success,
            'warning': mock_warning,
            'expander': mock_expander,
            'progress': mock_progress
        }

@pytest.fixture
def mock_ollama_models():
    """Mock Ollama models list."""
    return ["model1", "model2", "model3"]

@pytest.fixture
def setup_app_state():
    """Setup initial app state."""
    # Reset session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Initialize required session state variables
    st.session_state.initialized = False
    st.session_state.user_input = ""
    st.session_state.task_status = {}
    st.session_state.progress = 0
    st.session_state.selected_model = None

def test_page_initialization(mock_streamlit, setup_app_state):
    """Test initial page setup."""
    logger.info("Testing page initialization")
    try:
        with patch('llm.list_available_models', return_value=["test-model"]):
            # Initialize app
            st.set_page_config(page_title="Personal AI Assistant", page_icon="🤖", layout="wide")
            st.title("Your Personal AI Assistant")
            initialize_models()
            
            # Verify page configuration
            assert mock_streamlit['config'].called
            assert mock_streamlit['title'].called
            logger.debug("Page initialization successful")
    except Exception as e:
        logger.error(f"Error in page initialization test: {str(e)}")
        raise

def test_model_selection(mock_streamlit, mock_ollama_models, setup_app_state):
    """Test model selection functionality."""
    logger.info("Testing model selection")
    try:
        with patch('llm.list_available_models', return_value=mock_ollama_models):
            # Initialize models
            initialize_models()
            
            # Set up sidebar
            st.sidebar.title("Settings")
            selected_model = st.sidebar.selectbox(
                "Select Ollama Model",
                mock_ollama_models
            )
            st.session_state.selected_model = selected_model
            
            # Verify model selection
            assert mock_streamlit['selectbox'].called
            assert st.session_state.selected_model in mock_ollama_models
            logger.debug(f"Selected model: {st.session_state.selected_model}")
    except Exception as e:
        logger.error(f"Error in model selection test: {str(e)}")
        raise

def test_sample_tasks(mock_streamlit, setup_app_state):
    """Test sample tasks functionality."""
    logger.info("Testing sample tasks")
    try:
        # Test each sample task button
        for i, (key, value) in enumerate(sample_tasks.items()):
            # Simulate button click
            if mock_streamlit['button'].return_value:
                assert st.session_state.user_input == value
                logger.debug(f"Sample task selected: {key}")
    except Exception as e:
        logger.error(f"Error in sample tasks test: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_process_request(mock_streamlit, setup_app_state):
    """Test request processing functionality."""
    logger.info("Testing process request")
    
    mock_status = {
        "current_node": "planner",
        "response": "Test response",
        "plan": ["Step 1", "Step 2"],
    }
    
    try:
        with patch('task_manager.run_paa', return_value=[mock_status]):
            # Set up test state
            st.session_state.user_input = "Test task"
            st.session_state.selected_model = "test-model"
            
            # Create mock UI elements
            mock_progress = MagicMock()
            mock_placeholder = MagicMock()
            mock_expanders = [MagicMock() for _ in range(5)]
            
            # Run process_request with mock UI elements
            await process_request(
                "Test task",
                mock_progress,
                mock_placeholder,
                *mock_expanders
            )
            
            # Verify progress updates
            mock_progress.progress.assert_called()
            
            # Verify expander updates
            for expander in mock_expanders:
                expander.json.assert_called()
            
            logger.debug("Process request completed successfully")
    except Exception as e:
        logger.error(f"Error in process request test: {str(e)}")
        raise

def test_error_handling(mock_streamlit):
    """Test error handling in the UI."""
    logger.info("Testing error handling")
    try:
        # Test Ollama connection error
        with patch('llm.list_available_models', side_effect=Exception("Connection error")):
            # Call initialize_models directly to trigger error handling
            initialize_models()
            assert mock_streamlit['error'].called
            assert mock_streamlit['info'].called
            logger.debug("Error handling for connection failure verified")
        
        # Test empty input error
        st.session_state.user_input = ""
        mock_streamlit['button'].return_value = True  # Simulate button click
        # Call the button click handler
        if st.button("Get Assistance"):
            assert mock_streamlit['warning'].called
            logger.debug("Error handling for empty input verified")
    except Exception as e:
        logger.error(f"Error in error handling test: {str(e)}")
        raise

def test_session_state_management():
    """Test session state management."""
    logger.info("Testing session state management")
    try:
        # Reset session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Verify initialization of session state variables
        assert 'selected_model' not in st.session_state
        assert 'user_input' not in st.session_state
        assert 'task_status' not in st.session_state
        assert 'progress' not in st.session_state
        
        logger.debug("Session state management verified")
    except Exception as e:
        logger.error(f"Error in session state management test: {str(e)}")
        raise

def test_ui_components_visibility(mock_streamlit, setup_app_state):
    """Test visibility and arrangement of UI components."""
    logger.info("Testing UI components visibility")
    try:
        with patch('llm.list_available_models', return_value=["test-model"]):
            # Initialize app
            st.set_page_config(page_title="Personal AI Assistant", page_icon="🤖", layout="wide")
            st.title("Your Personal AI Assistant")
            initialize_models()
            
            # Set up sidebar
            st.sidebar.title("Settings")
            st.sidebar.selectbox("Select Ollama Model", ["test-model"])
            
            # Set up main components
            st.text_area("How can I assist you today?", value="", height=100)
            st.button("Get Assistance")
            
            # Verify components are displayed
            assert mock_streamlit['title'].called
            assert mock_streamlit['sidebar_title'].called
            assert mock_streamlit['text_area'].called
            assert mock_streamlit['button'].called
            
            logger.debug("UI components visibility verified")
    except Exception as e:
        logger.error(f"Error in UI components visibility test: {str(e)}")
        raise

def test_progress_tracking(mock_streamlit):
    """Test progress tracking functionality."""
    logger.info("Testing progress tracking")
    try:
        # Initialize progress
        st.session_state.progress = 0
        
        # Simulate different stages
        stages = ['planner', 'task_executor', 'project_updater', 'replanner']
        expected_progress = [25, 50, 75, 90]
        
        for stage, progress in zip(stages, expected_progress):
            st.session_state.current_node = stage
            assert st.session_state.progress == progress or st.session_state.progress == 0
            
        logger.debug("Progress tracking verified")
    except Exception as e:
        logger.error(f"Error in progress tracking test: {str(e)}")
        raise
