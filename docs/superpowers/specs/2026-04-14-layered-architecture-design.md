# Layered Architecture — Design Spec

**Date:** 2026-04-14
**Status:** Approved
**Goal:** Reorganise `agent_tui` into a `src/` layout with five explicit layers — `domain`, `configurator`, `services`, `common`, `entrypoints` — and split the `config.py` monolith into three focused modules.

---

## 1. Motivation

The current flat `agent_tui/` package has 40+ modules at one level. There is no structural signal for which files are core contracts, which are configuration, which are utilities, and which are entry points. `config.py` (1,516 lines) is imported by ~25 files and acts as an accidental hub.

This refactor:
- Makes layer boundaries explicit and visible in the file tree
- Removes `config.py` as a monolith, replacing it with three focused modules
- Adopts the standard Python `src/` layout (PEP 517 / Hatch best practice)

---

## 2. Approach

**Option chosen: Move + split `config.py` only.**

All files move into their respective layers. `config.py` is deleted and its content split into `configurator/settings.py`, `configurator/glyphs.py`, and `configurator/console.py`. All other large files (`app.py`, `sessions.py`, widget files) are moved intact — no internal refactoring.

---

## 3. Target Directory Structure

```
agent-tui/
├── src/
│   └── agent_tui/
│       ├── __init__.py          # lazy-loads cli_main from entrypoints
│       ├── __main__.py          # python -m agent_tui
│       ├── py.typed
│       │
│       ├── domain/              # pure types and contracts, zero framework deps
│       │   ├── __init__.py
│       │   ├── protocol.py
│       │   ├── command_registry.py
│       │   ├── mcp_tools.py
│       │   ├── session_stats.py      # ← _session_stats.py (underscore dropped)
│       │   ├── ask_user_types.py     # ← _ask_user_types.py (underscore dropped)
│       │   └── cli_context.py        # ← _cli_context.py (underscore dropped)
│       │
│       ├── configurator/        # configuration management
│       │   ├── __init__.py
│       │   ├── settings.py      # Settings class, dotenv loading, shell safety, config paths
│       │   ├── glyphs.py        # Glyphs class, CharsetMode, glyph constants, is_ascii_mode
│       │   ├── console.py       # Rich console, banners, editable-install detection
│       │   ├── theme.py         # ← theme.py
│       │   ├── env_vars.py      # ← _env_vars.py
│       │   ├── version.py       # ← _version.py
│       │   ├── debug.py         # ← _debug.py
│       │   ├── model_config.py  # ← model_config.py (stub)
│       │   ├── default_agent_prompt.md
│       │   └── system_prompt.md
│       │
│       ├── services/            # stateful logic, I/O, integrations
│       │   ├── __init__.py
│       │   ├── adapter.py
│       │   ├── stub_agent.py
│       │   ├── sessions.py
│       │   ├── hooks.py
│       │   ├── file_ops.py
│       │   ├── media_utils.py
│       │   ├── input.py
│       │   ├── tool_display.py
│       │   ├── tools.py
│       │   ├── clipboard.py
│       │   ├── editor.py
│       │   ├── update_check.py
│       │   ├── project_utils.py
│       │   └── skills/
│       │       ├── __init__.py
│       │       ├── load.py
│       │       └── invocation.py
│       │
│       ├── common/              # pure stateless utilities
│       │   ├── __init__.py
│       │   ├── formatting.py
│       │   ├── unicode_security.py
│       │   └── output.py
│       │
│       └── entrypoints/         # TUI app + all widgets
│           ├── __init__.py
│           ├── main.py
│           ├── app.py
│           ├── app.tcss
│           ├── ui.py
│           └── widgets/
│               ├── __init__.py
│               ├── messages.py
│               ├── message_store.py
│               ├── chat_input.py
│               ├── autocomplete.py
│               ├── history.py
│               ├── ask_user.py
│               ├── approval.py
│               ├── tool_widgets.py
│               ├── tool_renderers.py
│               ├── diff.py
│               ├── loading.py
│               ├── status.py
│               ├── thread_selector.py
│               ├── model_selector.py
│               ├── theme_selector.py
│               ├── notification_settings.py
│               ├── welcome.py
│               ├── mcp_viewer.py
│               └── _links.py
│
├── tests/                       # unchanged
│   ├── __init__.py
│   ├── test_protocol.py
│   ├── test_stub_agent.py
│   └── test_adapter.py
│
└── pyproject.toml
```

---

## 4. Layer Rules

| Layer | May import from | Must NOT import from |
|-------|----------------|----------------------|
| `domain` | stdlib only | configurator, services, common, entrypoints |
| `configurator` | domain, stdlib | services, common, entrypoints |
| `services` | domain, configurator, common, stdlib | entrypoints |
| `common` | stdlib only | domain, configurator, services, entrypoints |
| `entrypoints` | all layers | — |

---

## 5. `config.py` Split

`config.py` (1,516 lines) is deleted. Its content is distributed as follows:

### `configurator/glyphs.py`
- `CharsetMode` (StrEnum)
- `class Glyphs`
- `UNICODE_GLYPHS`, `ASCII_GLYPHS`
- `_detect_charset_mode()`, `get_glyphs()`, `reset_glyphs_cache()`
- `is_ascii_mode()`
- `MAX_ARG_LENGTH`

Dependency: imports `settings` from `configurator/settings.py` (for charset detection from config).

### `configurator/settings.py`
- Thread locks, `_ensure_bootstrap()`, `_load_dotenv()`, `_find_dotenv_from_start_path()`
- `_DEFAULT_CONFIG_DIR`, `_DEFAULT_CONFIG_PATH`
- `_ShellAllowAll`, `parse_shell_allow_list()`
- `_read_config_toml_skills_dirs()`, `_parse_extra_skills_dirs()`
- `class Settings`, `class SessionState`
- `_get_settings()`, lazy `settings` module accessor (`__getattr__`)
- `newline_shortcut()`, `build_langsmith_thread_url()`
- `DANGEROUS_SHELL_PATTERNS`, `RECOMMENDED_SAFE_SHELL_COMMANDS`
- `contains_dangerous_patterns()`, `is_shell_command_allowed()`
- `get_default_coding_instructions()`

Dependency: imports `env_vars` from `configurator/env_vars.py`.

### `configurator/console.py`
- `_get_git_branch()`
- `_resolve_editable_info()`, `_is_editable_install()`, `_get_editable_install_path()`
- `_UNICODE_BANNER`, `_ASCII_BANNER`, `get_banner()`
- `_get_console()`, lazy `console` module accessor (`__getattr__`)

Dependency: imports `get_glyphs` from `configurator/glyphs.py`.

### Dependency order within `configurator/`

```
settings.py  ←  glyphs.py  ←  console.py
```

No cycles.

---

## 6. `pyproject.toml` Changes

```toml
# Before
[tool.hatch.build.targets.wheel]
packages = ["agent_tui"]

# After
[tool.hatch.build.targets.wheel]
packages = ["src/agent_tui"]
```

Entry point is unchanged:
```toml
[project.scripts]
agent-tui = "agent_tui:cli_main"
```

---

## 7. Import Path Mapping

All internal imports gain a layer segment. Full mapping:

| Old import path | New import path |
|-----------------|-----------------|
| `agent_tui.protocol` | `agent_tui.domain.protocol` |
| `agent_tui.command_registry` | `agent_tui.domain.command_registry` |
| `agent_tui.mcp_tools` | `agent_tui.domain.mcp_tools` |
| `agent_tui._session_stats` | `agent_tui.domain.session_stats` |
| `agent_tui._ask_user_types` | `agent_tui.domain.ask_user_types` |
| `agent_tui._cli_context` | `agent_tui.domain.cli_context` |
| `agent_tui.config` → `settings` / `newline_shortcut` / `build_langsmith_thread_url` | `agent_tui.configurator.settings` |
| `agent_tui.config` → `get_glyphs` / `Glyphs` / `is_ascii_mode` / `MAX_ARG_LENGTH` | `agent_tui.configurator.glyphs` |
| `agent_tui.config` → `console` / `_is_editable_install` | `agent_tui.configurator.console` |
| `agent_tui.theme` | `agent_tui.configurator.theme` |
| `agent_tui._env_vars` | `agent_tui.configurator.env_vars` |
| `agent_tui._version` | `agent_tui.configurator.version` |
| `agent_tui._debug` | `agent_tui.configurator.debug` |
| `agent_tui.model_config` | `agent_tui.configurator.model_config` |
| `agent_tui.adapter` | `agent_tui.services.adapter` |
| `agent_tui.stub_agent` | `agent_tui.services.stub_agent` |
| `agent_tui.sessions` | `agent_tui.services.sessions` |
| `agent_tui.hooks` | `agent_tui.services.hooks` |
| `agent_tui.file_ops` | `agent_tui.services.file_ops` |
| `agent_tui.media_utils` | `agent_tui.services.media_utils` |
| `agent_tui.input` | `agent_tui.services.input` |
| `agent_tui.tool_display` | `agent_tui.services.tool_display` |
| `agent_tui.tools` | `agent_tui.services.tools` |
| `agent_tui.clipboard` | `agent_tui.services.clipboard` |
| `agent_tui.editor` | `agent_tui.services.editor` |
| `agent_tui.update_check` | `agent_tui.services.update_check` |
| `agent_tui.project_utils` | `agent_tui.services.project_utils` |
| `agent_tui.skills` | `agent_tui.services.skills` |
| `agent_tui.formatting` | `agent_tui.common.formatting` |
| `agent_tui.unicode_security` | `agent_tui.common.unicode_security` |
| `agent_tui.output` | `agent_tui.common.output` |
| `agent_tui.app` | `agent_tui.entrypoints.app` |
| `agent_tui.main` | `agent_tui.entrypoints.main` |
| `agent_tui.ui` | `agent_tui.entrypoints.ui` |
| `agent_tui.widgets` | `agent_tui.entrypoints.widgets` |

### Renamed files (underscore prefix dropped)

| Old filename | New filename |
|---|---|
| `_session_stats.py` | `session_stats.py` |
| `_ask_user_types.py` | `ask_user_types.py` |
| `_cli_context.py` | `cli_context.py` |
| `_env_vars.py` | `env_vars.py` |
| `_version.py` | `version.py` |
| `_debug.py` | `debug.py` |

(`_links.py` in widgets keeps its underscore — it's a widget-internal helper.)

---

## 8. Files Deleted

- `agent_tui/config.py` — replaced by `configurator/settings.py`, `configurator/glyphs.py`, `configurator/console.py`

---

## 9. Execution Approach

1. Create `src/` layout: `mkdir -p src/ && mv agent_tui src/`
2. Create all layer `__init__.py` files
3. Move files into their layers (rename underscore files)
4. Create `configurator/glyphs.py`, `configurator/settings.py`, `configurator/console.py` from `config.py`
5. Delete `config.py`
6. Update all internal imports throughout the codebase
7. Update `pyproject.toml`
8. Run `uv run pytest` — all 23 tests must pass
9. Run `uv run agent-tui` — TUI must launch

---

## 10. Success Criteria

- `uv run agent-tui` launches the TUI normally
- All 23 tests pass
- `grep -r "from agent_tui.config" src/` returns zero results
- `grep -r "agent_tui\." src/agent_tui/domain/` shows no imports from `configurator`, `services`, `common`, or `entrypoints`
- `grep -r "agent_tui\." src/agent_tui/common/` shows no imports from other layers
