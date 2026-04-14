# DeepAgents Integration — Architecture Spec

**Date:** 2026-04-14
**Status:** Approved
**Goal:** Integrate LangChain DeepAgents as the production agent backend while maintaining complete TUI isolation from implementation details.

---

## 1. Motivation

The `agent-tui` scaffold provides a Textual-based TUI for coding agents. It currently ships with `StubAgent` for development/testing. To become a full Claude Code alternative, we need a production-grade agent backend. LangChain DeepAgents provides:

- **Planning** — task decomposition via `write_todos`
- **File operations** — read, write, edit via virtual filesystem
- **Shell execution** — via `LocalShellBackend`
- **Web search** — via Tavily integration
- **Subagents** — context isolation for complex subtasks
- **Context management** — summarization and offloading
- **Memory** — persistent context across sessions
- **Human-in-the-loop** — tool approval workflows

DeepAgents is an **implementation detail**. The TUI must remain agnostic to which backend drives it.

---

## 2. Core Architectural Principle

**The `AgentProtocol` contract is the firewall.**

```
┌──────────────────────────────────────────────────────────────────────┐
│  ENTRYPOINTS (TUI — Textual App)                                    │
│  AgentTuiApp ──uses──► AgentAdapter ──drives──► AgentProtocol       │
└──────────────────────────────────────────────────────────────────────┘
                                       ▲
                                       │  (Protocol contract only)
                          ┌────────────┴────────────┐
                          │                         │
                   ┌──────┴──────┐         ┌───────┴───────┐
                   │  StubAgent  │         │ DeepAgentsAdapter│
                   │ (reference) │         │ (wraps DeepAgent) │
                   └─────────────┘         └─────────────────┘
```

**Rule:** `entrypoints` may NOT import from `deep_agents` or any backend-specific module. All communication flows through `AgentProtocol`.

---

## 3. AgentProtocol Contract

### Current Interface
```python
@runtime_checkable
class AgentProtocol(Protocol):
    async def stream(self, message: str, *, thread_id: str | None = None) -> AsyncIterator[AgentEvent]
    async def approve_tool(self, tool_id: str, approved: bool) -> None
    async def answer_question(self, answer: str) -> None
    async def cancel(self) -> None
    async def get_threads(self) -> list[dict[str, Any]]
    async def get_models(self) -> list[dict[str, Any]]
    async def set_model(self, model_name: str) -> None
    async def get_skills(self) -> list[dict[str, Any]]
    async def invoke_skill(self, name: str, args: str) -> None
```

### Extended EventType
```python
class EventType(StrEnum):
    # Existing
    MESSAGE_CHUNK = "message_chunk"
    MESSAGE_END = "message_end"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ASK_USER = "ask_user"
    TOKEN_UPDATE = "token_update"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    # New
    PLAN_STEP = "plan_step"
    SUBAGENT_START = "subagent_start"
    SUBAGENT_END = "subagent_end"
    CONTEXT_SUMMARIZED = "context_summarized"
    INTERRUPT = "interrupt"
```

### Extended AgentEvent
```python
@dataclass
class AgentEvent:
    type: EventType
    text: str = ""
    tool_name: str = ""
    tool_args: dict[str, Any] = field(default_factory=dict)
    tool_output: str = ""
    tool_id: str = ""
    question: str = ""
    token_count: int = 0
    context_limit: int = 0
    status_text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    # New fields
    subagent_name: str = ""
    plan_step_text: str = ""
    plan_total_steps: int = 0
    plan_current_step: int = 0
```

---

## 4. DeepAgentsAdapter

### Location
`services/deep_agents/adapter.py`

### Responsibilities
1. Implement `AgentProtocol` fully
2. Wrap `create_deep_agent()` from `deepagents`
3. Translate LangGraph checkpoint events to `AgentEvent` stream
4. Bridge TUI approval decisions to DeepAgents interrupt mechanism
5. Manage thread lifecycle via LangGraph checkpointer

### Initialization
```python
class DeepAgentsAdapter:
    def __init__(
        self,
        model: str = "openai:gpt-4o",
        tools: Sequence[BaseTool] | None = None,
        system_prompt: str | None = None,
        interrupt_on: dict[str, bool] | None = None,
    ) -> None:
```

### Backend Configuration
```python
# Phase 2+: LocalShellBackend for shell execution
from deepagents.backends import LocalShellBackend, FilesystemBackend

backend = CompositeBackend(
    default=FilesystemBackend(root_dir="."),
    routes={"/": LocalShellBackend(root_dir=".", env={"PATH": "/usr/bin:/bin"})},
)
```

### Stream Implementation
```python
async def stream(self, message: str, *, thread_id: str | None = None) -> AsyncIterator[AgentEvent]:
    config = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}
    
    async for event in self._agent.astream_events(
        {"messages": [{"role": "user", "content": message}]},
        config,
    ):
        yield from self._translator.translate(event)
```

---

## 5. EventTranslator

### Location
`services/deep_agents/event_translator.py`

### Responsibilities
1. Parse DeepAgents/LangGraph event structure
2. Map built-in tool names to standardized names
3. Extract streaming chunks from message events
4. Handle interrupt events
5. Handle subagent events

### Tool Name Mapping
| DeepAgents Tool | TUI Tool Name |
|-----------------|---------------|
| `read_file` | `Read` |
| `write_file` | `Write` |
| `edit_file` | `Edit` |
| `glob` | `Glob` |
| `grep` | `Grep` |
| `ls` | `Ls` |
| `execute` | `Bash` |
| `web_search` | `WebSearch` |
| `fetch_url` | `FetchUrl` |
| `task` | `Subagent` |
| `ask_user` | `AskUser` |
| `compact_conversation` | `Compact` |
| `write_todos` | `Todo` |

---

## 6. Layer Rules

| Layer | May Import | Must NOT Import |
|-------|------------|----------------|
| `domain` | stdlib only | deepagents, configurator, services, entrypoints |
| `configurator` | domain, stdlib | services, entrypoints |
| `services` | domain, configurator, common, stdlib | entrypoints |
| `common` | stdlib only | all layers |
| `entrypoints` | all layers | deepagents (enforced by architecture) |

**Enforcement:** `grep -r "from deepagents" src/agent_tui/entrypoints/` must return zero results.

---

## 7. CLI Integration

### Flag
```python
# entrypoints/main.py
parser.add_argument(
    "--agent",
    choices=["stub", "deepagents"],
    default="stub",
    help="Agent backend to use",
)
```

### Backend Selection
```python
if args.agent == "deepagents":
    from agent_tui.services.deep_agents import DeepAgentsAdapter
    agent = DeepAgentsAdapter.from_settings()
else:
    from agent_tui.services.stub_agent import StubAgent
    agent = StubAgent()
```

### Settings Integration
```python
# configurator/settings.py
@property
def deepagents_model(self) -> str:
    return os.environ.get("DEEPAGENTS_MODEL", "openai:gpt-4o")

@property
def openai_api_key(self) -> str | None:
    return os.environ.get("OPENAI_API_KEY")
```

---

## 8. Phases

| Phase | Branch | Goal |
|-------|--------|------|
| 1 | `phase/1-foundation` | DeepAgents streaming, basic message display |
| 2 | `phase/2-file-operations` | File tools via TUI approval |
| 3 | `phase/3-shell-execution` | execute tool + shell safety |
| 4 | `phase/4-web-search` | web_search, fetch_url |
| 5 | `phase/5-planning-subagents` | Planning indicator, subagent display |
| 6 | `phase/6-context-management` | Token display, context compaction |
| 7 | `phase/7-memory-skills` | AGENTS.md memory, skills |
| 8 | `phase/8-hitl-refinement` | Full interrupt/resume flow |
| 9 | `phase/9-mcp-sandboxes` | MCP tools, sandbox backends (future) |

---

## 9. Dependencies

```toml
# pyproject.toml
dependencies = [
    # Existing
    "textual>=8.0.0,<9.0.0",
    "rich>=14.0.0,<15.0.0",
    # ... rest of existing deps
    
    # Phase 1
    "deepagents>=0.5.2",
    "langchain-openai>=0.3.0",
    
    # Phase 4
    "tavily-python>=1.0.0",
]
```

---

## 10. File Structure

```
src/agent_tui/
├── domain/
│   └── protocol.py              # [MODIFIED] + EventType, + AgentEvent fields
├── services/
│   ├── adapter.py               # [MODIFIED] + handlers for new event types
│   ├── stub_agent.py           # [UNCHANGED]
│   └── deep_agents/            # [NEW]
│       ├── __init__.py         # exports DeepAgentsAdapter, EventTranslator
│       ├── adapter.py          # DeepAgentsAdapter (AgentProtocol impl)
│       ├── event_translator.py # checkpoint → AgentEvent translation
│       ├── backend.py          # [Phase 2+] backend configuration
│       ├── memory.py           # [Phase 7] memory bridge
│       ├── skills.py           # [Phase 7] skills bridge
│       ├── mcp.py              # [Phase 9] MCP integration
│       └── sandbox.py          # [Phase 9] sandbox backends
├── configurator/
│   └── settings.py             # [MODIFIED] + API key handling
└── entrypoints/
    ├── main.py                  # [MODIFIED] --agent flag
    └── app.py                  # [MODIFIED] + stub methods for new events
```

---

## 11. Testing Strategy

| Test | Scope | Location |
|------|-------|----------|
| `test_agent_protocol` | Runtime checkable protocol compliance | `tests/test_protocol.py` |
| `test_stub_agent` | StubAgent event sequences | `tests/test_stub_agent.py` |
| `test_adapter` | AgentAdapter dispatch logic | `tests/test_adapter.py` |
| `test_deep_agents_adapter` | DeepAgentsAdapter translation | `tests/test_deep_agents_adapter.py` |
| `test_event_translator` | EventTranslator mapping | `tests/test_event_translator.py` |

**Protocol compliance test:**
```python
def test_deep_agents_adapter_implements_protocol():
    from agent_tui.services.deep_agents import DeepAgentsAdapter
    assert isinstance(DeepAgentsAdapter(), AgentProtocol)
```

---

## 12. Rollback Plan

If DeepAgents integration reveals fundamental issues:
1. Keep `StubAgent` as default (`--agent=stub`)
2. `deep_agents/` module can be moved to `services/deprecated/deep_agents/`
3. TUI requires no changes — `AgentProtocol` remains the contract
4. No migration needed — protocol-based design ensures loose coupling
