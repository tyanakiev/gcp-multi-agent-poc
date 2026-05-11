"""
Writer Agent - Specialized for creating written content

Uses Google Cloud ADK for production-ready agent implementation.
"""

from typing import Any, Dict, Optional
import structlog

from sdk.base_agent_adk import ADKAgent
from sdk.message_types import AgentMessage, MessageKind

logger = structlog.get_logger(__name__)


class WriterAgent(ADKAgent):
    """
    Agent specialized in writing and content creation using Google Cloud ADK.

    Responsibilities:
    - Create well-structured written content
    - Synthesize information coherently
    - Present ideas clearly and engagingly
    - Format content appropriately
    """

    def __init__(self, agent_id: str = "writer", model: str = "gemini-2.5-flash"):
        """Initialize the writer agent with ADK pattern"""
        instruction = """You are an expert writer and content creator. Your role is to:
1. Create clear, engaging, and well-structured content
2. Synthesize multiple sources into coherent narratives
3. Use appropriate tone and style for the audience
4. Format content for maximum clarity and readability
5. Ensure consistency and flow throughout the writing

Be creative, clear, and focused on delivering high-quality written content."""

        super().__init__(
            agent_id=agent_id,
            name="Writer",
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
        Handle incoming content creation request.

        Args:
            message: Incoming message with writing task
            context: Execution context

        Returns:
            Response message with written content
        """
        try:
            # Extract the task from the payload
            task = message.payload.get("task", "")
            content_type = message.payload.get("type", "general")
            source_material = message.payload.get("source", "")

            if not task:
                return AgentMessage(
                    sender=self.agent_id,
                    recipient=message.sender,
                    kind=MessageKind.RESPONSE,
                    payload={"error": "No task provided"},
                    trace_id=message.trace_id,
                    parent_id=message.id,
                )

            # Build writing prompt
            write_prompt = task
            if source_material:
                write_prompt = f"Using this source material: {source_material}\n\nTask: {task}"

            result = await self.invoke_llm(
                write_prompt,
                fallback=f"Written content ({content_type}):\n{write_prompt[:150]}...",
            )

            logger.info(
                "content_created",
                agent_id=self.agent_id,
                trace_id=message.trace_id,
                content_type=content_type,
            )

            return AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                kind=MessageKind.RESPONSE,
                payload={"result": result, "type": content_type},
                trace_id=message.trace_id,
                parent_id=message.id,
            )

        except Exception as e:
            logger.error(
                "content_creation_failed",
                agent_id=self.agent_id,
                trace_id=message.trace_id,
                error=str(e),
            )
            raise

    def get_description(self) -> str:
        """Get agent description"""
        return """Writer Agent: Specialized in creating written content.
        Synthesizes information into clear, engaging narratives and formats
        content for maximum readability and impact."""

