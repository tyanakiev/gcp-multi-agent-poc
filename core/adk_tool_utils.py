"""Helpers for adapting PoC tool types to Google ADK tool unions."""

from __future__ import annotations

from typing import Any, Callable, List, Sequence

from core.adk_tools import ToolDefinition


def normalize_tools_for_adk(tools: Sequence[Any]) -> List[Callable[..., Any]]:
    """Convert ToolDefinition entries (and bare callables) into ADK tool callables."""
    normalized: List[Callable[..., Any]] = []
    for item in tools:
        if isinstance(item, ToolDefinition):
            normalized.append(item.func)
        elif callable(item):
            normalized.append(item)
        else:
            raise TypeError(
                f"Invalid tool entry {type(item)!r}: expected ToolDefinition or callable"
            )
    return normalized
