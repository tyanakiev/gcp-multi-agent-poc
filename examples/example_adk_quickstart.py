"""
ADK Quick Start - Simple example showing the Google Cloud ADK pattern

This demonstrates the ADK pattern from the example:

from google.adk import Agent
from google.adk.tools import google_search

agent = Agent(
    name="researcher",
    model="gemini-flash-latest",
    instruction="You help users research topics thoroughly.",
    tools=[google_search],
)
"""

import asyncio
from core.agent import Agent
from core.types import AgentRole
from core.adk_tools import WebSearchTool


class QuickStartResearcherAgent(Agent):
    """
    Simple researcher agent following the ADK pattern

    This is the direct translation of:
    agent = Agent(
        name="researcher",
        model="gemini-flash-latest",
        instruction="You help users research topics thoroughly.",
        tools=[google_search],
    )
    """

    def __init__(self):
        """Initialize using the ADK pattern"""
        # This directly follows the Google ADK pattern:
        # Agent(name, model, instruction, tools)
        super().__init__(
            agent_id="researcher",
            role=AgentRole.RESEARCHER,
            instruction="You help users research topics thoroughly.",
            model="gemini-2.0-flash",  # Using latest Gemini Flash model
            tools=[WebSearchTool.definition()]
        )

    def get_description(self) -> str:
        return "Researcher agent that helps with thorough research using web search."


async def main():
    """Demonstrate basic ADK agent usage"""
    print("Google Cloud ADK Pattern - Quick Start")
    print("=" * 50)
    print()
    print("Code Pattern:")
    print("-" * 50)
    print("from google.adk import Agent")
    print("from google.adk.tools import google_search")
    print()
    print("agent = Agent(")
    print('    name="researcher",')
    print('    model="gemini-flash-latest",')
    print('    instruction="You help users research topics thoroughly.",')
    print("    tools=[google_search],")
    print(")")
    print("-" * 50)
    print()

    # Create agent
    agent = QuickStartResearcherAgent()

    print(f"Agent Created: {agent.agent_id}")
    print(f"Model: {agent.model}")
    print(f"Role: {agent.role.value}")
    print(f"Tools Available: {len(agent.tools)}")
    print(f"Instruction: {agent.instruction[:50]}...")
    print()

    # Example of using the agent
    print("Usage Example:")
    print("-" * 50)
    print("response = await agent.execute(")
    print('    task="Research recent AI developments",')
    print('    context={"focus": "machine learning"}')
    print(")")
    print("-" * 50)
    print()
    print("Notes:")
    print("- Set GOOGLE_API_KEY environment variable to use the agent")
    print("- The agent will use Generative AI if ADK is not available")
    print("- Tools are available for extended capabilities")
    print("- Supports async execution for concurrent agent operations")


if __name__ == "__main__":
    asyncio.run(main())

