"""
Research Agent - Specialized for gathering and researching information

Uses Google Cloud ADK for production-ready agent implementation.
"""

from typing import Any, Dict, Optional
import structlog

from sdk.base_agent_adk import ADKAgent
from sdk.message_types import AgentMessage, MessageKind

logger = structlog.get_logger(__name__)


class ResearcherAgent(ADKAgent):
    """
    Agent specialized in research and information gathering using Google Cloud ADK.

    Responsibilities:
    - Gather relevant information
    - Research topics thoroughly
    - Provide comprehensive background
    """

    def __init__(self, agent_id: str = "researcher", model: str = "gemini-2.5-flash"):
        """Initialize the researcher agent with ADK pattern"""
        instruction = """You are an expert research agent. Your role is to:
1. Gather comprehensive information on topics
2. Research thoroughly and provide accurate details
3. Summarize findings clearly and concisely
4. Highlight key facts and important context
5. Provide sources and references when possible

Be thorough, accurate, and focus on delivering high-quality research."""

        super().__init__(
            agent_id=agent_id,
            name="Researcher",
            model=model,
            instruction=instruction,
            tools=[],
        )

    async def handle_message(
        self,
        message: AgentMessage,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentMessage:
        """
        Handle incoming research request.

        Args:
            message: Incoming message with research task
            context: Execution context

        Returns:
            Response message with research results
        """
        try:
            # Extract the task from the payload
            task = message.payload.get("task", "")
            topic = message.payload.get("topic", "")

            if not task and not topic:
                return AgentMessage(
                    sender=self.agent_id,
                    recipient=message.sender,
                    kind=MessageKind.RESPONSE,
                    payload={"error": "No task or topic provided"},
                    trace_id=message.trace_id,
                    parent_id=message.id,
                )

            research_query = task or topic

            result = await self.invoke_llm(
                research_query,
                fallback=(
                    f"Research findings on '{research_query}': "
                    "Comprehensive analysis available (simulated)."
                ),
            )

            logger.info(
                "research_completed",
                agent_id=self.agent_id,
                trace_id=message.trace_id,
                topic=topic,
            )

            return AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                kind=MessageKind.RESPONSE,
                payload={"result": result, "topic": topic},
                trace_id=message.trace_id,
                parent_id=message.id,
            )

        except Exception as e:
            logger.error(
                "research_failed",
                agent_id=self.agent_id,
                trace_id=message.trace_id,
                error=str(e),
            )
            raise

    def get_description(self) -> str:
        """Get agent description"""
        return """Researcher Agent: Specialized in gathering and analyzing information.
        Gathers comprehensive research, identifies key facts, and provides detailed
        background information for topics."""

