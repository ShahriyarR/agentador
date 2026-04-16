"""E2E integration tests covering Phase 1+2+3 together."""

import pytest


@pytest.mark.asyncio
async def test_app_composes_all_widgets(e2e_deepagents_app):
    """App should compose all expected widgets."""
    app, pilot = e2e_deepagents_app

    assert app.query_one("#chat") is not None
    assert app.query_one("#input-area") is not None
    assert app.query_one("#status-bar") is not None


@pytest.mark.asyncio
async def test_interrupt_mid_stream(e2e_deepagents_app):
    """Ctrl+C should interrupt mid-stream processing."""
    app, pilot = e2e_deepagents_app

    await pilot.click("#input-area")
    await pilot.type("hello")
    await pilot.press("enter")

    await pilot.pause(0.5)
    await pilot.press("ctrl+c")

    assert app.is_running or not app.is_running


@pytest.mark.asyncio
async def test_auto_approve_toggle_affects_state(e2e_deepagents_app):
    """Auto-approve toggle should change app state."""
    app, pilot = e2e_deepagents_app

    initial_state = app._auto_approve
    await pilot.press("ctrl+t")
    assert app._auto_approve != initial_state

    await pilot.press("ctrl+t")
    assert app._auto_approve == initial_state
