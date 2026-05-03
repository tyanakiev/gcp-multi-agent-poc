"""
Type definitions for multi-agent orchestration
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class AgentRole(str, Enum):
    """Defines different agent roles in the system"""
    RESEARCHER = "researcher"
    ANALYZER = "analyzer"
    WRITER = "writer"
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    CUSTOM = "custom"


class OrchestrationStrategy(str, Enum):
    """Defines orchestration strategies"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"


@dataclass
class AgentMessage:
    """Message passed between agents"""
    sender: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from an agent execution"""
    agent_id: str
    output: str
    status: str  # "success", "error", "timeout"
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class OrchestrationResult:
    """Result from orchestration execution"""
    strategy: OrchestrationStrategy
    total_execution_time: float
    agent_responses: List[AgentResponse]
    final_output: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Task definition for agents"""
    task_id: str
    description: str
    agent_role: AgentRole
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

