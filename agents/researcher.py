"""
Research Agent - Specialized for gathering and researching information
"""

from core.agent import Agent
from core.types import AgentRole


class ResearcherAgent(Agent):
    """
    Agent specialized in research and information gathering.

    Responsibilities:
    - Gather relevant information
    - Research topics thoroughly
    - Provide comprehensive background
    """

    def __init__(self, agent_id: str = "researcher"):
        """Initialize the researcher agent with ADK pattern"""
        instruction = """You are an expert research agent. Your role is to:
1. Gather comprehensive information on topics
2. Research thoroughly and provide accurate details
3. Summarize findings clearly and concisely
4. Highlight key facts and important context
5. Provide sources and references when possible

Be thorough, accurate, and focus on delivering high-quality research."""

        super().__init__(
            agent_id=agent_id,
            role=AgentRole.RESEARCHER,
            instruction=instruction
        )

    def get_description(self) -> str:
        """Get agent description"""
        return """Researcher Agent: Specialized in gathering and analyzing information.
        Gathers comprehensive research, identifies key facts, and provides detailed
        background information for topics."""

