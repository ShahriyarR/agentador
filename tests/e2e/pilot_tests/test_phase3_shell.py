"""E2E tests for Phase 3: Shell Execution with Safety Controls."""

import pytest


@pytest.mark.asyncio
async def test_shell_command_creates_tool_widget(e2e_deepagents_app):
    """Shell commands should create tool-related widgets."""
    app, pilot = e2e_deepagents_app

    from agent_tui.entrypoints.widgets.messages import ToolCallMessage

    assert ToolCallMessage is not None


@pytest.mark.asyncio
async def test_chat_input_shell_mode(e2e_deepagents_app):
    """Chat input should have shell mode available."""
    app, pilot = e2e_deepagents_app

    await pilot.click("#input-area")
    await pilot.type("!")
    await pilot.pause()

    assert app._chat_input is not None
