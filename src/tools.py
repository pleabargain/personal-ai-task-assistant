from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel


@tool
def call_calendar(query: str) -> str:
    """Calls the Google Calendar API to perform various calendar operations."""
    return f"Calendar operation performed: {query}"


@tool
def get_contact(name: str) -> str:
    """Retrieves contact information for a given name."""
    return f"Contact info for {name}: email@example.com, 123-456-7890"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Sends an email to a specified recipient with a subject and message body."""
    return f"Email sent to {to} with subject: {subject}\nbody: {body}"


@tool
def web_search(query: str) -> str:
    """Performs a web search based on the given query string."""
    return f"Web search results for: {query}"


# List of available tools
TOOLS = [call_calendar, get_contact, send_email, web_search]
