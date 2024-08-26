import streamlit as st
import asyncio
import json
from task_manager import run_paa

st.set_page_config(page_title="Personal AI Assistant", page_icon="🤖", layout="wide")

st.title("Your Personal AI Assistant")

bedrock_models = [
    "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
]

if "selected_model" not in st.session_state:
    st.session_state.selected_model = bedrock_models[0]

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "task_status" not in st.session_state:
    st.session_state.task_status = {}

if "progress" not in st.session_state:
    st.session_state.progress = 0

st.sidebar.title("Settings")
st.session_state.selected_model = st.sidebar.selectbox(
    "Select Bedrock Model", bedrock_models
)

st.write(f"Selected Model: {st.session_state.selected_model}")

# Sample tasks (기존과 동일하게 유지)
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

if st.button("Get Assistance"):
    if user_input:
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

        async def process_request():
            try:
                async for status in run_paa(
                    user_input, st.session_state.selected_model
                ):
                    if "error" in status:
                        st.error(f"An error occurred: {status['error']}")
                        if "traceback" in status:
                            st.code(status["traceback"], language="python")
                        break

                    current_node = status.get("current_node")

                    if current_node == "end":
                        # 최종 응답 처리
                        st.success("Task Completed")
                        st.write(
                            "Final Response:", status.get("response", "Task completed")
                        )
                        progress_bar.progress(100)
                        status_placeholder.write("Task Completed")

                        # 최종 상태 표시
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

                        st.session_state.task_status[current_node][
                            "status"
                        ] = "Completed"
                        progress_bar.progress(st.session_state.progress)
                        status_placeholder.write(f"Current step: {current_node}")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

        # Run the async function
        asyncio.run(process_request())
    else:
        st.warning("Please enter a task or question.")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p class='footer'>© 2024 Your Personal AI Assistant</p>", unsafe_allow_html=True
)
