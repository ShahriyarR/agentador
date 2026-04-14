# Layered Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganise `agent_tui` into a `src/` layout with five explicit layers (`domain`, `configurator`, `services`, `common`, `entrypoints`) and split `config.py` into three focused modules.

**Architecture:** Move the flat `agent_tui/` package under `src/`, create five layer subdirectories, move each file into its layer, and split `config.py` (1,516 lines) into `configurator/glyphs.py`, `configurator/settings.py`, and `configurator/console.py`. All 23 existing tests must pass after every task. No logic changes — pure reorganisation.

**Tech Stack:** Python 3.11+, hatchling (build backend), uv (package manager), Textual ≥ 8.0.0

**Spec:** `docs/superpowers/specs/2026-04-14-layered-architecture-design.md`

**One deviation from spec:** `project_utils.py` moves to `configurator/` (not `services/`) because `settings.py` has a lazy import of `get_server_project_context` inside `_ensure_bootstrap()`. Putting it in `services/` would create a `configurator → services` dependency that violates the layer rules.

---

## File Map

### Files created (new)
- `src/agent_tui/configurator/glyphs.py` — split from config.py: CharsetMode, Glyphs, glyph constants, charset detection
- `src/agent_tui/configurator/settings.py` — split from config.py: Settings class, dotenv bootstrap, shell safety
- `src/agent_tui/configurator/console.py` — split from config.py: Rich console, banners, editable-install detection
- `src/agent_tui/{domain,configurator,services,common,entrypoints}/__init__.py` — empty layer init files

### Files moved (path changes only, content unchanged except internal imports)

| Source | Destination |
|--------|-------------|
| `agent_tui/protocol.py` | `src/agent_tui/domain/protocol.py` |
| `agent_tui/command_registry.py` | `src/agent_tui/domain/command_registry.py` |
| `agent_tui/mcp_tools.py` | `src/agent_tui/domain/mcp_tools.py` |
| `agent_tui/_session_stats.py` | `src/agent_tui/domain/session_stats.py` |
| `agent_tui/_ask_user_types.py` | `src/agent_tui/domain/ask_user_types.py` |
| `agent_tui/_cli_context.py` | `src/agent_tui/domain/cli_context.py` |
| `agent_tui/theme.py` | `src/agent_tui/configurator/theme.py` |
| `agent_tui/_env_vars.py` | `src/agent_tui/configurator/env_vars.py` |
| `agent_tui/_version.py` | `src/agent_tui/configurator/version.py` |
| `agent_tui/_debug.py` | `src/agent_tui/configurator/debug.py` |
| `agent_tui/model_config.py` | `src/agent_tui/configurator/model_config.py` |
| `agent_tui/project_utils.py` | `src/agent_tui/configurator/project_utils.py` |
| `agent_tui/default_agent_prompt.md` | `src/agent_tui/configurator/default_agent_prompt.md` |
| `agent_tui/system_prompt.md` | `src/agent_tui/configurator/system_prompt.md` |
| `agent_tui/formatting.py` | `src/agent_tui/common/formatting.py` |
| `agent_tui/unicode_security.py` | `src/agent_tui/common/unicode_security.py` |
| `agent_tui/output.py` | `src/agent_tui/common/output.py` |
| `agent_tui/adapter.py` | `src/agent_tui/services/adapter.py` |
| `agent_tui/stub_agent.py` | `src/agent_tui/services/stub_agent.py` |
| `agent_tui/sessions.py` | `src/agent_tui/services/sessions.py` |
| `agent_tui/hooks.py` | `src/agent_tui/services/hooks.py` |
| `agent_tui/file_ops.py` | `src/agent_tui/services/file_ops.py` |
| `agent_tui/media_utils.py` | `src/agent_tui/services/media_utils.py` |
| `agent_tui/input.py` | `src/agent_tui/services/input.py` |
| `agent_tui/tool_display.py` | `src/agent_tui/services/tool_display.py` |
| `agent_tui/tools.py` | `src/agent_tui/services/tools.py` |
| `agent_tui/clipboard.py` | `src/agent_tui/services/clipboard.py` |
| `agent_tui/editor.py` | `src/agent_tui/services/editor.py` |
| `agent_tui/update_check.py` | `src/agent_tui/services/update_check.py` |
| `agent_tui/skills/` | `src/agent_tui/services/skills/` |
| `agent_tui/main.py` | `src/agent_tui/entrypoints/main.py` |
| `agent_tui/app.py` | `src/agent_tui/entrypoints/app.py` |
| `agent_tui/app.tcss` | `src/agent_tui/entrypoints/app.tcss` |
| `agent_tui/ui.py` | `src/agent_tui/entrypoints/ui.py` |
| `agent_tui/widgets/` | `src/agent_tui/entrypoints/widgets/` |

### Files deleted
- `src/agent_tui/config.py` — replaced by `configurator/glyphs.py`, `configurator/settings.py`, `configurator/console.py`

### Files modified (import paths updated only)
- `src/agent_tui/__init__.py` — update lazy import paths
- `src/agent_tui/__main__.py` — update import path
- `pyproject.toml` — update `packages` path
- Every `.py` file in `src/agent_tui/` — update `from agent_tui.X` → `from agent_tui.layer.X`
- `tests/test_protocol.py`, `tests/test_adapter.py`, `tests/test_stub_agent.py` — update import paths

---

### Task 1: Move to src/ layout and create layer scaffold

**Files:**
- Modify: `pyproject.toml`
- Create: `src/agent_tui/{domain,configurator,services,common,entrypoints}/__init__.py`

- [ ] **Step 1: Move the package under src/**

```bash
cd /home/shahriyarrzayev/REPOS/Learning_and_Development/agent-tui
mkdir src
git mv agent_tui src/agent_tui
```

- [ ] **Step 2: Create layer directories and empty `__init__.py` files**

```bash
mkdir -p src/agent_tui/{domain,configurator,services,common,entrypoints}
touch src/agent_tui/domain/__init__.py
touch src/agent_tui/configurator/__init__.py
touch src/agent_tui/services/__init__.py
touch src/agent_tui/common/__init__.py
touch src/agent_tui/entrypoints/__init__.py
```

- [ ] **Step 3: Update `pyproject.toml`**

In `pyproject.toml`, change:
```toml
[tool.hatch.build.targets.wheel]
packages = ["agent_tui"]
```
to:
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/agent_tui"]
```

- [ ] **Step 4: Verify the package is importable**

```bash
uv run python -c "import agent_tui; print(agent_tui.__version__)"
```

Expected: prints the version string (e.g. `0.1.0`). If it prints, the src layout is wired correctly.

- [ ] **Step 5: Run tests**

```bash
uv run pytest tests/ -q
```

Expected: `23 passed` — nothing changed yet, just the directory location.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: move package to src/ layout and scaffold layer directories"
```

---

### Task 2: Move domain/ files and update all callers

**Files:**
- Move: `src/agent_tui/{protocol,command_registry,mcp_tools,_session_stats,_ask_user_types,_cli_context}.py` → `src/agent_tui/domain/`
- Modify: `tests/test_protocol.py`, `tests/test_adapter.py`, `tests/test_stub_agent.py`
- Modify: every file that imports these modules

Domain files have zero internal `agent_tui` imports (they are pure stdlib/dataclasses), so no imports need updating inside the moved files themselves.

- [ ] **Step 1: Move the six domain files**

```bash
cd /home/shahriyarrzayev/REPOS/Learning_and_Development/agent-tui
git mv src/agent_tui/protocol.py        src/agent_tui/domain/protocol.py
git mv src/agent_tui/command_registry.py src/agent_tui/domain/command_registry.py
git mv src/agent_tui/mcp_tools.py       src/agent_tui/domain/mcp_tools.py
git mv src/agent_tui/_session_stats.py  src/agent_tui/domain/session_stats.py
git mv src/agent_tui/_ask_user_types.py src/agent_tui/domain/ask_user_types.py
git mv src/agent_tui/_cli_context.py    src/agent_tui/domain/cli_context.py
```

- [ ] **Step 2: Update all callers with sed**

```bash
# All files under src/ and tests/
FILES=$(find src tests -name "*.py")

# protocol
echo "$FILES" | xargs sed -i 's/from agent_tui\.protocol /from agent_tui.domain.protocol /g'
echo "$FILES" | xargs sed -i 's/from agent_tui\.protocol\b/from agent_tui.domain.protocol/g'

# command_registry
echo "$FILES" | xargs sed -i 's/from agent_tui\.command_registry /from agent_tui.domain.command_registry /g'
echo "$FILES" | xargs sed -i 's/from agent_tui\.command_registry\b/from agent_tui.domain.command_registry/g'
echo "$FILES" | xargs sed -i 's/import agent_tui\.command_registry/import agent_tui.domain.command_registry/g'

# mcp_tools
echo "$FILES" | xargs sed -i 's/from agent_tui\.mcp_tools /from agent_tui.domain.mcp_tools /g'
echo "$FILES" | xargs sed -i 's/from agent_tui\.mcp_tools\b/from agent_tui.domain.mcp_tools/g'

# _session_stats → session_stats (rename!)
echo "$FILES" | xargs sed -i 's/from agent_tui\._session_stats /from agent_tui.domain.session_stats /g'
echo "$FILES" | xargs sed -i 's/from agent_tui\._session_stats\b/from agent_tui.domain.session_stats/g'
echo "$FILES" | xargs sed -i 's/agent_tui\._session_stats/agent_tui.domain.session_stats/g'

# _ask_user_types → ask_user_types (rename!)
echo "$FILES" | xargs sed -i 's/from agent_tui\._ask_user_types /from agent_tui.domain.ask_user_types /g'
echo "$FILES" | xargs sed -i 's/from agent_tui\._ask_user_types\b/from agent_tui.domain.ask_user_types/g'
echo "$FILES" | xargs sed -i 's/agent_tui\._ask_user_types/agent_tui.domain.ask_user_types/g'

# _cli_context → cli_context (rename!)
echo "$FILES" | xargs sed -i 's/from agent_tui\._cli_context /from agent_tui.domain.cli_context /g'
echo "$FILES" | xargs sed -i 's/from agent_tui\._cli_context\b/from agent_tui.domain.cli_context/g'
echo "$FILES" | xargs sed -i 's/agent_tui\._cli_context/agent_tui.domain.cli_context/g'
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest tests/ -q
```

Expected: `23 passed`

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: move domain files to agent_tui/domain/"
```

---

### Task 3: Split config.py into configurator/ and move configurator files

This is the most complex task. `config.py` (1,516 lines) is deleted and replaced with three new files. Five additional files are moved into `configurator/`. `project_utils.py` also moves to `configurator/` (not `services/`) to prevent a `configurator → services` layer violation.

**Files:**
- Create: `src/agent_tui/configurator/glyphs.py`
- Create: `src/agent_tui/configurator/settings.py`
- Create: `src/agent_tui/configurator/console.py`
- Move: `_version.py → version.py`, `_env_vars.py → env_vars.py`, `_debug.py → debug.py`, `theme.py`, `model_config.py`, `project_utils.py`
- Delete: `src/agent_tui/config.py`

#### What goes in each new file

**`configurator/glyphs.py`** — lines 215–430 from config.py plus `MAX_ARG_LENGTH` (line 497):
- `CharsetMode` (StrEnum)
- `@dataclass(frozen=True) class Glyphs`
- `UNICODE_GLYPHS = Glyphs(...)`
- `ASCII_GLYPHS = Glyphs(...)`
- `_glyphs_cache` module-level variable (initialized to `None`)
- `_detect_charset_mode() -> CharsetMode` — reads `os.environ` and `sys.stdout` only, no internal imports
- `get_glyphs() -> Glyphs`
- `reset_glyphs_cache() -> None`
- `is_ascii_mode() -> bool`
- `MAX_ARG_LENGTH: int = 150`

**`configurator/console.py`** — scattered sections from config.py:
- `_editable_cache` module-level variable (initialized to `None`)
- `_singleton_lock = threading.Lock()`
- `_git_branch_cache: dict[str, str | None] = {}`
- `_resolve_editable_info() -> tuple[bool, str | None]` — lines 319–354
- `_is_editable_install() -> bool` — line 357–365
- `_get_editable_install_path() -> str | None` — lines 368–374
- `_UNICODE_BANNER` (f-string constant) — lines 444–461
- `_ASCII_BANNER` (f-string constant) — lines 462–475
- `get_banner() -> str` — lines 478–494
- `_get_git_branch() -> str | None` — lines 513–542
- `_get_console() -> Console` — lines 1437–1458
- `__getattr__(name)` — handles `"console"` only

**`configurator/settings.py`** — the remainder of config.py:
- Threading locks: `_bootstrap_done`, `_bootstrap_lock`, `_singleton_lock`, `_bootstrap_start_path`
- `_find_dotenv_from_start_path()`, `_load_dotenv()`, `_ensure_bootstrap()` — lines 43–178
- `MODE_PREFIXES`, `MODE_DISPLAY_GLYPHS`, `PREFIX_TO_MODE` — lines 190–212
- `newline_shortcut() -> str` — lines 432–441
- `_ShellAllowAll`, `SHELL_ALLOW_ALL`, `parse_shell_allow_list()` — lines 543–613
- `_DEFAULT_CONFIG_DIR`, `_DEFAULT_CONFIG_PATH` — lines 616–617
- `_read_config_toml_skills_dirs()`, `_parse_extra_skills_dirs()` — lines 620–694
- `class Settings` — lines 696–1209
- `class SessionState` — lines 1210–1261
- `DANGEROUS_SHELL_PATTERNS`, `RECOMMENDED_SAFE_SHELL_COMMANDS` — lines 1262–1327
- `contains_dangerous_patterns()`, `is_shell_command_allowed()` — lines 1328–1423
- `get_default_coding_instructions()` — lines 1424–1436
- `_get_settings() -> Settings` — lines 1460–1487
- `__getattr__(name)` — handles `"settings"` only (not `"console"`)
- `build_langsmith_thread_url()` — lines 1510–1516

- [ ] **Step 1: Move the five configurator files and project_utils**

```bash
cd /home/shahriyarrzayev/REPOS/Learning_and_Development/agent-tui
git mv src/agent_tui/_version.py      src/agent_tui/configurator/version.py
git mv src/agent_tui/_env_vars.py     src/agent_tui/configurator/env_vars.py
git mv src/agent_tui/_debug.py        src/agent_tui/configurator/debug.py
git mv src/agent_tui/theme.py         src/agent_tui/configurator/theme.py
git mv src/agent_tui/model_config.py  src/agent_tui/configurator/model_config.py
git mv src/agent_tui/project_utils.py src/agent_tui/configurator/project_utils.py
git mv src/agent_tui/default_agent_prompt.md src/agent_tui/configurator/default_agent_prompt.md
git mv src/agent_tui/system_prompt.md src/agent_tui/configurator/system_prompt.md
# NOTE: if any code loads these files via Path(__file__).parent / "default_agent_prompt.md"
# (relative to app.py or main.py), move them to entrypoints/ instead and update the path.
```

- [ ] **Step 2: Create `src/agent_tui/configurator/glyphs.py`**

```python
"""Glyph constants and charset mode detection for agent-tui."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import StrEnum

_glyphs_cache: Glyphs | None = None
```

Then append the content of config.py lines 215–430 (CharsetMode through `reset_glyphs_cache` and `is_ascii_mode`) followed by:

```python
MAX_ARG_LENGTH = 150
"""Character limit for tool argument values in the UI."""
```

This file has zero internal `agent_tui` imports — `_detect_charset_mode` only reads `os.environ` and `sys.stdout`.

- [ ] **Step 3: Create `src/agent_tui/configurator/console.py`**

```python
"""Rich console, banners, and editable-install detection for agent-tui."""

from __future__ import annotations

import json
import logging
import subprocess  # noqa: S404
import threading
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import unquote, urlparse

from agent_tui.configurator.glyphs import _detect_charset_mode, CharsetMode
from agent_tui.configurator.version import __version__

if TYPE_CHECKING:
    from rich.console import Console
    console: Console

logger = logging.getLogger(__name__)

_editable_cache: tuple[bool, str | None] | None = None
_singleton_lock = threading.Lock()
_git_branch_cache: dict[str, str | None] = {}
```

Then append (copy unchanged from config.py):
- Lines 319–374: `_resolve_editable_info`, `_is_editable_install`, `_get_editable_install_path`
- Lines 444–494: `_UNICODE_BANNER`, `_ASCII_BANNER`, `get_banner`
- Lines 513–542: `_get_git_branch`
- Lines 1437–1458: `_get_console`

Then add the `__getattr__` for `console` only:

```python
def __getattr__(name: str) -> Console:
    """Lazy module attribute for `console`."""
    if name == "console":
        return _get_console()
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
```

- [ ] **Step 4: Create `src/agent_tui/configurator/settings.py`**

```python
"""Settings, environment loading, and shell safety for agent-tui."""

from __future__ import annotations

import json
import logging
import os
import re
import shlex
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from agent_tui.configurator.version import __version__  # noqa: F401 (re-exported)

if TYPE_CHECKING:
    from rich.console import Console
    settings: Settings
```

Then append (copy unchanged from config.py):
- Lines 27–40: thread locks and `_bootstrap_start_path`
- Lines 43–178: `_find_dotenv_from_start_path`, `_load_dotenv`, `_ensure_bootstrap`

  **Important:** inside `_ensure_bootstrap`, the lazy import reads:
  ```python
  from agent_tui.project_utils import get_server_project_context as _get_server_project_context
  ```
  Change this line to:
  ```python
  from agent_tui.configurator.project_utils import get_server_project_context as _get_server_project_context
  ```

- Lines 190–212: `MODE_PREFIXES`, `MODE_DISPLAY_GLYPHS`, `PREFIX_TO_MODE`
- Lines 432–441: `newline_shortcut`
- Lines 543–1261: `_ShellAllowAll`, `SHELL_ALLOW_ALL`, `parse_shell_allow_list`, config path constants, `Settings`, `SessionState`
- Lines 1262–1436: shell safety patterns and functions, `get_default_coding_instructions`
- Lines 1460–1487: `_get_settings`

Then add `__getattr__` for `settings` only:

```python
def __getattr__(name: str) -> Settings:
    """Lazy module attribute for `settings`."""
    if name == "settings":
        return _get_settings()
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
```

Then append:
- Lines 1510–1516: `build_langsmith_thread_url`

- [ ] **Step 5: Delete `config.py`**

```bash
git rm src/agent_tui/config.py
```

- [ ] **Step 6: Update internal imports within the new configurator files**

`configurator/debug.py` imports `_env_vars`:
```bash
sed -i 's/from agent_tui\._env_vars /from agent_tui.configurator.env_vars /g' src/agent_tui/configurator/debug.py
sed -i 's/agent_tui\._env_vars/agent_tui.configurator.env_vars/g' src/agent_tui/configurator/debug.py
```

`configurator/project_utils.py` imports `_env_vars`:
```bash
sed -i 's/from agent_tui\._env_vars /from agent_tui.configurator.env_vars /g' src/agent_tui/configurator/project_utils.py
sed -i 's/agent_tui\._env_vars/agent_tui.configurator.env_vars/g' src/agent_tui/configurator/project_utils.py
```

`configurator/update_check.py` and `configurator/skills/load.py` (still at their old path — will be updated in their own tasks):
No action needed here.

`configurator/theme.py` imports `_version` and `config`:
```bash
sed -i 's/from agent_tui\._version /from agent_tui.configurator.version /g' src/agent_tui/configurator/theme.py
sed -i 's/agent_tui\._version/agent_tui.configurator.version/g' src/agent_tui/configurator/theme.py
sed -i 's/from agent_tui\.config /from agent_tui.configurator.settings /g' src/agent_tui/configurator/theme.py
sed -i 's/agent_tui\.config\b/agent_tui.configurator.settings/g' src/agent_tui/configurator/theme.py
```

- [ ] **Step 7: Update all callers of `config.*` across the codebase**

Run these sed commands against all Python files in `src/` and `tests/`:

```bash
FILES=$(find src tests -name "*.py")

# config → glyphs (get_glyphs, Glyphs, is_ascii_mode, MAX_ARG_LENGTH)
# We can't do a blanket replacement of 'agent_tui.config' since different callers
# need different new modules. Instead, update each import line precisely.

# Files importing get_glyphs / Glyphs / is_ascii_mode from config → configurator.glyphs
for f in \
  src/agent_tui/services/clipboard.py \
  src/agent_tui/entrypoints/widgets/diff.py \
  src/agent_tui/entrypoints/widgets/loading.py \
  src/agent_tui/entrypoints/widgets/mcp_viewer.py \
  src/agent_tui/entrypoints/widgets/model_selector.py \
  src/agent_tui/entrypoints/widgets/notification_settings.py \
  src/agent_tui/entrypoints/widgets/status.py \
  src/agent_tui/entrypoints/widgets/theme_selector.py \
  src/agent_tui/entrypoints/widgets/welcome.py \
  src/agent_tui/entrypoints/widgets/approval.py \
  src/agent_tui/entrypoints/widgets/ask_user.py \
  src/agent_tui/entrypoints/widgets/chat_input.py \
  src/agent_tui/entrypoints/widgets/messages.py \
  src/agent_tui/entrypoints/widgets/thread_selector.py \
  src/agent_tui/entrypoints/app.py \
  src/agent_tui/services/tool_display.py; do
  sed -i 's/from agent_tui\.config import/from agent_tui.configurator.glyphs import/g' "$f" 2>/dev/null || true
done
```

**IMPORTANT:** The sed command above is a rough starting point only. Several files import **both** glyph things (`get_glyphs`, `is_ascii_mode`) **and** settings things (`settings`, `newline_shortcut`). For those files, after the blanket replacement you must manually split the import into two lines:

```python
# Before (single import, now wrong):
from agent_tui.config import get_glyphs, is_ascii_mode, settings

# After (two imports, correct):
from agent_tui.configurator.glyphs import get_glyphs, is_ascii_mode
from agent_tui.configurator.settings import settings
```

Specifically these files need manual two-line split:
- `src/agent_tui/entrypoints/app.py` — imports `is_ascii_mode`, `settings`, `_is_editable_install`, `build_langsmith_thread_url`, `newline_shortcut` from config. Split into three imports:
  ```python
  from agent_tui.configurator.glyphs import is_ascii_mode
  from agent_tui.configurator.settings import build_langsmith_thread_url, newline_shortcut, settings
  from agent_tui.configurator.console import _is_editable_install
  ```
- `src/agent_tui/entrypoints/widgets/chat_input.py` — check what it imports from config; split accordingly
- `src/agent_tui/entrypoints/widgets/thread_selector.py` — check what it imports from config; split accordingly
- `src/agent_tui/entrypoints/widgets/messages.py` — check what it imports from config; split accordingly
- `src/agent_tui/entrypoints/widgets/welcome.py` — check what it imports from config; split accordingly

Callers importing only `console`:
```bash
for f in \
  src/agent_tui/services/input.py \
  src/agent_tui/services/sessions.py; do
  sed -i 's/from agent_tui\.config import console/from agent_tui.configurator.console import console/g' "$f"
  sed -i 's/from agent_tui\.config import\(.*\)console/from agent_tui.configurator.console import console/g' "$f"
done
```

Callers importing only `settings`:
```bash
for f in \
  src/agent_tui/services/file_ops.py \
  src/agent_tui/services/tools.py \
  src/agent_tui/services/skills/invocation.py \
  src/agent_tui/entrypoints/main.py; do
  sed -i 's/from agent_tui\.config import settings/from agent_tui.configurator.settings import settings/g' "$f"
done
```

Callers importing `_is_editable_install`:
```bash
for f in \
  src/agent_tui/services/update_check.py; do
  sed -i 's/from agent_tui\.config import _is_editable_install/from agent_tui.configurator.console import _is_editable_install/g' "$f"
done
```

After all sed commands, grep to confirm zero remaining references to `agent_tui.config`:
```bash
grep -rn "from agent_tui\.config\b\|import agent_tui\.config\b" src/ tests/
```

Expected: no output.

- [ ] **Step 8: Update callers of the renamed single-file imports**

```bash
FILES=$(find src tests -name "*.py")

# _version → configurator.version
echo "$FILES" | xargs sed -i 's/from agent_tui\._version /from agent_tui.configurator.version /g'
echo "$FILES" | xargs sed -i 's/agent_tui\._version\b/agent_tui.configurator.version/g'

# _env_vars → configurator.env_vars
echo "$FILES" | xargs sed -i 's/from agent_tui\._env_vars /from agent_tui.configurator.env_vars /g'
echo "$FILES" | xargs sed -i 's/agent_tui\._env_vars\b/agent_tui.configurator.env_vars/g'

# _debug → configurator.debug
echo "$FILES" | xargs sed -i 's/from agent_tui\._debug /from agent_tui.configurator.debug /g'
echo "$FILES" | xargs sed -i 's/agent_tui\._debug\b/agent_tui.configurator.debug/g'

# theme → configurator.theme
echo "$FILES" | xargs sed -i 's/from agent_tui\.theme /from agent_tui.configurator.theme /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.theme\b/agent_tui.configurator.theme/g'

# model_config → configurator.model_config
echo "$FILES" | xargs sed -i 's/from agent_tui\.model_config /from agent_tui.configurator.model_config /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.model_config\b/agent_tui.configurator.model_config/g'

# project_utils → configurator.project_utils
echo "$FILES" | xargs sed -i 's/from agent_tui\.project_utils /from agent_tui.configurator.project_utils /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.project_utils\b/agent_tui.configurator.project_utils/g'
```

- [ ] **Step 9: Update `src/agent_tui/__init__.py`**

```python
"""Agent TUI - Terminal UI for agent interaction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from agent_tui.configurator.version import __version__

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = [
    "__version__",
    "cli_main",  # noqa: F822  # resolved lazily by __getattr__
]


def __getattr__(name: str) -> Callable[[], None]:
    """Lazy import for `cli_main`."""
    if name == "cli_main":
        from agent_tui.entrypoints.main import cli_main

        return cli_main
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
```

- [ ] **Step 10: Update `src/agent_tui/__main__.py`**

```python
"""Allow running the CLI as: python -m agent_tui."""

from agent_tui.entrypoints.main import cli_main

cli_main()
```

- [ ] **Step 11: Run tests**

```bash
uv run pytest tests/ -q
```

Expected: `23 passed`. If failures, read the error carefully — it will name the exact import that still references the old path.

- [ ] **Step 12: Commit**

```bash
git add -A
git commit -m "refactor: split config.py into configurator/glyphs, settings, console; move configurator files"
```

---

### Task 4: Move common/ files and update all callers

**Files:**
- Move: `src/agent_tui/{formatting,unicode_security,output}.py` → `src/agent_tui/common/`

- [ ] **Step 1: Move the three common files**

```bash
cd /home/shahriyarrzayev/REPOS/Learning_and_Development/agent-tui
git mv src/agent_tui/formatting.py      src/agent_tui/common/formatting.py
git mv src/agent_tui/unicode_security.py src/agent_tui/common/unicode_security.py
git mv src/agent_tui/output.py          src/agent_tui/common/output.py
```

- [ ] **Step 2: Update all callers**

```bash
FILES=$(find src tests -name "*.py")

echo "$FILES" | xargs sed -i 's/from agent_tui\.formatting /from agent_tui.common.formatting /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.formatting\b/agent_tui.common.formatting/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.unicode_security /from agent_tui.common.unicode_security /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.unicode_security\b/agent_tui.common.unicode_security/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.output /from agent_tui.common.output /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.output\b/agent_tui.common.output/g'
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest tests/ -q
```

Expected: `23 passed`

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: move formatting, unicode_security, output to common/"
```

---

### Task 5: Move services/ files and update all callers

**Files:**
- Move: `adapter.py`, `stub_agent.py`, `sessions.py`, `hooks.py`, `file_ops.py`, `media_utils.py`, `input.py`, `tool_display.py`, `tools.py`, `clipboard.py`, `editor.py`, `update_check.py`, `skills/` → `src/agent_tui/services/`

- [ ] **Step 1: Move all service files**

```bash
cd /home/shahriyarrzayev/REPOS/Learning_and_Development/agent-tui
git mv src/agent_tui/adapter.py     src/agent_tui/services/adapter.py
git mv src/agent_tui/stub_agent.py  src/agent_tui/services/stub_agent.py
git mv src/agent_tui/sessions.py    src/agent_tui/services/sessions.py
git mv src/agent_tui/hooks.py       src/agent_tui/services/hooks.py
git mv src/agent_tui/file_ops.py    src/agent_tui/services/file_ops.py
git mv src/agent_tui/media_utils.py src/agent_tui/services/media_utils.py
git mv src/agent_tui/input.py       src/agent_tui/services/input.py
git mv src/agent_tui/tool_display.py src/agent_tui/services/tool_display.py
git mv src/agent_tui/tools.py       src/agent_tui/services/tools.py
git mv src/agent_tui/clipboard.py   src/agent_tui/services/clipboard.py
git mv src/agent_tui/editor.py      src/agent_tui/services/editor.py
git mv src/agent_tui/update_check.py src/agent_tui/services/update_check.py
git mv src/agent_tui/skills         src/agent_tui/services/skills
```

- [ ] **Step 2: Update internal imports within moved service files**

Each service file that imports another service file needs updating. Run:

```bash
FILES=$(find src/agent_tui/services tests -name "*.py")

# adapter imports protocol (now domain)
echo "$FILES" | xargs sed -i 's/from agent_tui\.domain\.protocol/from agent_tui.domain.protocol/g'
# (already updated in task 2 — just verify)

# skills/invocation imports skills/load and config
sed -i 's/from agent_tui\.skills\./from agent_tui.services.skills./g' src/agent_tui/services/skills/invocation.py
sed -i 's/from agent_tui\.skills\b/from agent_tui.services.skills/g' src/agent_tui/services/skills/invocation.py
```

- [ ] **Step 3: Update all callers of service modules**

```bash
FILES=$(find src tests -name "*.py")

echo "$FILES" | xargs sed -i 's/from agent_tui\.adapter /from agent_tui.services.adapter /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.adapter\b/agent_tui.services.adapter/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.stub_agent /from agent_tui.services.stub_agent /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.stub_agent\b/agent_tui.services.stub_agent/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.sessions /from agent_tui.services.sessions /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.sessions\b/agent_tui.services.sessions/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.hooks /from agent_tui.services.hooks /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.hooks\b/agent_tui.services.hooks/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.file_ops /from agent_tui.services.file_ops /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.file_ops\b/agent_tui.services.file_ops/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.media_utils /from agent_tui.services.media_utils /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.media_utils\b/agent_tui.services.media_utils/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.input /from agent_tui.services.input /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.input\b/agent_tui.services.input/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.tool_display /from agent_tui.services.tool_display /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.tool_display\b/agent_tui.services.tool_display/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.tools /from agent_tui.services.tools /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.tools\b/agent_tui.services.tools/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.clipboard /from agent_tui.services.clipboard /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.clipboard\b/agent_tui.services.clipboard/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.editor /from agent_tui.services.editor /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.editor\b/agent_tui.services.editor/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.update_check /from agent_tui.services.update_check /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.update_check\b/agent_tui.services.update_check/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.skills\./from agent_tui.services.skills./g'
echo "$FILES" | xargs sed -i 's/from agent_tui\.skills /from agent_tui.services.skills /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.skills\b/agent_tui.services.skills/g'
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/ -q
```

Expected: `23 passed`

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move service files to agent_tui/services/"
```

---

### Task 6: Move entrypoints/ files and update all callers

**Files:**
- Move: `main.py`, `app.py`, `app.tcss`, `ui.py`, `widgets/` → `src/agent_tui/entrypoints/`
- Modify: `src/agent_tui/__init__.py`, `src/agent_tui/__main__.py` (already updated in Task 3 Step 9–10 — verify here)

- [ ] **Step 1: Move entrypoints files**

```bash
cd /home/shahriyarrzayev/REPOS/Learning_and_Development/agent-tui
git mv src/agent_tui/main.py   src/agent_tui/entrypoints/main.py
git mv src/agent_tui/app.py    src/agent_tui/entrypoints/app.py
git mv src/agent_tui/app.tcss  src/agent_tui/entrypoints/app.tcss
git mv src/agent_tui/ui.py     src/agent_tui/entrypoints/ui.py
git mv src/agent_tui/widgets   src/agent_tui/entrypoints/widgets
```

- [ ] **Step 2: Update internal imports within entrypoints files**

`entrypoints/app.py` has the most imports. It imports from services, configurator, domain, and common — all of which were updated by the sed runs in earlier tasks. Verify by checking for any remaining `from agent_tui\.(adapter|stub_agent|sessions|protocol|config|theme|...)` that haven't been updated:

```bash
grep -n "from agent_tui\." src/agent_tui/entrypoints/app.py | grep -v "from agent_tui\.\(domain\|configurator\|services\|common\|entrypoints\)\."
```

Expected: no output. If any appear, update them manually to the correct layer path.

`entrypoints/main.py` imports the app:
```bash
sed -i 's/from agent_tui\.app /from agent_tui.entrypoints.app /g' src/agent_tui/entrypoints/main.py
sed -i 's/agent_tui\.app\b/agent_tui.entrypoints.app/g' src/agent_tui/entrypoints/main.py
```

`entrypoints/ui.py` may import from config (now configurator) — check:
```bash
grep -n "from agent_tui\." src/agent_tui/entrypoints/ui.py
```

Update any remaining `from agent_tui.X` to the correct layer path.

All widget files' imports of each other (e.g. `from agent_tui.widgets.messages import ...`) need updating:
```bash
FILES=$(find src/agent_tui/entrypoints -name "*.py")
echo "$FILES" | xargs sed -i 's/from agent_tui\.widgets\./from agent_tui.entrypoints.widgets./g'
echo "$FILES" | xargs sed -i 's/agent_tui\.widgets\b/agent_tui.entrypoints.widgets/g'
```

- [ ] **Step 3: Update callers of entrypoints modules outside entrypoints/**

```bash
FILES=$(find src tests -name "*.py")

echo "$FILES" | xargs sed -i 's/from agent_tui\.app /from agent_tui.entrypoints.app /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.app\b/agent_tui.entrypoints.app/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.main /from agent_tui.entrypoints.main /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.main\b/agent_tui.entrypoints.main/g'

echo "$FILES" | xargs sed -i 's/from agent_tui\.ui /from agent_tui.entrypoints.ui /g'
echo "$FILES" | xargs sed -i 's/agent_tui\.ui\b/agent_tui.entrypoints.ui/g'
```

- [ ] **Step 4: Verify `__init__.py` and `__main__.py` reference entrypoints paths**

```bash
grep "entrypoints" src/agent_tui/__init__.py src/agent_tui/__main__.py
```

Expected output includes:
```
src/agent_tui/__init__.py:        from agent_tui.entrypoints.main import cli_main
src/agent_tui/__main__.py:from agent_tui.entrypoints.main import cli_main
```

If not, apply the content from Task 3 Steps 9–10.

- [ ] **Step 5: Confirm no stale `agent_tui.X` imports remain (X is a flat module name)**

```bash
grep -rn "from agent_tui\.\(app\|main\|ui\|adapter\|stub_agent\|sessions\|hooks\|file_ops\|media_utils\|input\|tool_display\|tools\|clipboard\|editor\|update_check\|skills\|formatting\|unicode_security\|output\|config\|theme\|_env_vars\|_version\|_debug\|model_config\|project_utils\|protocol\|command_registry\|mcp_tools\|_session_stats\|_ask_user_types\|_cli_context\)\b" src/ tests/
```

Expected: no output. If any appear, update them to the correct layer path.

- [ ] **Step 6: Run tests**

```bash
uv run pytest tests/ -q
```

Expected: `23 passed`

- [ ] **Step 7: Verify the TUI launches**

```bash
uv run python -c "
import asyncio
from agent_tui.entrypoints.app import AgentTuiApp
from agent_tui.services.stub_agent import StubAgent
app = AgentTuiApp(agent=StubAgent())
# run_test() runs a headless Textual app and returns immediately
result = asyncio.run(app.run_async(headless=True))
print('TUI launch: OK')
" 2>/dev/null || uv run python -c "from agent_tui.entrypoints.app import AgentTuiApp; print('Import OK')"
```

Expected: prints `Import OK` at minimum.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "refactor: move entrypoints files to agent_tui/entrypoints/"
```

---

### Task 7: Final verification

- [ ] **Step 1: Run the full test suite**

```bash
uv run pytest tests/ -q
```

Expected: `23 passed, 0 failed`

- [ ] **Step 2: Verify zero stale flat imports remain**

```bash
grep -rn "from agent_tui\.config\b" src/ tests/
```

Expected: no output.

```bash
grep -rn "from agent_tui\.\(app\|main\|ui\|adapter\|stub_agent\|sessions\|hooks\|file_ops\|media_utils\|input\|tool_display\|tools\|clipboard\|editor\|update_check\|skills\|formatting\|unicode_security\|output\|theme\|_env_vars\|_version\|_debug\|model_config\|project_utils\|protocol\|command_registry\|mcp_tools\|_session_stats\|_ask_user_types\|_cli_context\)\b" src/ tests/
```

Expected: no output.

- [ ] **Step 3: Verify layer rule — domain has no internal imports**

```bash
grep -rn "from agent_tui\." src/agent_tui/domain/
```

Expected: no output. Domain files are stdlib-only.

- [ ] **Step 4: Verify layer rule — common has no internal imports**

```bash
grep -rn "from agent_tui\." src/agent_tui/common/
```

Expected: no output. Common files are stdlib-only.

- [ ] **Step 5: Verify the CLI entry point works**

```bash
uv run agent-tui --help
```

Expected: prints the agent-tui help text without errors.

- [ ] **Step 6: Confirm final directory structure**

```bash
find src/agent_tui -name "*.py" | sort
```

Expected output (ordered):
```
src/agent_tui/__init__.py
src/agent_tui/__main__.py
src/agent_tui/common/__init__.py
src/agent_tui/common/formatting.py
src/agent_tui/common/output.py
src/agent_tui/common/unicode_security.py
src/agent_tui/configurator/__init__.py
src/agent_tui/configurator/console.py
src/agent_tui/configurator/debug.py
src/agent_tui/configurator/env_vars.py
src/agent_tui/configurator/glyphs.py
src/agent_tui/configurator/model_config.py
src/agent_tui/configurator/project_utils.py
src/agent_tui/configurator/settings.py
src/agent_tui/configurator/theme.py
src/agent_tui/configurator/version.py
src/agent_tui/domain/__init__.py
src/agent_tui/domain/ask_user_types.py
src/agent_tui/domain/cli_context.py
src/agent_tui/domain/command_registry.py
src/agent_tui/domain/mcp_tools.py
src/agent_tui/domain/protocol.py
src/agent_tui/domain/session_stats.py
src/agent_tui/entrypoints/__init__.py
src/agent_tui/entrypoints/app.py
src/agent_tui/entrypoints/main.py
src/agent_tui/entrypoints/ui.py
src/agent_tui/entrypoints/widgets/__init__.py
src/agent_tui/entrypoints/widgets/approval.py
src/agent_tui/entrypoints/widgets/ask_user.py
src/agent_tui/entrypoints/widgets/autocomplete.py
src/agent_tui/entrypoints/widgets/chat_input.py
src/agent_tui/entrypoints/widgets/diff.py
src/agent_tui/entrypoints/widgets/history.py
src/agent_tui/entrypoints/widgets/loading.py
src/agent_tui/entrypoints/widgets/mcp_viewer.py
src/agent_tui/entrypoints/widgets/messages.py
src/agent_tui/entrypoints/widgets/message_store.py
src/agent_tui/entrypoints/widgets/model_selector.py
src/agent_tui/entrypoints/widgets/notification_settings.py
src/agent_tui/entrypoints/widgets/status.py
src/agent_tui/entrypoints/widgets/theme_selector.py
src/agent_tui/entrypoints/widgets/thread_selector.py
src/agent_tui/entrypoints/widgets/tool_renderers.py
src/agent_tui/entrypoints/widgets/tool_widgets.py
src/agent_tui/entrypoints/widgets/welcome.py
src/agent_tui/entrypoints/widgets/_links.py
src/agent_tui/services/__init__.py
src/agent_tui/services/adapter.py
src/agent_tui/services/clipboard.py
src/agent_tui/services/editor.py
src/agent_tui/services/file_ops.py
src/agent_tui/services/hooks.py
src/agent_tui/services/input.py
src/agent_tui/services/media_utils.py
src/agent_tui/services/sessions.py
src/agent_tui/services/skills/__init__.py
src/agent_tui/services/skills/invocation.py
src/agent_tui/services/skills/load.py
src/agent_tui/services/stub_agent.py
src/agent_tui/services/tool_display.py
src/agent_tui/services/tools.py
src/agent_tui/services/update_check.py
```

- [ ] **Step 7: Final commit**

```bash
git add -A
git commit -m "chore: final verification — layered architecture complete"
```
