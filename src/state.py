from typing import Annotated, TypedDict, List, Tuple, Dict
from langchain_core.messages import BaseMessage
import operator


class State(TypedDict):
    messages: Annotated[List[BaseMessage], "The conversation history"]
    plan: List[str]
    goals: str
    past_actions: Annotated[List[Tuple[str, str]], operator.add]
    current_task: str
    response: str
    context: Annotated[Dict[str, str], "Additional context information"]
    current_node: str
