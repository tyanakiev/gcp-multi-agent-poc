"""Run Google ADK LlmAgent instances using Runner + session (ADK 1.x pattern)."""

from __future__ import annotations

import uuid
from typing import Optional

from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types


def _content_parts_text(content: Optional[types.Content]) -> str:
    if not content or not content.parts:
        return ""
    chunks: list[str] = []
    for part in content.parts:
        if part.text:
            chunks.append(part.text)
    return "\n".join(chunks).strip()


async def run_agent_single_turn(
    root_agent: Agent,
    user_text: str,
    *,
    app_name: str,
    user_id: str = "local_user",
    session_id: Optional[str] = None,
) -> str:
    """
    Execute one user turn against an ADK agent using InMemorySessionService.

    Each call uses a fresh session_id unless one is provided (isolated turn by default).
    """
    sid = session_id or str(uuid.uuid4())
    session_service = InMemorySessionService()
    runner = Runner(
        app_name=app_name,
        agent=root_agent,
        session_service=session_service,
        auto_create_session=True,
    )
    message = types.Content(
        role="user",
        parts=[types.Part(text=user_text)],
    )
    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=sid,
        new_message=message,
    ):
        if event.is_final_response() and event.content:
            text = _content_parts_text(event.content)
            if text:
                final_text = text
    return final_text
