"""Canonical registry of `AGENT_TUI_*` environment variables.

Every env var the CLI reads whose name starts with `AGENT_TUI_` must
be defined here as a module-level constant.  A drift-detection test
(`tests/unit_tests/test_env_vars.py`) fails when a bare string literal
like `"AGENT_TUI_FOO"` appears in source code instead of a constant
imported from this module.

Import the short-name constants (e.g. `AUTO_UPDATE`, `DEBUG`) and pass them
to `os.environ.get()` instead of using raw string literals. If the env var is
ever renamed, only the value here changes.

!!! note

    `resolve_env_var` also supports a dynamic prefix override for API keys
    and provider credentials: setting `AGENT_TUI_{NAME}` takes priority
    over `{NAME}`.  For example, `AGENT_TUI_OPENAI_API_KEY` overrides
    `OPENAI_API_KEY`. Only call sites that use `resolve_env_var` benefit from
    this -- direct `os.environ.get` lookups (like the constants below) do not.
    Dynamic overrides are not listed here because they mirror third-party
    variable names.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Constants — import these instead of bare string literals.
# Keep alphabetically sorted by constant name.
# ---------------------------------------------------------------------------

AUTO_UPDATE = "AGENT_TUI_AUTO_UPDATE"
"""Enable automatic CLI updates ('1', 'true', or 'yes')."""

DEBUG = "AGENT_TUI_DEBUG"
"""Enable verbose debug logging to a file."""

DEBUG_FILE = "AGENT_TUI_DEBUG_FILE"
"""Path for the debug log file (default: `/tmp/deepagents_debug.log`)."""

EXTRA_SKILLS_DIRS = "AGENT_TUI_EXTRA_SKILLS_DIRS"
"""Colon-separated paths added to the skill containment allowlist."""

LANGSMITH_PROJECT = "AGENT_TUI_LANGSMITH_PROJECT"
"""Override LangSmith project name for agent traces."""

NO_UPDATE_CHECK = "AGENT_TUI_NO_UPDATE_CHECK"
"""Disable automatic update checking when set."""

SERVER_ENV_PREFIX = "AGENT_TUI_SERVER_"
"""Environment variable prefix used to pass CLI config to the server subprocess."""

SHELL_ALLOW_LIST = "AGENT_TUI_SHELL_ALLOW_LIST"
"""Comma-separated shell commands to allow (or 'recommended'/'all')."""

USER_ID = "AGENT_TUI_USER_ID"
"""Attach a user identifier to LangSmith trace metadata."""
