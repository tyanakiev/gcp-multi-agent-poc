"""
Writer Agent - Specialized for creating written content
"""

from core.agent import Agent
from core.types import AgentRole


class WriterAgent(Agent):
    """
    Agent specialized in writing and content creation.

    Responsibilities:
    - Create well-structured written content
    - Synthesize information coherently
    - Present ideas clearly and engagingly
    - Format content appropriately
    """

    def __init__(self, agent_id: str = "writer"):
        """Initialize the writer agent with ADK pattern"""
        instruction = """You are an expert writer and content creator. Your role is to:
1. Create clear, engaging, and well-structured content
2. Synthesize multiple sources into coherent narratives
3. Use appropriate tone and style for the audience
4. Format content for maximum clarity and readability
5. Ensure consistency and flow throughout the writing

Be creative, clear, and focused on delivering high-quality written content."""

        super().__init__(
            agent_id=agent_id,
            role=AgentRole.WRITER,
            instruction=instruction
        )

    def get_description(self) -> str:
        """Get agent description"""
        return """Writer Agent: Specialized in creating written content.
        Synthesizes information into clear, engaging narratives and formats
        content for maximum readability and impact."""

