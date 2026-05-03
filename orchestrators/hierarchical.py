"""
Hierarchical Orchestrator - Use Case 3

One coordinator agent manages and delegates to worker agents.
Best for complex tasks requiring supervision and coordination.

Flow: Coordinator Agent
         |
         +-> Worker Agent 1
         |
         +-> Worker Agent 2
         |
         +-> Worker Agent 3
         |
         Synthesize Results
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from core.orchestrator import Orchestrator
from core.types import OrchestrationStrategy, Task, AgentResponse, AgentRole
from core.agent import Agent

logger = logging.getLogger(__name__)


class HierarchicalOrchestrator(Orchestrator):
    """
    Hierarchical orchestration strategy.

    A coordinator agent delegates tasks to worker agents and synthesizes results.
    The coordinator can make decisions about which workers to use and how to combine results.
    """

    def __init__(
        self,
        orchestrator_id: str,
        agents: Dict[str, Agent],
        coordinator_id: str = "coordinator"
    ):
        """
        Initialize hierarchical orchestrator.

        Args:
            orchestrator_id: ID for the orchestrator
            agents: Dictionary of available agents
            coordinator_id: ID of the coordinator agent (default: "coordinator")
        """
        super().__init__(orchestrator_id, OrchestrationStrategy.HIERARCHICAL, agents)
        self.coordinator_id = coordinator_id

    async def _execute_strategy(
        self,
        tasks: List[Task],
        initial_context: Optional[Dict[str, Any]] = None
    ) -> List[AgentResponse]:
        """
        Execute hierarchical orchestration.

        1. Coordinator analyzes the tasks
        2. Coordinator delegates to appropriate workers
        3. Workers execute in parallel
        4. Coordinator synthesizes results
        """
        context = initial_context or {}
        responses = []

        # Step 1: Coordinator analyzes tasks
        logger.info("Coordinator analyzing tasks")
        task_description = self._describe_tasks(tasks)

        coordinator = self.get_agent(self.coordinator_id)
        if not coordinator:
            logger.error(f"Coordinator {self.coordinator_id} not found")
            return self._error_responses(tasks)

        # Coordinator decides on delegation strategy
        coordination_response = await coordinator.execute(
            f"Analyze these tasks and decide how to delegate them to workers:\n{task_description}",
            context
        )
        responses.append(coordination_response)

        if coordination_response.status != "success":
            logger.error(f"Coordinator failed: {coordination_response.error}")
            return responses

        # Step 2: Execute worker tasks in parallel
        logger.info(f"Delegating {len(tasks)} tasks to workers")

        worker_execution_tasks = []
        for task in tasks:
            agent = self.get_agent(task.agent_role.value)

            if not agent:
                logger.warning(f"Agent {task.agent_role.value} not found, skipping")
                worker_execution_tasks.append(
                    self._error_response(task.agent_role.value)
                )
            else:
                # Include coordination guidance in context
                task_context = dict(context)
                task_context["coordination_guidance"] = coordination_response.output

                worker_execution_tasks.append(
                    agent.execute(task.description, task_context)
                )

        # Execute all workers concurrently
        worker_responses = await asyncio.gather(*worker_execution_tasks)
        responses.extend(worker_responses)

        # Step 3: Coordinator synthesizes results
        logger.info("Coordinator synthesizing results")

        synthesis_prompt = self._create_synthesis_prompt(worker_responses, tasks)
        synthesis_response = await coordinator.execute(
            synthesis_prompt,
            context
        )
        responses.append(synthesis_response)

        return responses

    def _describe_tasks(self, tasks: List[Task]) -> str:
        """Create a description of tasks for the coordinator"""
        description = ""
        for i, task in enumerate(tasks, 1):
            description += f"{i}. {task.description} (Role: {task.agent_role.value})\n"
        return description

    def _create_synthesis_prompt(
        self,
        worker_responses: List[AgentResponse],
        tasks: List[Task]
    ) -> str:
        """Create a prompt for synthesizing worker results"""
        prompt = "Synthesize the following worker outputs into a cohesive final result:\n\n"

        for response in worker_responses:
            if response.status == "success":
                prompt += f"From {response.agent_id}:\n{response.output}\n\n"
            else:
                prompt += f"From {response.agent_id}: ERROR - {response.error}\n\n"

        prompt += "\nProvide a final, integrated summary that combines all the worker insights."

        return prompt

    async def _error_response(self, agent_id: str) -> AgentResponse:
        """Generate error response for missing agent"""
        return AgentResponse(
            agent_id=agent_id,
            output="",
            status="error",
            execution_time=0,
            error=f"Agent {agent_id} not found"
        )

    def _error_responses(self, tasks: List[Task]) -> List[AgentResponse]:
        """Generate error responses for all tasks"""
        return [
            AgentResponse(
                agent_id=task.agent_role.value,
                output="",
                status="error",
                execution_time=0,
                error="Orchestration initialization failed"
            )
            for task in tasks
        ]

    def _aggregate_results(self, responses: List[AgentResponse]) -> str:
        """
        Aggregate hierarchical results.

        Displays the coordinator's final synthesis prominently,
        with worker outputs for reference.
        """
        summary = "Hierarchical Processing Results:\n"
        summary += "=" * 50 + "\n\n"

        # Find coordinator response and worker responses
        coordinator_response = None
        worker_responses = []

        for response in responses:
            if response.agent_id == self.coordinator_id:
                coordinator_response = response
            else:
                worker_responses.append(response)

        # Display coordination phase
        summary += "COORDINATION PHASE:\n"
        if coordinator_response and coordinator_response.status == "success":
            summary += f"{coordinator_response.output}\n\n"

        # Display worker outputs
        summary += "WORKER OUTPUTS:\n"
        summary += "-" * 50 + "\n"
        for response in worker_responses:
            if response.status == "success":
                summary += f"{response.agent_id}:\n{response.output}\n\n"
            else:
                summary += f"{response.agent_id}: ERROR - {response.error}\n\n"

        # Display final synthesis
        summary += "FINAL SYNTHESIS:\n"
        summary += "-" * 50 + "\n"
        if len(responses) > 1:
            final_synthesis = responses[-1]
            if final_synthesis.status == "success":
                summary += final_synthesis.output
            else:
                summary += f"ERROR: {final_synthesis.error}"

        return summary

