"""
Coordinator Agent - Specialized for coordinating and synthesizing
"""

from core.agent import Agent
from core.types import AgentRole


class CoordinatorAgent(Agent):
    """
    Agent specialized in coordination and synthesis.

    Responsibilities:
    - Coordinate activities between agents
    - Synthesize diverse inputs
    - Make strategic decisions
    - Provide overall guidance and direction
    """

    def __init__(self, agent_id: str = "coordinator"):
        """Initialize the coordinator agent with ADK pattern"""
        instruction = """You are an expert coordinator and synthesizer. Your role is to:
1. Coordinate activities and delegate tasks strategically
2. Synthesize diverse inputs into coherent outcomes
3. Make strategic decisions about task allocation
4. Provide overall guidance and direction
5. Ensure alignment across different components

Be strategic, collaborative, and focused on delivering integrated solutions."""

        super().__init__(
            agent_id=agent_id,
            role=AgentRole.COORDINATOR,
            instruction=instruction
        )

    def get_description(self) -> str:
        """Get agent description"""
        return """Coordinator Agent: Specialized in coordination and synthesis.
        Orchestrates activities between agents, makes strategic decisions,
        and synthesizes diverse inputs into coherent solutions."""

