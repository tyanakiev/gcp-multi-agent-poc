"""
Example ADK Agent with Tools - Demonstrates Google Cloud ADK pattern
"""

import asyncio
from core.agent import Agent
from core.types import AgentRole
from core.adk_tools import WebSearchTool, DataAnalysisTool, ContentGenerationTool


class ResearcherWithToolsAgent(Agent):
    """
    Researcher agent using Google Cloud ADK with tools for web search and data analysis.
    This demonstrates the ADK pattern from the example:

    agent = Agent(
        name="researcher",
        model="gemini-flash-latest",
        instruction="You help users research topics thoroughly.",
        tools=[google_search],
    )
    """

    def __init__(self, agent_id: str = "researcher_with_tools"):
        """Initialize researcher agent with tools"""
        instruction = """You are an expert research agent with access to multiple tools.
Your role is to:
1. Use web search to gather current information
2. Analyze data patterns and trends
3. Synthesize findings into coherent research reports
4. Provide comprehensive, well-sourced information

Use your available tools effectively to deliver thorough research."""

        super().__init__(
            agent_id=agent_id,
            role=AgentRole.RESEARCHER,
            instruction=instruction,
            tools=[
                WebSearchTool.definition(),
                DataAnalysisTool.definition(),
            ]
        )

    def get_description(self) -> str:
        return """Researcher with Tools: Uses web search and data analysis to conduct thorough research."""


class AnalystWithToolsAgent(Agent):
    """
    Analyst agent using ADK tools for data analysis and content generation.
    """

    def __init__(self, agent_id: str = "analyst_with_tools"):
        """Initialize analyst agent with tools"""
        instruction = """You are an expert analyst with advanced tools at your disposal.
Your role is to:
1. Analyze structured data to uncover insights
2. Generate detailed analytical reports
3. Identify trends and patterns
4. Provide actionable recommendations

Leverage your tools to deliver comprehensive analysis."""

        super().__init__(
            agent_id=agent_id,
            role=AgentRole.ANALYZER,
            instruction=instruction,
            tools=[
                DataAnalysisTool.definition(),
                ContentGenerationTool.definition(),
            ]
        )

    def get_description(self) -> str:
        return """Analyst with Tools: Uses data analysis and content generation to provide deep insights."""


class ContentCreatorWithToolsAgent(Agent):
    """
    Content creator agent using ADK tools for content generation.
    """

    def __init__(self, agent_id: str = "content_creator_with_tools"):
        """Initialize content creator agent with tools"""
        instruction = """You are an expert content creator with powerful generation tools.
Your role is to:
1. Generate high-quality, well-formatted content
2. Create content in multiple formats (markdown, HTML, etc.)
3. Tailor content length and style to requirements
4. Ensure content is engaging and well-structured

Use your tools to create professional, polished content."""

        super().__init__(
            agent_id=agent_id,
            role=AgentRole.WRITER,
            instruction=instruction,
            tools=[
                ContentGenerationTool.definition(),
            ]
        )

    def get_description(self) -> str:
        return """Content Creator with Tools: Uses advanced content generation to create polished, professional content."""


async def main():
    """Example usage of ADK agents with tools"""
    print("=" * 60)
    print("Google Cloud ADK Agent Examples with Tools")
    print("=" * 60)

    # Initialize agents
    researcher = ResearcherWithToolsAgent()
    analyst = AnalystWithToolsAgent()
    creator = ContentCreatorWithToolsAgent()

    print("\n1. Researcher Agent with Tools")
    print(f"   Description: {researcher.get_description()}")
    print(f"   Available Tools: {len(researcher.tools)}")
    print(f"   Model: {researcher.model}")
    print(f"   Role: {researcher.role.value}")

    print("\n2. Analyst Agent with Tools")
    print(f"   Description: {analyst.get_description()}")
    print(f"   Available Tools: {len(analyst.tools)}")
    print(f"   Model: {analyst.model}")
    print(f"   Role: {analyst.role.value}")

    print("\n3. Content Creator Agent with Tools")
    print(f"   Description: {creator.get_description()}")
    print(f"   Available Tools: {len(creator.tools)}")
    print(f"   Model: {creator.model}")
    print(f"   Role: {creator.role.value}")

    print("\n" + "=" * 60)
    print("Execution Example (simulated - requires API key)")
    print("=" * 60)

    # Example of how to use with actual execution
    # Uncomment when GOOGLE_API_KEY is configured
    # response = await researcher.execute(
    #     task="Research the latest developments in AI",
    #     context={"focus_area": "machine learning", "time_period": "last 6 months"}
    # )
    # print(f"\nResearch Output:\n{response.output}")

    print("\nTo use these agents:")
    print("1. Set GOOGLE_API_KEY environment variable")
    print("2. Call agent.execute() with a task")
    print("3. Agents will use their tools to complete the task")


if __name__ == "__main__":
    asyncio.run(main())

