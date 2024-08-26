import logging
import json
import re
import boto3
import inspect
from typing import Union, Dict, List, Tuple, AsyncGenerator, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.agents import AgentExecutor
from langchain_aws.chat_models.bedrock import ChatBedrock
from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from enum import Enum
from llm import create_llm
from tools import TOOLS
from state import State

logger = logging.getLogger(__name__)
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-west-2")


def create_agent(llm) -> AgentExecutor:
    """Sets up the AgentExecutor using the provided language model and tools."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant. Use the available tools to complete tasks.",
            ),
            ("human", "{input}"),
        ]
    )
    return AgentExecutor(agent=llm, tools=TOOLS, prompt=prompt, verbose=True)


def extract_core_tasks(plan: List[str]) -> List[str]:
    """Extracts the core tasks from a detailed plan."""
    logger.debug(f"Extracting core tasks from plan: {plan}")
    core_tasks = [line[2:].strip() for line in plan if line.startswith("")]
    logger.debug(f"Extracted core tasks: {core_tasks}")
    return core_tasks


def get_last_human_message(messages: List[BaseMessage]) -> Optional[HumanMessage]:
    """Retrieves the last human message from the conversation history."""
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return message
    return None


def parse_llm_result(result):
    """Parses the result from the LLM."""
    if isinstance(result, BaseMessage):
        content = result.content
    elif isinstance(result, dict) and "content" in result:
        content = result["content"]
    else:
        raise ValueError("Unexpected response format from LLM.")

    # Try to find JSON-like structure in the content
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # If no valid JSON found, return a structured dict with raw content
    return {
        "goals": "Could not parse goals",
        "plan": content.split("\n"),  # Split content into lines as a fallback plan
    }


def create_new_state(state: State, **kwargs) -> State:
    """Creates a new state with updated values."""
    new_state = state.copy()
    new_state.update(kwargs)
    return new_state


def planner(state: State) -> State:
    """Planner function to generate a step-by-step plan."""
    logger.info("Executing Planner")
    llm = create_llm(state["context"]["model_id"])

    last_human_message = get_last_human_message(state["messages"])
    if not last_human_message:
        raise ValueError("No human message found in the conversation history")

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content="You are a planning expert. Create a concise step-by-step minimum required plan with no more than 10 steps."
            ),
            HumanMessage(
                content=f"""
        Task: {last_human_message.content}
        
        Please provide a response in the following format:
        {{
            "goals": "Main goal of the task (1 sentence)",
            "plan": [
                "Step 1",
                "Step 2",
                "Step 3",
                "Step 4",
                "Step 5",
                ...
            ]
        }}
        Ensure the plan has no more than 10 steps.
        """
            ),
        ]
    )

    try:
        result = llm.invoke(prompt.format_messages())
        logger.debug(f"Raw LLM output: {result.content}")
        parsed_result = parse_llm_result(result)
        core_tasks = parsed_result["plan"]

        return create_new_state(
            state,
            plan=core_tasks,
            goals=parsed_result["goals"],
            current_task=core_tasks[0] if core_tasks else "",
            response="",
            current_node="planner",
        )
    except Exception as e:
        logger.error(f"Error in planner: {str(e)}", exc_info=True)
        raise


def task_executor(state: State) -> Union[Dict, AgentFinish]:
    logger.info("Executing Task Executor")

    if "context" not in state or "model_id" not in state["context"]:
        logger.error("Missing context or model_id in state")
        return handle_error(state, "Missing context or model_id")

    llm = ChatBedrock(model_id=state["context"]["model_id"], client=bedrock_runtime)
    llm_with_tools = llm.bind_tools(TOOLS)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant. Use the available tools to complete tasks.",
            ),
            (
                "human",
                "Task: {task}\nGoal: {goal}\n\nPlease complete this task using the available tools if necessary.",
            ),
        ]
    )

    tools_by_name = {tool.name: tool for tool in TOOLS}

    try:
        messages = prompt.format_messages(
            task=state["current_task"], goal=state["goals"]
        )
        result = llm_with_tools.invoke(messages)

        tool_calls = result.tool_calls

        response = ""
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            try:
                tool_args = tool_call["args"]
                tool_output = tools_by_name[tool_name].invoke(tool_args)

                response += f"Tool used: {tool_name}\nArgs: {tool_args}\nOutput: {tool_output}\n\n"
            except Exception as tool_error:
                logger.error(f"Error using tool {tool_name}: {str(tool_error)}")
                response += f"Error using tool {tool_name}: {str(tool_error)}\n\n"

        response += f"Final response: {result.content}"

        next_task_index = state["plan"].index(state["current_task"]) + 1
        next_task = (
            state["plan"][next_task_index]
            if next_task_index < len(state["plan"])
            else None
        )

        return {
            "past_actions": state["past_actions"] + [(state["current_task"], response)],
            "current_node": "task_executor",
            "response": response,
            "next_task": next_task,
            "plan": state["plan"],
            "goals": state["goals"],
            "context": state["context"],
        }
    except Exception as e:
        logger.error(f"Error in task_executor: {str(e)}", exc_info=True)
        return handle_error(state, str(e))


def handle_error(state: State, error_message: str) -> Dict:
    return {
        "past_actions": state["past_actions"]
        + [(state["current_task"], f"Error occurred: {error_message}")],
        "current_node": "task_executor",
        "response": f"Error occurred while executing the task: {error_message}",
        "next_task": None,
        "plan": state.get("plan", []),
        "goals": state.get("goals", ""),
        "context": state.get("context", {}),
    }


def project_updater(state: State) -> State:
    """Updates the project status."""
    logger.info("Executing Project Updater")
    last_action = (
        state["past_actions"][-1]
        if state["past_actions"]
        else ("No action", "No details")
    )

    # Include checklist in the update summary
    checklist_summary = "\n".join([f"- {task}" for task in state.get("plan", [])])
    summary = f"Completed task: {last_action[0]}. Action taken: {last_action[1]}\n\nChecklist:\n{checklist_summary}"

    return create_new_state(state, response=summary, current_node="project_updater")


class Decision(str, Enum):
    COMPLETE = "complete"
    REPLAN = "replan"
    CONTINUE = "continue"


class ReplannerOutput(BaseModel):
    decision: Decision
    reasoning: str
    new_plan: Optional[List[str]] = Field(
        None, description="New step-by-step plan if decision is 'replan'"
    )


def replanner(state: State) -> Union[Dict, AgentFinish]:
    logger.info("Executing Replanner")
    llm = create_llm(state["context"]["model_id"])

    structured_llm = llm.with_structured_output(ReplannerOutput)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a replanning expert. Evaluate the current progress and decide if the plan needs to be updated or if the task is complete.",
            ),
            (
                "human",
                "Original goal: {goals}\n"
                "Current plan:\n{plan}\n"
                "Completed actions:\n{past_actions}\n"
                "Last update:\n{response}\n\n"
                "Please provide your decision on whether the plan should be continued, updated, or marked as complete. "
                "If you decide to replan, provide a new step-by-step plan.",
            ),
        ]
    )

    try:
        messages = prompt.format_messages(
            goals=state["goals"],
            plan=state["plan"],
            past_actions=state["past_actions"],
            response=state["response"],
        )

        result = structured_llm.invoke(messages)

        if result.decision == Decision.COMPLETE:
            return AgentFinish(
                return_values={"output": result.reasoning},
                log="Task completed",
            )
        elif result.decision == Decision.REPLAN:
            return {
                "plan": result.new_plan,
                "current_task": result.new_plan[0] if result.new_plan else "",
                "current_node": "replanner",
            }
        else:  # continue
            return {
                "current_node": "replanner",
            }
    except Exception as e:
        logger.error(f"Error in replanner: {str(e)}", exc_info=True)
        return handle_error(state, str(e))


async def run_paa(question: str, model_id: str) -> AsyncGenerator[Dict, None]:
    logger.info(f"Running Personal AI Assistant with question: {question}")

    initial_state: State = {
        "messages": [
            SystemMessage(content="You are a helpful personal AI assistant."),
            HumanMessage(content=question),
        ],
        "plan": [],
        "goals": "",
        "past_actions": [],
        "current_task": "",
        "response": "",
        "context": {"model_id": model_id},
        "current_node": "planner",
    }

    try:
        current_state = initial_state
        while current_state["current_node"] != "end":
            logger.info(f"Current node: {current_state['current_node']}")

            if current_state["current_node"] == "planner":
                current_state = planner(current_state)
                if current_state["plan"]:
                    current_state["current_task"] = current_state["plan"][0]
                    current_state["current_node"] = "task_executor"
                else:
                    current_state["current_node"] = "end"
            elif current_state["current_node"] == "task_executor":
                current_state = task_executor(current_state)
                if current_state["next_task"]:
                    current_state["current_task"] = current_state["next_task"]
                    current_state["current_node"] = "task_executor"
                else:
                    current_state["current_node"] = "project_updater"
            elif current_state["current_node"] == "project_updater":
                current_state = project_updater(current_state)
                current_state["current_node"] = "replanner"
            elif current_state["current_node"] == "replanner":
                result = replanner(current_state)
                if isinstance(result, AgentFinish):
                    yield {
                        "current_node": "end",
                        "response": result.return_values.get(
                            "output", "Task completed"
                        ),
                        "plan": current_state.get("plan", []),
                        "goals": current_state.get("goals", ""),
                        "current_task": "",
                        "past_actions": current_state.get("past_actions", []),
                    }
                    break
                else:
                    current_state.update(result)
            yield {
                "current_node": current_state["current_node"],
                "response": current_state.get("response", ""),
                "plan": current_state.get("plan", []),
                "goals": current_state.get("goals", ""),
                "current_task": current_state.get("current_task", ""),
                "past_actions": current_state.get("past_actions", []),
            }

        logger.info("Workflow completed")
        yield {"final_answer": current_state.get("response", "Task completed")}

    except Exception as e:
        logger.error(f"Error occurred in run_paa: {str(e)}", exc_info=True)
        yield {"error": str(e)}
