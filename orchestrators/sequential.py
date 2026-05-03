"""
Sequential Orchestrator - Use Case 1

Executes agents one after another, with each agent receiving the output
from the previous one. Best for data pipelines and step-by-step processes.

Flow: Agent1 -> Agent2 -> Agent3 -> ... -> Final Output

Uses Google Cloud ADK for production-ready orchestration.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
import structlog

from sdk.orchestrator_base import ADKOrchestrator
from sdk.base_agent_adk import ADKAgent
from sdk.message_types import AgentMessage, MessageKind, MessageEnvelope
from sdk.pubsub_client import PubSubClient

logger = structlog.get_logger(__name__)


class SequentialOrchestrator(ADKOrchestrator):
    """
    Sequential orchestration strategy using Google Cloud ADK.

    Agents execute in order, with each agent's output becoming the next agent's input.
    Uses Pub/Sub for message routing between agents.
    """

    def __init__(
        self,
        orchestrator_id: str,
        agents: Dict[str, ADKAgent],
        pubsub_client: Optional[PubSubClient] = None,
    ):
        """Initialize sequential orchestrator"""
        super().__init__(
            orchestrator_id=orchestrator_id,
            agents=agents,
            pubsub_client=pubsub_client,
        )
        # Get ordered list of agent IDs for sequential execution
        self.agent_order = list(agents.keys())

        logger.info(
            "sequential_orchestrator_initialized",
            orchestrator_id=orchestrator_id,
            agent_order=self.agent_order,
        )

    async def execute(
        self,
        messages: List[AgentMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[AgentMessage]:
        """
        Execute messages sequentially through agents.

        Each message is routed to the first agent, then results are
        passed to subsequent agents in order.

        Args:
            messages: Initial messages to process
            context: Execution context

        Returns:
            Final messages after sequential processing
        """
        start_time = time.time()

        if not messages:
            logger.warning("no_messages_to_execute", orchestrator_id=self.orchestrator_id)
            return []

        # Start with initial messages routed to first agent
        if not self.agent_order:
            logger.error("no_agents_configured", orchestrator_id=self.orchestrator_id)
            return messages

        current_messages = messages
        logger.info(
            "starting_sequential_execution",
            orchestrator_id=self.orchestrator_id,
            initial_message_count=len(messages),
            agent_count=len(self.agent_order),
        )

        try:
            # Process through each agent in sequence
            for agent_id in self.agent_order:
                next_messages = []

                for message in current_messages:
                    # Route to current agent
                    message.recipient = agent_id
                    response = await self.route_message(message, context)
                    next_messages.append(response)

                current_messages = next_messages

                logger.info(
                    "sequential_stage_completed",
                    orchestrator_id=self.orchestrator_id,
                    agent_id=agent_id,
                    message_count=len(current_messages),
                )

            execution_time = time.time() - start_time
            self.total_duration += execution_time
            self.execution_count += 1

            logger.info(
                "sequential_execution_completed",
                orchestrator_id=self.orchestrator_id,
                execution_time=execution_time,
                final_message_count=len(current_messages),
            )

            return current_messages

        except Exception as e:
            self.error_count += 1
            logger.error(
                "sequential_execution_failed",
                orchestrator_id=self.orchestrator_id,
                error=str(e),
            )
            raise

