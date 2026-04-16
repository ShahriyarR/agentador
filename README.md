# agent-tui

Standalone TUI scaffold for building AI coding agent CLIs.

Extracted from the deepagents CLI — full UI with all agent interactions stubbed behind an `AgentProtocol`.

## Installation

```bash
git clone https://github.com/your-repo/agent-tui.git
cd agent-tui
uv sync
```

## Quick Start

### Stub Agent (no API key required)

```bash
uv run agent-tui
# or explicitly:
uv run agent-tui --agent=stub
```

### DeepAgents (requires API key)

```bash
# Set your API key
export OPENAI_API_KEY=sk-...

# Run with DeepAgents backend
uv run agent-tui --agent=deepagents
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes* | — | OpenAI API key for DeepAgents |
| `AGENT_TUI_OPENAI_API_KEY` | Yes* | — | Alternative to `OPENAI_API_KEY` (scoped to agent-tui) |
| `DEEPAGENTS_MODEL` | No | `openai:gpt-5.2` | Model in `provider:model` format |
| `DEEPAGENTS_ALLOWED_DIRS` | No | All paths | Colon-separated list of directories the agent can access |

*Either `OPENAI_API_KEY` or `AGENT_TUI_OPENAI_API_KEY` is required for `--agent=deepagents`.

### Example .env file

```bash
# Required for DeepAgents
OPENAI_API_KEY=sk-your-key-here

# Optional: use a specific model
DEEPAGENTS_MODEL=openai:gpt-4o

# Optional: restrict file access to specific directories
DEEPAGENTS_ALLOWED_DIRS=/home/user/projects:/tmp/agent-scratch
```

## Architecture

The TUI communicates with any agent backend through `AgentProtocol` — a Python protocol class that emits typed `AgentEvent` objects. A `StubAgent` is included for development and testing.

See `agent_tui/protocol.py` for the contract.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run E2E tests only
uv run python tests/e2e/run_e2e.py

# Run E2E tests with pilot (fast, no PTY)
uv run python tests/e2e/run_e2e.py --pilot-only

# Run E2E tests with PTY (slow, terminal fidelity)
uv run python tests/e2e/run_e2e.py --pty-only
```
