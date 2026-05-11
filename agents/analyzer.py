"""
Analyzer Agent - Specialized for analyzing and interpreting information

Uses Google Cloud ADK for production-ready agent implementation.
"""

from typing import Any, Dict, Optional
import structlog

from sdk.base_agent_adk import ADKAgent
from sdk.message_types import AgentMessage, MessageKind

logger = structlog.get_logger(__name__)


class AnalyzerAgent(ADKAgent):
    """
    Agent specialized in analysis and interpretation using Google Cloud ADK.

    Responsibilities:
    - Analyze complex information
    - Identify patterns and trends
    - Provide insights and interpretations
    - Break down complex concepts
    """

    def __init__(self, agent_id: str = "analyzer", model: str = "gemini-2.5-flash"):
        """Initialize the analyzer agent with ADK pattern"""
        instruction = """You are an expert analysis agent. Your role is to:
1. Analyze information deeply and critically
2. Identify patterns, trends, and relationships
3. Provide clear insights and interpretations
4. Break down complex concepts into understandable components
5. Offer data-driven conclusions

Be analytical, insightful, and provide clear reasoning for your conclusions."""

        super().__init__(
            agent_id=agent_id,
            name="Analyzer",
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
        Handle incoming analysis request.

        Args:
            message: Incoming message with analysis task
            context: Execution context

        Returns:
            Response message with analysis results
        """
        try:
            # Extract the task from the payload
            task = message.payload.get("task", "")
            analysis_type = message.payload.get("type", "general")

            if not task:
                return AgentMessage(
                    sender=self.agent_id,
                    recipient=message.sender,
                    kind=MessageKind.RESPONSE,
                    payload={"error": "No task provided"},
                    trace_id=message.trace_id,
                    parent_id=message.id,
                )

            result = await self.invoke_llm(
                task,
                fallback=f"Analysis ({analysis_type}): {task[:100]}...",
            )

            logger.info(
                "analysis_completed",
                agent_id=self.agent_id,
                trace_id=message.trace_id,
                analysis_type=analysis_type,
            )

            return AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                kind=MessageKind.RESPONSE,
                payload={"result": result, "type": analysis_type},
                trace_id=message.trace_id,
                parent_id=message.id,
            )

        except Exception as e:
            logger.error(
                "analysis_failed",
                agent_id=self.agent_id,
                trace_id=message.trace_id,
                error=str(e),
            )
            raise

    def get_description(self) -> str:
        """Get agent description"""
        return """Analyzer Agent: Specialized in analyzing and interpreting information.
        Identifies patterns, provides insights, and offers data-driven analysis
        and conclusions."""

