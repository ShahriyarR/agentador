"""E2E tests for Phase 1: Agent Integration."""

import pytest


@pytest.mark.asyncio
async def test_app_starts_without_crash(e2e_deepagents_app):
    """App should start without crashing."""
    app, pilot = e2e_deepagents_app
    assert app is not None
    assert pilot is not None


@pytest.mark.asyncio
async def test_auto_approve_toggle(e2e_deepagents_app):
    """Ctrl+T should toggle auto-approve mode."""
    app, pilot = e2e_deepagents_app

    assert app._auto_approve is False

    await pilot.press("ctrl+t")

    assert app._auto_approve is True

    await pilot.press("ctrl+t")
    assert app._auto_approve is False


@pytest.mark.asyncio
async def test_interrupt_with_escape(e2e_deepagents_app):
    """Escape should interrupt current operation."""
    app, pilot = e2e_deepagents_app

    await pilot.click("#input-area")
    await pilot.type("hello")
    await pilot.press("enter")

    await pilot.pause()

    await pilot.press("escape")

    await pilot.pause()


@pytest.mark.asyncio
async def test_session_state_is_initialized(e2e_deepagents_app):
    """App should have session state initialized."""
    app, pilot = e2e_deepagents_app

    await pilot.pause(0.5)

    assert app._session_state is not None
    assert app._session_state.thread_id is not None
