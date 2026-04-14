"""DeepAgents integration for agent-tui.

Public API:
- DeepAgentsAdapter: Bridge between DeepAgents and the TUI
- EventTranslator: Translates DeepAgents events to domain events
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_tui.services.deep_agents.adapter import DeepAgentsAdapter
    from agent_tui.services.deep_agents.event_translator import EventTranslator

__all__ = [
    "DeepAgentsAdapter",
    "EventTranslator",
]
