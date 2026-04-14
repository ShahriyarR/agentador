# agent-tui

Standalone TUI scaffold for building AI coding agent CLIs.

Extracted from the deepagents CLI — full UI with all agent interactions stubbed behind an `AgentProtocol`.

## Quick Start

```bash
uv run agent-tui
```

## Architecture

The TUI communicates with any agent backend through `AgentProtocol` — a Python protocol class that emits typed `AgentEvent` objects. A `StubAgent` is included for development and testing.

See `agent_tui/protocol.py` for the contract.


## Implementation Phases

Phase 1 Summary
Completed
Branch: phase/1-foundation (commits b045582 → 7e3e127)

Files Created

services/deep_agents/__init__.py
services/deep_agents/adapter.py
services/deep_agents/event_translator.py
tests/test_deep_agents_adapter.py
tests/test_event_translator.py
docs/superpowers/specs/2026-04-14-deepagents-integration-architecture.md
docs/superpowers/plans/2026-04-14-deepagents-integration.md

Files Modified

domain/protocol.py	+5 EventType values, +4 AgentEvent fields
services/adapter.py	+5 new event handlers
entrypoints/main.py	--agent flag (stub/deepagents)
entrypoints/app.py	+5 stub methods for new events
configurator/settings.py	+deepagents_model property
pyproject.toml	+deepagents>=0.5.2, langchain-openai>=0.3.0

Verification
- uv run agent-tui --agent=stub ✓
- uv run agent-tui --agent=deepagents ✓ (TUI launches)
- 44 tests pass

Key Fixes Applied
1. __init__.py lazy loading — was blocking runtime imports
2. DeepAgentsAdapter.from_settings() — was missing class method
3. create_deep_agent() — was incorrectly using deepagents.Agent