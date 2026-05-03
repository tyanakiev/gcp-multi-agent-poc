"""
Advanced example: Custom Agent Creation

This example shows how to create your own custom agents
by extending the base Agent class.
"""

from core.agent import Agent
from core.types import AgentRole


class CustomAgent(Agent):
    """
    Example of a custom agent with domain-specific logic.

    You can extend the base Agent class to create specialized agents
    for your specific use cases.
    """

    def __init__(self, agent_id: str, domain: str):
        """
        Initialize a custom agent.

        Args:
            agent_id: Unique identifier
            domain: The domain this agent specializes in
        """
        system_prompt = f"""You are a specialized agent in the {domain} domain.
Your role is to provide expert analysis, insights, and recommendations
specific to {domain}. Be thorough, accurate, and domain-aware."""

        super().__init__(
            agent_id=agent_id,
            role=AgentRole.CUSTOM,
            system_prompt=system_prompt
        )
        self.domain = domain

    def get_description(self) -> str:
        """Get agent description"""
        return f"Custom Agent specialized in {self.domain}"


# Example: Create domain-specific agents
if __name__ == "__main__":
    # Create agents for different domains
    finance_agent = CustomAgent("finance_expert", "financial analysis")
    tech_agent = CustomAgent("tech_expert", "technology and software")
    healthcare_agent = CustomAgent("healthcare_expert", "healthcare and medicine")

    print("Custom Agents Created:")
    print(f"- {finance_agent.get_description()}")
    print(f"- {tech_agent.get_description()}")
    print(f"- {healthcare_agent.get_description()}")

