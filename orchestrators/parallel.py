"""
Parallel Orchestrator - Use Case 2

Executes multiple agents simultaneously on independent tasks.
Best for analyzing different aspects concurrently or parallel processing.

Flow: Agent1
      Agent2  -> Aggregate Results -> Final Output
      Agent3
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from core.orchestrator import Orchestrator
from core.types import OrchestrationStrategy, Task, AgentResponse
from core.agent import Agent

logger = logging.getLogger(__name__)


class ParallelOrchestrator(Orchestrator):
    """
    Parallel orchestration strategy.

    Multiple agents execute simultaneously on independent tasks.
    All tasks run concurrently and results are aggregated at the end.
    """

    def __init__(self, orchestrator_id: str, agents: Dict[str, Agent]):
        """Initialize parallel orchestrator"""
        super().__init__(orchestrator_id, OrchestrationStrategy.PARALLEL, agents)

    async def _execute_strategy(
        self,
        tasks: List[Task],
        initial_context: Optional[Dict[str, Any]] = None
    ) -> List[AgentResponse]:
        """
        Execute all tasks in parallel.

        All agents work independently and concurrently.
        """
        context = initial_context or {}

        logger.info(f"Starting parallel execution of {len(tasks)} tasks")

        # Create coroutines for all tasks
        execution_tasks = []
        for task in tasks:
            agent = self.get_agent(task.agent_role.value)

            if not agent:
                logger.error(f"Agent {task.agent_role.value} not found")
                # Still add to tasks to maintain order
                execution_tasks.append(self._error_response(task.agent_role.value))
            else:
                # Execute agent with the provided context
                execution_tasks.append(
                    agent.execute(task.description, context)
                )

        # Execute all tasks concurrently
        responses = await asyncio.gather(*execution_tasks)

        logger.info(f"All {len(tasks)} tasks completed")

        return responses

    async def _error_response(self, agent_id: str) -> AgentResponse:
        """Generate error response for missing agent"""
        return AgentResponse(
            agent_id=agent_id,
            output="",
            status="error",
            execution_time=0,
            error=f"Agent {agent_id} not found"
        )

    def _aggregate_results(self, responses: List[AgentResponse]) -> str:
        """
        Aggregate parallel results, organizing by agent.
        """
        summary = "Parallel Processing Results:\n"
        summary += "=" * 50 + "\n\n"

        successful_count = 0
        error_count = 0
        total_time = 0

        for response in responses:
            total_time += response.execution_time

            if response.status == "success":
                successful_count += 1
                summary += f"✓ {response.agent_id}:\n"
                summary += f"{response.output}\n"
                summary += f"(Execution time: {response.execution_time:.2f}s)\n\n"
            else:
                error_count += 1
                summary += f"✗ {response.agent_id}: ERROR - {response.error}\n\n"

        # Add summary statistics
        summary += "=" * 50 + "\n"
        summary += f"Successful: {successful_count}/{len(responses)}\n"
        summary += f"Errors: {error_count}/{len(responses)}\n"
        summary += f"Total Execution Time: {total_time:.2f}s\n"

        return summary

