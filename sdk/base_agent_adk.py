"""
ADK-native base agent for Google Cloud ADK integration

Provides lifecycle hooks, message envelope support, and health checks.
"""

import logging
import uuid
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime

try:
    from google.adk import Agent as GoogleADKAgent
    GOOGLE_ADK_AVAILABLE = True
except ImportError:
    GOOGLE_ADK_AVAILABLE = False
    GoogleADKAgent = None

import structlog
from sdk.message_types import AgentMessage, MessageKind, MessageEnvelope
from core.config import ENABLE_STRUCTURED_LOGGING, TRACE_ID_HEADER, SERVICE_NAME
from core.adk_tool_utils import normalize_tools_for_adk
from core.adk_runtime import run_agent_single_turn

# Configure logging
if ENABLE_STRUCTURED_LOGGING:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger(__name__)
standard_logger = logging.getLogger(__name__)


class ADKAgent(ABC):
    """
    ADK-native agent base class for Google Cloud ADK integration.

    Provides:
    - Lifecycle hooks (init, start, handle_message, stop)
    - Message envelope support
    - Structured logging with trace context
    - Health check helpers
    - Metrics collection
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        model: str,
        instruction: str,
        tools: Optional[List[Any]] = None,
        max_retries: int = 3,
        timeout: int = 60,
    ):
        """
        Initialize ADK agent.

        Args:
            agent_id: Unique agent identifier
            name: Display name for the agent
            model: LLM model name (e.g., "gemini-2.0-flash")
            instruction: System instruction for agent behavior
            tools: List of tools available to the agent
            max_retries: Maximum retry attempts
            timeout: Execution timeout in seconds
        """
        self.agent_id = agent_id
        self.name = name
        self.model = model
        self.instruction = instruction
        self.tools = tools or []
        self.max_retries = max_retries
        self.timeout = timeout
        self._adk_tools = normalize_tools_for_adk(self.tools)

        # Tracking
        self.instance_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.message_count = 0
        self.error_count = 0
        self.health_status = "initializing"

        # Initialize Google ADK agent if available
        self.use_google_adk = False
        self.google_adk_agent = None
        if GOOGLE_ADK_AVAILABLE:
            try:
                self.google_adk_agent = GoogleADKAgent(
                    name=name,
                    model=model,
                    instruction=instruction,
                    tools=self._adk_tools,
                )
                self.use_google_adk = True
                logger.info(
                    "adk_agent_initialized",
                    agent_id=agent_id,
                    backend="google_adk",
                )
            except Exception as e:
                logger.warning(
                    "adk_initialization_failed",
                    agent_id=agent_id,
                    error=str(e),
                )

    async def initialize(self) -> None:
        """Initialize the agent - override in subclasses"""
        self.health_status = "ready"
        logger.info("adk_agent_ready", agent_id=self.agent_id)

    async def invoke_llm(self, prompt: str, fallback: str) -> str:
        """Run one ADK turn via Runner, or return fallback when ADK is unavailable."""
        if self.use_google_adk and self.google_adk_agent:
            text = await run_agent_single_turn(
                self.google_adk_agent,
                prompt,
                app_name=f"gcp_multi_agent_poc_{self.agent_id}",
            )
            return text if text.strip() else fallback
        return fallback

    async def handle_message(
        self,
        message: AgentMessage,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentMessage:
        """
        Handle incoming message - must be implemented by subclasses.

        Args:
            message: Incoming agent message
            context: Execution context

        Returns:
            Response message
        """
        raise NotImplementedError("Subclasses must implement handle_message()")

    async def process_envelope(
        self,
        envelope: MessageEnvelope,
        context: Optional[Dict[str, Any]] = None,
    ) -> MessageEnvelope:
        """
        Process a message envelope with retry logic.

        Args:
            envelope: Message envelope from Pub/Sub
            context: Execution context

        Returns:
            Response envelope
        """
        message = envelope.message
        trace_id = message.trace_id

        # Add trace context to logger
        logger_context = {
            "trace_id": trace_id,
            "agent_id": self.agent_id,
            "message_id": message.id,
        }

        self.message_count += 1

        try:
            # Handle the message
            response = await self.handle_message(message, context)

            # Create response envelope
            response_envelope = MessageEnvelope(
                message=response,
                delivery_count=0,
            )

            logger.info(
                "message_processed",
                **logger_context,
                status="success",
            )

            return response_envelope

        except Exception as e:
            self.error_count += 1
            envelope.delivery_count += 1
            envelope.last_error = str(e)

            logger.error(
                "message_processing_failed",
                **logger_context,
                error=str(e),
                delivery_count=envelope.delivery_count,
            )

            # Return error response
            error_response = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                kind=MessageKind.ERROR,
                payload={"error": str(e)},
                trace_id=trace_id,
                parent_id=message.id,
            )

            return MessageEnvelope(
                message=error_response,
                delivery_count=envelope.delivery_count,
                last_error=str(e),
            )

    def get_health(self) -> Dict[str, Any]:
        """Get agent health status"""
        uptime = time.time() - self.start_time
        return {
            "status": self.health_status,
            "agent_id": self.agent_id,
            "instance_id": self.instance_id,
            "uptime_seconds": uptime,
            "messages_processed": self.message_count,
            "errors": self.error_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        uptime = time.time() - self.start_time
        error_rate = (self.error_count / self.message_count) if self.message_count > 0 else 0

        return {
            "agent_id": self.agent_id,
            "uptime_seconds": uptime,
            "total_messages": self.message_count,
            "total_errors": self.error_count,
            "error_rate": error_rate,
            "avg_message_time": uptime / self.message_count if self.message_count > 0 else 0,
        }

    async def shutdown(self) -> None:
        """Shutdown the agent - override in subclasses for cleanup"""
        self.health_status = "shutting_down"
        logger.info("adk_agent_shutdown", agent_id=self.agent_id)

