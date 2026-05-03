"""
Message types for inter-agent communication using Google Cloud ADK

Defines the message envelope and types for standardized agent communication.
"""

from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import uuid


class MessageKind(str, Enum):
    """Message kinds for inter-agent communication"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    CONTROL = "control"


@dataclass
class AgentMessage:
    """Standardized message for agent communication"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = field(default="")
    recipient: str = field(default="")
    kind: MessageKind = field(default=MessageKind.REQUEST)
    payload: Dict[str, Any] = field(default_factory=dict)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    parent_id: Optional[str] = field(default=None)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        msg_dict = asdict(self)
        msg_dict['kind'] = self.kind.value
        msg_dict['timestamp'] = self.timestamp.isoformat()
        return msg_dict

    def to_json(self) -> str:
        """Convert message to JSON"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary"""
        data_copy = data.copy()
        # Convert ISO timestamp back to datetime
        if isinstance(data_copy.get('timestamp'), str):
            data_copy['timestamp'] = datetime.fromisoformat(data_copy['timestamp'])
        # Convert kind string to enum
        if isinstance(data_copy.get('kind'), str):
            data_copy['kind'] = MessageKind(data_copy['kind'])
        return cls(**data_copy)

    @classmethod
    def from_json(cls, json_str: str) -> "AgentMessage":
        """Create message from JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class MessageEnvelope:
    """Envelope for Pub/Sub message transport"""
    message: AgentMessage
    delivery_count: int = 0
    last_error: Optional[str] = None
    expiry_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert envelope to dictionary"""
        return {
            "message": self.message.to_dict(),
            "delivery_count": self.delivery_count,
            "last_error": self.last_error,
            "expiry_time": self.expiry_time.isoformat() if self.expiry_time else None,
        }

    def to_json(self) -> str:
        """Convert envelope to JSON"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageEnvelope":
        """Create envelope from dictionary"""
        msg_data = data.get("message", {})
        message = AgentMessage.from_dict(msg_data)

        expiry = data.get("expiry_time")
        if isinstance(expiry, str):
            expiry = datetime.fromisoformat(expiry)

        return cls(
            message=message,
            delivery_count=data.get("delivery_count", 0),
            last_error=data.get("last_error"),
            expiry_time=expiry,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "MessageEnvelope":
        """Create envelope from JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)

