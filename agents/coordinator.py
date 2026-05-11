"""
Coordinator Agent - Specialized for coordinating and synthesizing

Uses Google Cloud ADK for production-ready agent implementation.
"""

from typing import Any, Dict, Optional
import structlog

from sdk.base_agent_adk import ADKAgent
from sdk.message_types import AgentMessage, MessageKind

logger = structlog.get_logger(__name__)


class CoordinatorAgent(ADKAgent):
    """
    Agent specialized in coordination and synthesis using Google Cloud ADK.

    Responsibilities:
    - Coordinate activities between agents
    - Synthesize diverse inputs
    - Make strategic decisions
    - Provide overall guidance and direction
    """

    def __init__(self, agent_id: str = "coordinator", model: str = "gemini-2.5-flash"):
        """Initialize the coordinator agent with ADK pattern"""
        instruction = """You are an expert coordinator and synthesizer. Your role is to:
1. Coordinate activities and delegate tasks strategically
2. Synthesize diverse inputs into coherent outcomes
3. Make strategic decisions about task allocation
4. Provide overall guidance and direction
5. Ensure alignment across different components

Be strategic, collaborative, and focused on delivering integrated solutions."""

        super().__init__(
            agent_id=agent_id,
            name="Coordinator",
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
        Handle incoming coordination request.

        Args:
            message: Incoming message with coordination task
            context: Execution context

        Returns:
            Response message with coordination results
        """
        try:
            # Extract the task from the payload
            task = message.payload.get("task", "")
            agents_involved = message.payload.get("agents", [])

            if not task:
                return AgentMessage(
                    sender=self.agent_id,
                    recipient=message.sender,
                    kind=MessageKind.RESPONSE,
                    payload={"error": "No task provided"},
                    trace_id=message.trace_id,
                    parent_id=message.id,
                )

            coordination_prompt = task
            if agents_involved:
                coordination_prompt = f"Coordinate the following agents: {', '.join(agents_involved)}\n\nTask: {task}"

            result = await self.invoke_llm(
                coordination_prompt,
                fallback=f"Coordination plan:\n{coordination_prompt[:150]}...",
            )

            logger.info(
                "coordination_completed",
                agent_id=self.agent_id,
                trace_id=message.trace_id,
                agents_involved=len(agents_involved),
            )

            return AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                kind=MessageKind.RESPONSE,
                payload={"result": result, "agents": agents_involved},
                trace_id=message.trace_id,
                parent_id=message.id,
            )

        except Exception as e:
            logger.error(
                "coordination_failed",
                agent_id=self.agent_id,
                trace_id=message.trace_id,
                error=str(e),
            )
            raise

    def get_description(self) -> str:
        """Get agent description"""
        return """Coordinator Agent: Specialized in coordination and synthesis.
        Orchestrates activities between agents, makes strategic decisions,
        and synthesizes diverse inputs into coherent solutions."""

