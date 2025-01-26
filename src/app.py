import streamlit as st
import asyncio
import json
from task_manager import run_paa
from llm import list_available_models
from logging_config import setup_logging

# Initialize logging and get log paths
logger, log_paths = setup_logging()

# Initialize available models
available_models = []

def initialize_models():
    global available_models
    try:
        logger.info("Fetching available Ollama models")
        available_models = list_available_models()
        if not available_models:
            error_msg = "No Ollama models found"
            logger.error(error_msg)
            st.error(f"{error_msg}. Please ensure Ollama is running and models are installed.")
            st.info(f"Check error log for details: {log_paths['error_log']}")
            return False
        logger.info(f"Found {len(available_models)} available models: {available_models}")
        return True
    except Exception as e:
        error_msg = f"Failed to connect to Ollama: {str(e)}"
        logger.error(error_msg, exc_info=True)
        st.error(error_msg)
        st.info(f"Please ensure Ollama is running (ollama serve) and try again.")
        st.info(f"Check error log for details: {log_paths['error_log']}")
        return False

# Set page config and title
st.set_page_config(page_title="Personal AI Assistant", page_icon="🤖", layout="wide")
st.title("Your Personal AI Assistant")

# Initialize models
initialize_models()

# Initialize Streamlit session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'task_status' not in st.session_state:
    st.session_state.task_status = {}
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = available_models[0] if available_models else None

st.sidebar.title("Settings")
st.session_state.selected_model = st.sidebar.selectbox(
    "Select Ollama Model", available_models
)

st.write(f"Selected Model: {st.session_state.selected_model}")

# Sample tasks
sample_tasks = {
    "Schedule Meeting": "Schedule a meeting with Eric for next Tuesday at 2 PM.",
    "Draft Email": "Draft a polite email to decline a vendor's proposal.",
    "Research": "Find the latest statistics on renewable energy adoption in Europe.",
    "Task Planning": "Create a to-do list for planning a team building event.",
    "Summarize Document": "Summarize the key points from the attached quarterly report.",
}

st.write("Sample Tasks:")
cols = st.columns(len(sample_tasks))
for i, (key, value) in enumerate(sample_tasks.items()):
    if cols[i].button(key, key=f"sample_{i}"):
        st.session_state.user_input = value

# User input text area
user_input = st.text_area(
    "How can I assist you today?",
    value=st.session_state.user_input,
    height=100,
    key="user_input",
)

async def process_request(
    user_input: str,
    progress_bar,
    status_placeholder,
    input_expander,
    planner_expander,
    task_expander,
    update_expander,
    replan_expander
):
    """Process a user request and update the UI with progress."""
    try:
        logger.info("Starting PAA execution")
        async for status in run_paa(user_input, st.session_state.selected_model):
            logger.debug(f"Received status update: {status}")
            if "error" in status:
                error_msg = status['error']
                logger.error(f"PAA execution error: {error_msg}")
                st.error(f"An error occurred: {error_msg}")
                st.info(f"Check error log for details: {log_paths['error_log']}")
                if "traceback" in status:
                    logger.error(f"Error traceback: {status['traceback']}")
                    st.code(status["traceback"], language="python")
                    st.info(f"Full error details have been logged to: {log_paths['error_log']}")
                break

            current_node = status.get("current_node")

            if current_node == "end":
                # Final response handling
                logger.info("Task execution completed successfully")
                st.success("Task Completed")
                final_response = status.get("response", "Task completed")
                logger.debug(f"Final response: {final_response}")
                st.write("Final Response:", final_response)
                progress_bar.progress(100)
                status_placeholder.write("Task Completed")

                # Final status display
                final_status_expander = st.expander(
                    "Final Status", expanded=True
                )
                final_status_expander.json(status)
                break

            if current_node:
                if current_node not in st.session_state.task_status:
                    st.session_state.task_status[current_node] = {
                        "status": "In Progress",
                        "details": "",
                    }

                if current_node == "planner":
                    planner_expander.json(status)
                    if "plan" in status:
                        task_checklist = task_expander.empty()
                        task_checklist.write("#### Task Checklist")
                        for i, task in enumerate(status["plan"]):
                            task_checklist.checkbox(task, key=f"task_{i}")
                    st.session_state.progress = 25
                elif current_node == "task_executor":
                    task_expander.json(status)
                    st.session_state.progress = 50
                elif current_node == "project_updater":
                    update_expander.json(status)
                    st.session_state.progress = 75
                elif current_node == "replanner":
                    replan_expander.json(status)
                    st.session_state.progress = 90

                st.session_state.task_status[current_node]["status"] = "Completed"
                progress_bar.progress(st.session_state.progress)
                status_placeholder.write(f"Current step: {current_node}")

    except Exception as e:
        error_msg = "Unexpected error during request processing"
        logger.error(error_msg, exc_info=True)
        st.error(f"An error occurred: {str(e)}")
        st.info(f"Check error log for details: {log_paths['error_log']}")
        st.exception(e)

# Handle assistance button click
if st.button("Get Assistance"):
    if user_input:
        logger.info(f"Processing new request with model: {st.session_state.selected_model}")
        logger.debug(f"User input: {user_input}")
        st.session_state.task_status = {}
        st.session_state.progress = 0

        # Create placeholders for each step
        input_expander = st.expander("Input", expanded=True)
        planner_expander = st.expander("Planning", expanded=True)
        task_expander = st.expander("Task Execution", expanded=False)
        update_expander = st.expander("Project Update", expanded=False)
        replan_expander = st.expander("Replanning", expanded=False)

        input_expander.write(user_input)

        progress_bar = st.progress(0)
        status_placeholder = st.empty()

        # Run the async function
        asyncio.run(process_request(
            user_input,
            progress_bar,
            status_placeholder,
            input_expander,
            planner_expander,
            task_expander,
            update_expander,
            replan_expander
        ))
    else:
        logger.warning("Attempted to submit empty task")
        st.warning("Please enter a task or question.")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p class='footer'>© 2024 Your Personal AI Assistant</p>", unsafe_allow_html=True
)
