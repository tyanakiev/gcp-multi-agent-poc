"""
Sequential Orchestrator - Use Case 1

Executes agents one after another, with each agent receiving the output
from the previous one. Best for data pipelines and step-by-step processes.

Flow: Agent1 -> Agent2 -> Agent3 -> ... -> Final Output
"""

import logging
from typing import Dict, List, Optional, Any

from core.orchestrator import Orchestrator
from core.types import OrchestrationStrategy, Task, AgentResponse
from core.agent import Agent

logger = logging.getLogger(__name__)


class SequentialOrchestrator(Orchestrator):
    """
    Sequential orchestration strategy.

    Agents execute in order, with each agent's output becoming the next agent's input.
    """

    def __init__(self, orchestrator_id: str, agents: Dict[str, Agent]):
        """Initialize sequential orchestrator"""
        super().__init__(orchestrator_id, OrchestrationStrategy.SEQUENTIAL, agents)

    async def _execute_strategy(
        self,
        tasks: List[Task],
        initial_context: Optional[Dict[str, Any]] = None
    ) -> List[AgentResponse]:
        """
        Execute tasks sequentially.

        Each task is executed by the corresponding agent, and the output
        is passed as context to the next task.
        """
        responses = []
        context = initial_context or {}

        for i, task in enumerate(tasks):
            agent = self.get_agent(task.agent_role.value)

            if not agent:
                logger.error(f"Agent {task.agent_role.value} not found")
                responses.append(
                    AgentResponse(
                        agent_id=task.agent_role.value,
                        output="",
                        status="error",
                        execution_time=0,
                        error=f"Agent {task.agent_role.value} not found"
                    )
                )
                continue

            # Execute agent with accumulated context
            logger.info(f"Executing task {i+1}/{len(tasks)}: {task.task_id}")
            response = await agent.execute(task.description, context)
            responses.append(response)

            # Add previous output to context for next agent
            context[f"previous_output_{i}"] = response.output
            context["previous_agent"] = response.agent_id

            # Update context with task parameters
            context.update(task.parameters)

            if response.status != "success":
                logger.warning(f"Task {task.task_id} failed: {response.error}")

        return responses

    def _aggregate_results(self, responses: List[AgentResponse]) -> str:
        """
        Aggregate sequential results, highlighting the final output
        from the last successful agent.
        """
        successful_responses = [r for r in responses if r.status == "success"]

        if not successful_responses:
            return "No successful agent outputs"

        # Return the output from the last successful agent
        final_output = successful_responses[-1].output

        # Include intermediate steps for context
        summary = "Sequential Processing Results:\n"
        summary += "=" * 50 + "\n\n"

        for i, response in enumerate(responses, 1):
            if response.status == "success":
                summary += f"Step {i} ({response.agent_id}):\n"
                summary += f"{response.output}\n"
                summary += f"(Execution time: {response.execution_time:.2f}s)\n\n"
            else:
                summary += f"Step {i} ({response.agent_id}): ERROR - {response.error}\n\n"

        return summary

