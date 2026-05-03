"""
Advanced example: Custom Orchestrator Creation

This example shows how to create your own custom orchestrators
by extending the base Orchestrator class.
"""

import logging
from typing import Dict, List, Optional, Any

from core.orchestrator import Orchestrator
from core.types import OrchestrationStrategy, Task, AgentResponse
from core.agent import Agent

logger = logging.getLogger(__name__)


class CustomOrchestrator(Orchestrator):
    """
    Example of a custom orchestrator implementing a unique strategy.

    This example implements a "Round-Robin" strategy where agents
    are selected in rotation to handle tasks.
    """

    def __init__(self, orchestrator_id: str, agents: Dict[str, Agent]):
        """Initialize custom orchestrator"""
        # Use a custom strategy
        super().__init__(orchestrator_id, OrchestrationStrategy.SEQUENTIAL, agents)
        self.strategy_name = "round_robin"
        self.agent_list = list(agents.keys())
        self.current_index = 0

    async def _execute_strategy(
        self,
        tasks: List[Task],
        initial_context: Optional[Dict[str, Any]] = None
    ) -> List[AgentResponse]:
        """
        Execute tasks using round-robin agent selection.

        Agents are selected in rotation regardless of task role.
        """
        responses = []
        context = initial_context or {}

        for i, task in enumerate(tasks):
            # Select agent in round-robin fashion
            agent_id = self.agent_list[self.current_index % len(self.agent_list)]
            agent = self.get_agent(agent_id)

            self.current_index += 1

            if not agent:
                logger.error(f"Agent {agent_id} not found")
                responses.append(
                    AgentResponse(
                        agent_id=agent_id,
                        output="",
                        status="error",
                        execution_time=0,
                        error=f"Agent {agent_id} not found"
                    )
                )
                continue

            logger.info(f"Task {i+1} assigned to {agent_id} (round-robin)")
            response = await agent.execute(task.description, context)
            responses.append(response)

            # Update context
            context[f"output_{i}"] = response.output

        return responses

    def _aggregate_results(self, responses: List[AgentResponse]) -> str:
        """Aggregate results with round-robin information"""
        summary = "Round-Robin Orchestration Results:\n"
        summary += "=" * 50 + "\n\n"

        for i, response in enumerate(responses, 1):
            if response.status == "success":
                summary += f"Task {i} (Agent: {response.agent_id}):\n"
                summary += f"{response.output}\n\n"
            else:
                summary += f"Task {i} (Agent: {response.agent_id}): ERROR - {response.error}\n\n"

        return summary


# Example usage documentation
if __name__ == "__main__":
    print("""
    Custom Orchestrator Example
    
    This example demonstrates how to create a custom orchestrator
    by extending the base Orchestrator class.
    
    Key points:
    1. Define your custom strategy logic in _execute_strategy()
    2. Optionally override _aggregate_results() for custom output
    3. Implement any additional methods your strategy needs
    
    The example here uses a round-robin strategy where agents
    are selected in rotation to handle tasks.
    
    Usage:
        from examples.example_custom_orchestrator import CustomOrchestrator
        
        orchestrator = CustomOrchestrator("custom_1", agents)
        result = await orchestrator.orchestrate(tasks)
    """)

