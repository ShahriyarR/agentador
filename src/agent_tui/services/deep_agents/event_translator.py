"""EventTranslator: DeepAgents/LangGraph checkpoint events → AgentEvent stream."""

from __future__ import annotations

from typing import Any, Iterator

from agent_tui.domain.protocol import AgentEvent, EventType


class EventTranslator:
    """Translates DeepAgents/LangGraph checkpoint events to AgentEvent stream.

    This is a pure translation layer with no side effects and no DeepAgents
    dependencies. It works with generic event dict structures that can be
    adapted when DeepAgents is actually integrated.

    Supported events (Phase 1):
        - content_block_delta → MESSAGE_CHUNK
        - on_chain_end → MESSAGE_END
        - on_tool_start → TOOL_CALL
        - on_tool_end → TOOL_RESULT

    Not yet handled (future phases):
        - PLAN_STEP (Phase 5)
        - SUBAGENT_START/SUBAGENT_END (Phase 5)
        - CONTEXT_SUMMARIZED (Phase 6)
        - INTERRUPT (Phase 8)
    """

    def translate(self, event: dict[str, Any]) -> Iterator[AgentEvent]:
        """Translate a raw DeepAgents event dict to AgentEvent stream.

        Args:
            event: Raw event dict with structure:
                {
                    "event_type": str,  # e.g., "on_chain_stream", "on_tool_start"
                    "data": dict,        # Event-specific payload
                    "run_id": str,       # Optional run identifier
                }

        Yields:
            AgentEvent objects based on the input event type.
        """
        event_type = event.get("event_type", "")
        data = event.get("data", {})
        data_present = "data" in event

        if event_type == "on_chain_stream":
            yield from self._handle_chain_stream(data, event)
        elif event_type == "on_tool_start":
            yield from self._handle_tool_start(data, event)
        elif event_type == "on_tool_end":
            yield from self._handle_tool_end(data, event)
        elif event_type == "on_chain_end":
            yield from self._handle_chain_end(data, event, data_present)
        elif event_type == "on_tool_error":
            yield from self._handle_tool_error(data, event)

    def _handle_chain_stream(self, data: dict[str, Any], event: dict[str, Any]) -> Iterator[AgentEvent]:
        """Handle on_chain_stream events for message chunks."""
        name = data.get("name", "")
        if name == "content_block_delta":
            content = data.get("data", {}).get("content", "")
            if content:
                yield AgentEvent(
                    type=EventType.MESSAGE_CHUNK,
                    text=content,
                )

    def _handle_tool_start(self, data: dict[str, Any], event: dict[str, Any]) -> Iterator[AgentEvent]:
        """Handle on_tool_start events for tool calls."""
        tool_name = data.get("name", "")
        tool_input = data.get("input", {})
        run_id = event.get("run_id", "")

        if tool_name:
            yield AgentEvent(
                type=EventType.TOOL_CALL,
                tool_name=tool_name,
                tool_args=tool_input,
                tool_id=run_id,
            )

    def _handle_tool_end(self, data: dict[str, Any], event: dict[str, Any]) -> Iterator[AgentEvent]:
        """Handle on_tool_end events for tool results."""
        if "output" not in data:
            return
        tool_output = data.get("output")
        if tool_output is None:
            return
        yield AgentEvent(
            type=EventType.TOOL_RESULT,
            tool_output=str(tool_output),
        )

    def _handle_chain_end(
        self, data: dict[str, Any], event: dict[str, Any], data_present: bool
    ) -> Iterator[AgentEvent]:
        """Handle on_chain_end events for message end."""
        if not data_present:
            return
        yield AgentEvent(type=EventType.MESSAGE_END)

    def _handle_tool_error(self, data: dict[str, Any], event: dict[str, Any]) -> Iterator[AgentEvent]:
        """Handle on_tool_error events for errors."""
        error_text = data.get("error", str(data))
        yield AgentEvent(
            type=EventType.ERROR,
            text=f"Tool error: {error_text}",
        )
