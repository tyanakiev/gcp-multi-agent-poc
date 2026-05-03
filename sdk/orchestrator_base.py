"""
ADK orchestrator base for coordinating multiple agents

Provides orchestration primitives, retry logic, and metrics hooks.
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

import structlog
from sdk.base_agent_adk import ADKAgent
from sdk.message_types import AgentMessage, MessageKind, MessageEnvelope
from sdk.pubsub_client import PubSubClient
from core.config import (
    MAX_RETRIES,
    RETRY_BACKOFF_MULTIPLIER,
    INITIAL_RETRY_DELAY,
    ORCHESTRATOR_TIMEOUT,
)

logger = structlog.get_logger(__name__)


class ADKOrchestrator(ABC):
    """
    ADK orchestrator base for coordinating multiple agents.

    Provides:
    - Agent lifecycle management
    - Message routing via Pub/Sub
    - Retry logic with exponential backoff
    - Trace context propagation
    - Metrics collection
    """

    def __init__(
        self,
        orchestrator_id: str,
        agents: Dict[str, ADKAgent],
        pubsub_client: Optional[PubSubClient] = None,
        max_retries: int = MAX_RETRIES,
        retry_backoff: float = RETRY_BACKOFF_MULTIPLIER,
    ):
        """
        Initialize orchestrator.

        Args:
            orchestrator_id: Unique orchestrator identifier
            agents: Dictionary of agents keyed by ID
            pubsub_client: Pub/Sub client for messaging
            max_retries: Maximum retry attempts
            retry_backoff: Backoff multiplier for retries
        """
        self.orchestrator_id = orchestrator_id
        self.agents = agents
        self.pubsub_client = pubsub_client or PubSubClient()
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        # Tracking
        self.start_time = time.time()
        self.execution_count = 0
        self.total_duration = 0.0
        self.error_count = 0

        logger.info(
            "orchestrator_initialized",
            orchestrator_id=orchestrator_id,
            agent_count=len(agents),
        )

    async def initialize_agents(self) -> None:
        """Initialize all agents"""
        tasks = [agent.initialize() for agent in self.agents.values()]
        await asyncio.gather(*tasks)
        logger.info("all_agents_initialized", orchestrator_id=self.orchestrator_id)

    @abstractmethod
    async def execute(
        self,
        messages: List[AgentMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[AgentMessage]:
        """
        Execute orchestration - must be implemented by subclasses.

        Args:
            messages: List of messages to process
            context: Execution context

        Returns:
            List of response messages
        """
        pass

    async def route_message(
        self,
        message: AgentMessage,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentMessage:
        """
        Route a message to the appropriate agent with retry logic.

        Args:
            message: Message to route
            context: Execution context

        Returns:
            Response message
        """
        recipient_id = message.recipient
        agent = self.agents.get(recipient_id)

        if not agent:
            logger.error(
                "agent_not_found",
                recipient=recipient_id,
                trace_id=message.trace_id,
            )
            return AgentMessage(
                sender=self.orchestrator_id,
                recipient=message.sender,
                kind=MessageKind.ERROR,
                payload={"error": f"Agent {recipient_id} not found"},
                trace_id=message.trace_id,
                parent_id=message.id,
            )

        # Create envelope and process with retry
        envelope = MessageEnvelope(message=message)
        return_envelope = await self._execute_with_retry(
            agent,
            envelope,
            context,
        )

        return return_envelope.message

    async def _execute_with_retry(
        self,
        agent: ADKAgent,
        envelope: MessageEnvelope,
        context: Optional[Dict[str, Any]] = None,
        attempt: int = 0,
    ) -> MessageEnvelope:
        """
        Execute agent with exponential backoff retry.

        Args:
            agent: Agent to execute
            envelope: Message envelope
            context: Execution context
            attempt: Current attempt number

        Returns:
            Response envelope
        """
        try:
            return await agent.process_envelope(envelope, context)

        except Exception as e:
            attempt += 1

            if attempt >= self.max_retries:
                logger.error(
                    "max_retries_exceeded",
                    agent_id=agent.agent_id,
                    trace_id=envelope.message.trace_id,
                    error=str(e),
                )
                # Send to DLQ
                await self.pubsub_client.publish_to_dlq(
                    envelope,
                    f"Max retries ({self.max_retries}) exceeded: {str(e)}",
                )
                self.error_count += 1

                # Return error response
                return MessageEnvelope(
                    message=AgentMessage(
                        sender=agent.agent_id,
                        recipient=envelope.message.sender,
                        kind=MessageKind.ERROR,
                        payload={"error": f"Max retries exceeded: {str(e)}"},
                        trace_id=envelope.message.trace_id,
                        parent_id=envelope.message.id,
                    ),
                    delivery_count=attempt,
                    last_error=str(e),
                )

            # Calculate backoff
            backoff_delay = INITIAL_RETRY_DELAY * (self.retry_backoff ** (attempt - 1))

            logger.info(
                "retrying_agent_execution",
                agent_id=agent.agent_id,
                attempt=attempt,
                backoff_delay=backoff_delay,
                trace_id=envelope.message.trace_id,
            )

            # Wait and retry
            await asyncio.sleep(backoff_delay)
            return await self._execute_with_retry(agent, envelope, context, attempt)

    async def publish_message(
        self,
        envelope: MessageEnvelope,
    ) -> str:
        """
        Publish a message via Pub/Sub.

        Args:
            envelope: Message envelope to publish

        Returns:
            Message ID
        """
        recipient = envelope.message.recipient
        topic_name = f"{recipient}"
        return await self.pubsub_client.publish_message(envelope, topic_name)

    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics"""
        uptime = time.time() - self.start_time
        avg_duration = self.total_duration / self.execution_count if self.execution_count > 0 else 0

        return {
            "orchestrator_id": self.orchestrator_id,
            "uptime_seconds": uptime,
            "total_executions": self.execution_count,
            "total_errors": self.error_count,
            "avg_execution_time": avg_duration,
            "agent_count": len(self.agents),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def shutdown(self) -> None:
        """Shutdown orchestrator and all agents"""
        logger.info("orchestrator_shutting_down", orchestrator_id=self.orchestrator_id)

        # Shutdown agents
        tasks = [agent.shutdown() for agent in self.agents.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Shutdown Pub/Sub
        await self.pubsub_client.shutdown()

        logger.info("orchestrator_shutdown_complete", orchestrator_id=self.orchestrator_id)

