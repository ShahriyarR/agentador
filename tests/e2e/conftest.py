"""Shared fixtures for E2E tests."""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from textual.pilot import TextualPilot

    from agent_tui.entrypoints.app import AgentTuiApp


class CapturedEvents:
    """Records AgentEvents during test execution."""

    def __init__(self) -> None:
        self._events: list = []
        self._lock = asyncio.Lock()

    async def capture(self, event) -> None:
        async with self._lock:
            self._events.append(event)

    def get_events(self):
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()


@pytest.fixture
def captured_events():
    """Returns a CapturedEvents instance."""
    return CapturedEvents()


class PilotHelper:
    """Helper for TextualPilot that adds type() method for sending text."""

    def __init__(self, pilot):
        self._pilot = pilot

    async def type(self, text: str) -> None:
        """Send text character by character to the focused widget."""
        for char in text:
            await self._pilot.press(char)
            await self._pilot.pause(0.01)

    def __getattr__(self, name):
        return getattr(self._pilot, name)


async def _create_app(agent, *, auto_approve: bool = False):
    """Helper to create and mount app for testing."""
    from agent_tui.entrypoints.app import AgentTuiApp

    app = AgentTuiApp(
        agent=agent,
        auto_approve=auto_approve,
    )
    async with app.run_test() as pilot:
        helper = PilotHelper(pilot)
        yield app, helper


def _get_e2e_agent():
    """Determine which agent to use based on environment."""
    agent_type = os.environ.get("AGENT_TUI_E2E_AGENT", "deepagents")
    if agent_type == "stub":
        from agent_tui.services.stub_agent import StubAgent

        return StubAgent()
    else:
        from agent_tui.services.deep_agents import DeepAgentsAdapter

        return DeepAgentsAdapter.from_settings()


@pytest.fixture
async def e2e_app_factory():
    """Creates AgentTuiApp with configured agent (default: DeepAgents).

    Use AGENT_TUI_E2E_AGENT=stub env var to use StubAgent instead.
    """
    agent = _get_e2e_agent()
    async for result in _create_app(agent):
        yield result


@pytest.fixture
async def e2e_stub_app():
    """Creates AgentTuiApp with StubAgent for debugging."""
    from agent_tui.services.stub_agent import StubAgent

    agent = StubAgent()
    async for result in _create_app(agent):
        yield result


@pytest.fixture
async def e2e_deepagents_app():
    """Creates AgentTuiApp with DeepAgentsAdapter (default for E2E)."""
    from agent_tui.services.deep_agents import DeepAgentsAdapter

    try:
        adapter = DeepAgentsAdapter.from_settings()
    except Exception:
        pytest.skip("DeepAgents not available or misconfigured")

    async for result in _create_app(adapter):
        yield result
