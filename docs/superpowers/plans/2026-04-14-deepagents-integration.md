# DeepAgents Integration — Implementation Plan

**Date:** 2026-04-14
**Status:** Approved
**Spec:** `docs/superpowers/specs/2026-04-14-deepagents-integration-architecture.md`

---

## Branch Strategy

```
main ───────────────────────────────────────────────────────────────────
         \
          phase/1-foundation ──────────────────────────────────────────
                   \
                    phase/2-file-operations ───────────────────────────
                             \
                              phase/3-shell-execution ─────────────────
                                       \
                                        phase/4-web-search ───────────
                                                  \
                                                   phase/5-planning-subagents
                                                            \
                                                             phase/6-context-management
                                                                      \
                                                                       phase/7-memory-skills
                                                                                \
                                                                                 phase/8-hitl-refinement
                                                                                          \
                                                                                           phase/9-mcp-sandboxes (future)
```

Linear merge strategy — each phase branch merges into the previous.

---

## Phase 1: Foundation
**Branch:** `phase/1-foundation`
**Merge into:** `main`
**Goal:** DeepAgents streaming working through TUI with basic message display

### Tasks
| # | Component | Change |
|---|-----------|--------|
| 1.1 | `domain/protocol.py` | Add `PLAN_STEP`, `SUBAGENT_START`, `SUBAGENT_END`, `CONTEXT_SUMMARIZED`, `INTERRUPT` to `EventType`; extend `AgentEvent` with `subagent_name`, `plan_step_text`, `plan_total_steps`, `plan_current_step` fields |
| 1.2 | `services/deep_agents/__init__.py` | New module init — exports `DeepAgentsAdapter`, `EventTranslator` |
| 1.3 | `services/deep_agents/event_translator.py` | Translate LangGraph checkpoint events → `AgentEvent` stream; handles messages, tool_calls, interrupts |
| 1.4 | `services/deep_agents/adapter.py` | `DeepAgentsAdapter` implements `AgentProtocol` fully; default model `openai:gpt-4o`; Phase 1: no custom tools |
| 1.5 | `services/adapter.py` | Add `_dispatch()` handlers for 5 new event types calling stub app methods |
| 1.6 | `entrypoints/main.py` | Add `--agent` flag: `stub` (default) vs `deepagents`; backend selection in `cli_main()` |
| 1.7 | `entrypoints/app.py` | Add stub methods: `show_plan_step()`, `show_subagent_started()`, `show_subagent_finished()`, `show_context_summarized()`, `pause_for_human_input()` |
| 1.8 | `configurator/settings.py` | Add `OPENAI_API_KEY`, `DEEPAGENTS_MODEL` env var handling |
| 1.9 | `pyproject.toml` | Add `deepagents>=0.5.2`, `langchain-openai` |
| 1.10 | `tests/test_deep_agents_adapter.py` | Unit tests for `DeepAgentsAdapter` |

### Files Created
```
services/deep_agents/__init__.py
services/deep_agents/adapter.py
services/deep_agents/event_translator.py
tests/test_deep_agents_adapter.py
```

### Files Modified
```
domain/protocol.py
services/adapter.py
entrypoints/main.py
entrypoints/app.py
configurator/settings.py
pyproject.toml
```

### Verification
- [ ] `agent-tui --agent=stub` launches (existing behavior)
- [ ] `agent-tui --agent=deepagents` launches
- [ ] Message sent → response streams and displays
- [ ] `get_models()` returns OpenAI model list
- [ ] All tests pass

---

## Phase 2: File Operations
**Branch:** `phase/2-file-operations`
**Merge into:** `phase/1-foundation`
**Goal:** File tools (read, write, edit) flow through TUI approval system

### Tasks
| # | Component | Change |
|---|-----------|--------|
| 2.1 | `services/deep_agents/adapter.py` | Map DeepAgents built-in tools (read_file, write_file, edit_file, glob, grep) → `TOOL_CALL` events |
| 2.2 | `services/deep_agents/event_translator.py` | Translate tool call results back to `TOOL_RESULT` events |
| 2.3 | `entrypoints/app.py` | Ensure approval widgets display file tool args (path, content preview) |
| 2.4 | `entrypoints/app.py` | Implement `show_plan_step`, `show_subagent_*` properly (not just stubs) |
| 2.5 | `services/adapter.py` | Handle file tool results with appropriate display |
| 2.6 | `configurator/settings.py` | Add file path allowlist configuration (which directories agent can access) |

### Verification
- [ ] "Read this file" → approval request appears in TUI
- [ ] User approves → file content displays
- [ ] "Write to file" → shows path and content preview
- [ ] Agent can complete file operations end-to-end

---

## Phase 3: Shell Execution
**Branch:** `phase/3-shell-execution`
**Merge into:** `phase/2-file-operations`
**Goal:** `execute` tool works with TUI safety controls

### Tasks
| # | Component | Change |
|---|-----------|--------|
| 3.1 | `services/deep_agents/backend.py` | Integrate `LocalShellBackend` + `FilesystemBackend` |
| 3.2 | `services/deep_agents/adapter.py` | Map `execute` → `TOOL_CALL`; parse command args |
| 3.3 | `configurator/settings.py` | Shell allowlist patterns (reuse/extend `DANGEROUS_SHELL_PATTERNS`) |
| 3.4 | `entrypoints/app.py` | Shell approval UI with command preview (styled diff-like) |
| 3.5 | `entrypoints/app.py` | Implement `pause_for_human_input()` properly |

### Verification
- [ ] `execute "echo hello"` runs after approval
- [ ] Dangerous patterns blocked with clear error
- [ ] Command output streams to TUI

---

## Phase 4: Web Search
**Branch:** `phase/4-web-search`
**Merge into:** `phase/3-shell-execution`
**Goal:** `web_search`, `fetch_url` tools work

### Tasks
| # | Component | Change |
|---|-----------|--------|
| 4.1 | `services/deep_agents/adapter.py` | Map web_search, fetch_url → `TOOL_CALL` |
| 4.2 | `configurator/settings.py` | Add `TAVILY_API_KEY` env var |
| 4.3 | `pyproject.toml` | Add `tavily-python` |
| 4.4 | `entrypoints/app.py` | Search results widget (formatted output) |
| 4.5 | `entrypoints/app.py` | Implement `show_context_summarized()` properly |

### Verification
- [ ] "Search the web" → approval request → results display
- [ ] fetch_url renders markdown nicely

---

## Phase 5: Planning & Subagents
**Branch:** `phase/5-planning-subagents`
**Merge into:** `phase/4-web-search`
**Goal:** Display agent planning and subagent delegation

### Tasks
| # | Component | Change |
|---|-----------|--------|
| 5.1 | `services/adapter.py` | `PLAN_STEP` → planning progress widget |
| 5.2 | `services/adapter.py` | `SUBAGENT_START/END` → activity indicator |
| 5.3 | `entrypoints/app.py` | Planning step widget (collapsible, shows current/total) |
| 5.4 | `entrypoints/app.py` | Subagent activity display |
| 5.5 | `services/deep_agents/adapter.py` | Map DeepAgents `task` tool → `SUBAGENT_*` events |

### Verification
- [ ] "Planning..." indicator shows when agent is decomposing task
- [ ] Subagent spawning shows name and status

---

## Phase 6: Context Management
**Branch:** `phase/6-context-management`
**Merge into:** `phase/5-planning-subagents`
**Goal:** Token display and context compaction visible

### Tasks
| # | Component | Change |
|---|-----------|--------|
| 6.1 | `services/adapter.py` | `CONTEXT_SUMMARIZED` → update context meter |
| 6.2 | `domain/session_stats.py` | Add context window fields |
| 6.3 | `entrypoints/app.py` | Context window usage bar (percentage display) |
| 6.4 | `services/deep_agents/adapter.py` | Map `compact_conversation` tool |

### Verification
- [ ] Token count always visible in status bar
- [ ] Context compaction shows progress indicator
- [ ] Offloaded messages indicated visually

---

## Phase 7: Memory & Skills
**Branch:** `phase/7-memory-skills`
**Merge into:** `phase/6-context-management`
**Goal:** AGENTS.md memory and skills system integrated

### Tasks
| # | Component | Change |
|---|-----------|--------|
| 7.1 | `services/deep_agents/memory.py` | Bridge DeepAgents `InMemoryStore` ↔ TUI session |
| 7.2 | `services/deep_agents/skills.py` | Map DeepAgents skills → `get_skills()` / `invoke_skill()` |
| 7.3 | `entrypoints/app.py` | Skills panel (list, invoke button) |
| 7.4 | `entrypoints/app.py` | Memory view (show what's persisted) |
| 7.5 | `services/deep_agents/backend.py` | Configure `StoreBackend` for cross-thread persistence |

### Verification
- [ ] Skills listed in TUI
- [ ] `/skill:name` invocation works
- [ ] Memory persists across sessions

---

## Phase 8: Human-in-the-Loop Refinement
**Branch:** `phase/8-hitl-refinement`
**Merge into:** `phase/7-memory-skills`
**Goal:** Full interrupt/resume flow

### Tasks
| # | Component | Change |
|---|-----------|--------|
| 8.1 | `services/deep_agents/adapter.py` | `approve_tool()` triggers LangGraph resume after approval |
| 8.2 | `services/adapter.py` | `INTERRUPT` → pause UI, show approval state |
| 8.3 | `services/deep_agents/backend.py` | Configure `interrupt_on` per-tool; add checkpointer |
| 8.4 | `entrypoints/app.py` | Interrupt overlay with approve/edit/reject options |
| 8.5 | `entrypoints/app.py` | Implement `request_tool_approval()` fully |

### Verification
- [ ] Agent pauses on sensitive tools
- [ ] User can approve/edit/reject
- [ ] Agent resumes correctly after decision

---

## Phase 9: MCP & Sandboxes (Future)
**Branch:** `phase/9-mcp-sandboxes`
**Merge into:** `phase/8-hitl-refinement`
**Goal:** MCP tool loading, sandbox isolation

### Tasks
| # | Component | Change |
|---|-----------|--------|
| 9.1 | `services/deep_agents/mcp.py` | MCP server discovery, `.mcp.json` parsing |
| 9.2 | `services/deep_agents/sandbox.py` | Sandbox backend integration |
| 9.3 | `entrypoints/app.py` | MCP tools panel |

---

## Complete File Change Map

### New Files (by phase)
```
Phase 1:
  services/deep_agents/__init__.py
  services/deep_agents/adapter.py
  services/deep_agents/event_translator.py
  tests/test_deep_agents_adapter.py

Phase 2+:
  services/deep_agents/backend.py
  services/deep_agents/memory.py
  services/deep_agents/skills.py
  services/deep_agents/mcp.py
  services/deep_agents/sandbox.py
```

### Modified Files (cumulative)
```
domain/protocol.py              (Phase 1)
services/adapter.py             (Phase 1-8)
entrypoints/main.py             (Phase 1)
entrypoints/app.py              (Phase 1-8)
configurator/settings.py       (Phase 1-4)
pyproject.toml                  (Phase 1, 4)
domain/session_stats.py         (Phase 6)
```

---

## Layer Compliance Summary

| Layer | Rule | DeepAgents Integration |
|-------|------|----------------------|
| `domain` | stdlib only | EventType additions are pure types |
| `configurator` | domain + stdlib | API key env vars |
| `services` | domain + configurator + common + stdlib | DeepAgentsAdapter, EventTranslator |
| `entrypoints` | all layers | Only imports AgentProtocol, never deepagents directly |

---

## Dependencies Added (by phase)

```toml
# Phase 1
deepagents>=0.5.2
langchain-openai>=0.3.0

# Phase 4
tavily-python>=1.0.0

# Future phases (not in pyproject yet)
langchain-anthropic  # when adding Anthropic support
langchain-google-genai  # when adding Gemini support
```

---

## Rollback Plan

If DeepAgents integration reveals fundamental issues:
1. Keep `StubAgent` as default (`--agent=stub`)
2. Move `deep_agents/` to `services/deprecated/deep_agents/` if abandoned
3. TUI requires no changes — `AgentProtocol` remains the contract
4. No migration needed — protocol-based design ensures loose coupling
