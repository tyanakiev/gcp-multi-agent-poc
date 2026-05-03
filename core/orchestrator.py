"""
Base Orchestrator class for coordinating multiple agents
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from core.types import OrchestrationStrategy, Task, AgentResponse, OrchestrationResult
from core.agent import Agent

logger = logging.getLogger(__name__)


class Orchestrator(ABC):
    """
    Base class for orchestration strategies.

    Responsible for:
    - Managing multiple agents
    - Coordinating execution flow
    - Aggregating results
    - Error handling
    """

    def __init__(
        self,
        orchestrator_id: str,
        strategy: OrchestrationStrategy,
        agents: Dict[str, Agent]
    ):
        """
        Initialize orchestrator.

        Args:
            orchestrator_id: Unique identifier
            strategy: Orchestration strategy
            agents: Dictionary of agents keyed by ID
        """
        self.orchestrator_id = orchestrator_id
        self.strategy = strategy
        self.agents = agents
        self.execution_log = []

    async def orchestrate(
        self,
        tasks: List[Task],
        initial_context: Optional[Dict[str, Any]] = None
    ) -> OrchestrationResult:
        """
        Execute orchestration based on strategy.

        Args:
            tasks: List of tasks to execute
            initial_context: Initial context for agents

        Returns:
            OrchestrationResult with all agent responses
        """
        start_time = time.time()

        logger.info(f"Starting {self.strategy.value} orchestration with {len(tasks)} tasks")

        agent_responses = await self._execute_strategy(tasks, initial_context)

        execution_time = time.time() - start_time

        # Generate final output
        final_output = self._aggregate_results(agent_responses)

        result = OrchestrationResult(
            strategy=self.strategy,
            total_execution_time=execution_time,
            agent_responses=agent_responses,
            final_output=final_output,
            metadata={
                "orchestrator_id": self.orchestrator_id,
                "num_agents": len(self.agents),
                "num_tasks": len(tasks)
            }
        )

        self.execution_log.append(result)

        logger.info(f"Orchestration completed in {execution_time:.2f}s")

        return result

    @abstractmethod
    async def _execute_strategy(
        self,
        tasks: List[Task],
        initial_context: Optional[Dict[str, Any]]
    ) -> List[AgentResponse]:
        """
        Execute strategy-specific orchestration logic.

        Implemented by subclasses.
        """
        pass

    def _aggregate_results(self, responses: List[AgentResponse]) -> str:
        """
        Aggregate agent responses into final output.

        Can be overridden by subclasses for custom aggregation.
        """
        outputs = []
        for response in responses:
            if response.status == "success":
                outputs.append(f"[{response.agent_id}]: {response.output}")
            else:
                outputs.append(f"[{response.agent_id}] ERROR: {response.error}")

        return "\n\n".join(outputs)

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)

    def add_agent(self, agent_id: str, agent: Agent):
        """Add an agent to the orchestrator"""
        self.agents[agent_id] = agent
        logger.info(f"Added agent {agent_id}")

    def get_execution_log(self) -> list:
        """Get execution log"""
        return self.execution_log

    def get_summary(self) -> str:
        """Get a summary of orchestrator performance"""
        if not self.execution_log:
            return "No executions yet"

        total_time = sum(r.total_execution_time for r in self.execution_log)
        avg_time = total_time / len(self.execution_log)

        return f"""
Orchestrator: {self.orchestrator_id}
Strategy: {self.strategy.value}
Executions: {len(self.execution_log)}
Total Time: {total_time:.2f}s
Average Time: {avg_time:.2f}s
Agents: {len(self.agents)}
        """

