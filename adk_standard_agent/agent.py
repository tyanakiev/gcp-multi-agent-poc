"""
Canonical ADK entrypoint: defines root_agent for the official CLI and web UI.

Run from repository root (ensure this directory's parent is on PYTHONPATH, e.g. repo root):
  adk run adk_standard_agent
  adk web --port 8000
"""

from google.adk import Agent


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for information on a given topic.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default: 5).
    """
    return f"Search results for '{query}' (simulated, max_results={max_results})"


root_agent = Agent(
    model="gemini-2.5-flash",
    name="poc_root_agent",
    description="Proof-of-concept root agent with a simulated web search tool.",
    instruction=(
        "You are a helpful research assistant for the gcp-multi-agent-poc project. "
        "Use the web_search tool when the user asks for current or external information."
    ),
    tools=[web_search],
)
