"""
Analyzer Agent - Specialized for analyzing and interpreting information
"""

from core.agent import Agent
from core.types import AgentRole


class AnalyzerAgent(Agent):
    """
    Agent specialized in analysis and interpretation.

    Responsibilities:
    - Analyze complex information
    - Identify patterns and trends
    - Provide insights and interpretations
    - Break down complex concepts
    """

    def __init__(self, agent_id: str = "analyzer"):
        """Initialize the analyzer agent with ADK pattern"""
        instruction = """You are an expert analysis agent. Your role is to:
1. Analyze information deeply and critically
2. Identify patterns, trends, and relationships
3. Provide clear insights and interpretations
4. Break down complex concepts into understandable components
5. Offer data-driven conclusions

Be analytical, insightful, and provide clear reasoning for your conclusions."""

        super().__init__(
            agent_id=agent_id,
            role=AgentRole.ANALYZER,
            instruction=instruction
        )

    def get_description(self) -> str:
        """Get agent description"""
        return """Analyzer Agent: Specialized in analyzing and interpreting information.
        Identifies patterns, provides insights, and offers data-driven analysis
        and conclusions."""

