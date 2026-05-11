"""
Base Agent class for multi-agent orchestration using Google Cloud ADK
"""

import time
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

try:
    from google.adk import Agent as ADKAgent
    USE_ADK = True
except ImportError:
    USE_ADK = False
    ADKAgent = None

try:
    from google import generativeai as genai
except ImportError:
    genai = None

from core.types import AgentRole, AgentResponse
from core.config import GOOGLE_PROJECT_ID, DEFAULT_MODEL, DEFAULT_TEMPERATURE, AGENT_TIMEOUT
from core.adk_tool_utils import normalize_tools_for_adk
from core.adk_runtime import run_agent_single_turn

logger = logging.getLogger(__name__)

# Configure Generative AI if API key is available
if genai and os.getenv("GOOGLE_API_KEY"):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class Agent(ABC):
    """
    Base class for all agents using Google Cloud ADK.

    Each agent has:
    - A unique ID (name)
    - A role/specialization
    - System instructions defining behavior
    - Tools for extended capabilities
    - Ability to execute tasks using LLMs
    """

    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        instruction: str,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        tools: Optional[List[Any]] = None
    ):
        """
        Initialize an agent with Google Cloud ADK pattern.

        Args:
            agent_id: Unique identifier for the agent
            role: Agent's role/specialization
            instruction: System instructions for the agent behavior
            model: LLM model to use (default: gemini-2.0-flash)
            temperature: Temperature for generation
            tools: List of tools available to the agent
        """
        self.agent_id = agent_id
        self.role = role
        self.instruction = instruction
        self.model = model
        self.temperature = temperature
        self.tools = tools or []
        self.execution_history = []

        # Initialize ADK Agent if available
        if USE_ADK:
            try:
                adk_tools = normalize_tools_for_adk(self.tools)
                self.adk_agent = ADKAgent(
                    name=agent_id,
                    model=model,
                    instruction=instruction,
                    tools=adk_tools,
                )
                self.use_adk = True
                logger.info(f"Agent {agent_id} initialized with Google Cloud ADK")
            except Exception as e:
                logger.warning(f"Failed to initialize ADK: {e}, falling back to Generative AI")
                self.use_adk = False
                self.adk_agent = None
        else:
            self.use_adk = False
            self.adk_agent = None

        # Fallback to Generative AI
        if not self.use_adk and genai:
            try:
                self.genai_model = genai.GenerativeModel(
                    model_name=model,
                    generation_config=genai.types.GenerationConfig(temperature=temperature)
                )
                logger.info(f"Agent {agent_id} initialized with Generative AI")
            except Exception as e:
                logger.error(f"Failed to initialize Generative AI: {e}")
                self.genai_model = None

    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: int = AGENT_TIMEOUT
    ) -> AgentResponse:
        """
        Execute a task with the agent using Google Cloud ADK.

        Args:
            task: The task description
            context: Additional context/input for the task
            timeout: Execution timeout in seconds

        Returns:
            AgentResponse with output and metadata
        """
        start_time = time.time()

        try:
            # Build the full prompt with context
            full_prompt = self._build_prompt(task, context)

            # Execute via ADK Agent if available
            if self.use_adk and self.adk_agent:
                try:
                    output = await run_agent_single_turn(
                        self.adk_agent,
                        full_prompt,
                        app_name=f"gcp_multi_agent_poc_{self.agent_id}",
                    )
                    if not output:
                        raise RuntimeError("ADK returned empty response")
                except Exception as e:
                    logger.debug(f"ADK execution failed: {e}, falling back to Generative AI")
                    output = await self._execute_with_genai(full_prompt)
            else:
                output = await self._execute_with_genai(full_prompt)

            execution_time = time.time() - start_time

            # Store in history
            self.execution_history.append({
                "task": task,
                "output": output,
                "timestamp": start_time
            })

            logger.info(f"Agent {self.agent_id} completed task in {execution_time:.2f}s")

            return AgentResponse(
                agent_id=self.agent_id,
                output=output,
                status="success",
                execution_time=execution_time,
                metadata={
                    "role": self.role.value,
                    "model": self.model,
                    "backend": "adk" if self.use_adk else "generative_ai",
                    "tools_count": len(self.tools)
                }
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Agent {self.agent_id} failed: {str(e)}")

            return AgentResponse(
                agent_id=self.agent_id,
                output="",
                status="error",
                execution_time=execution_time,
                error=str(e),
                metadata={"role": self.role.value}
            )

    async def _execute_with_genai(self, prompt: str) -> str:
        """
        Execute task using Google Generative AI as fallback.

        Args:
            prompt: The prompt to send to the model

        Returns:
            Model output text
        """
        if not self.genai_model:
            raise RuntimeError("Generative AI model not initialized")

        response = self.genai_model.generate_content(prompt)
        return response.text

    def _build_prompt(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build the final prompt with system context.

        Args:
            task: The task description
            context: Additional context

        Returns:
            Full prompt string
        """
        prompt = f"{self.instruction}\n\n"

        if context:
            prompt += "Context:\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"

        prompt += f"Task: {task}"

        return prompt

    def get_history(self) -> list:
        """Get execution history for this agent"""
        return self.execution_history

    def clear_history(self):
        """Clear execution history"""
        self.execution_history = []

    @abstractmethod
    def get_description(self) -> str:
        """Get a description of what this agent does"""
        pass

