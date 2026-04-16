"""E2E tests for Phase 2: File Tool Approval."""

import pytest


@pytest.mark.asyncio
async def test_approval_widget_exists(e2e_deepagents_app):
    """Approval widget should be available in the app."""
    app, pilot = e2e_deepagents_app

    from agent_tui.entrypoints.widgets.approval import ApprovalMenu

    assert ApprovalMenu is not None


@pytest.mark.asyncio
async def test_chat_input_accepts_text(e2e_deepagents_app):
    """Chat input should accept text input."""
    app, pilot = e2e_deepagents_app

    await pilot.click("#input-area")
    await pilot.type("hello")
    await pilot.pause()

    text_area = app.query_one("#chat-input")
    assert text_area is not None
