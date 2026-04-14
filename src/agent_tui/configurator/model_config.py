"""Stub module: model_config.

All symbols here are no-ops that keep the rest of the codebase importable
without the original deepagents model-configuration stack.  Functions that
previously read/wrote ``~/.agent-tui/config.toml`` now return safe defaults
or do nothing.

TODO(Task 21+): Replace stubs with real implementations once the scaffold has
a config story.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

DEFAULT_CONFIG_PATH: Path = Path.home() / ".agent-tui" / "config.toml"

# ---------------------------------------------------------------------------
# ModelSpec
# ---------------------------------------------------------------------------


@dataclass
class ModelSpec:
    """Minimal stand-in for the original ModelSpec dataclass."""

    provider: str | None
    model: str

    @classmethod
    def try_parse(cls, spec: str) -> "ModelSpec | None":
        """Parse ``provider:model`` format.  Returns ``None`` on failure."""
        if ":" in spec:
            provider, _, model = spec.partition(":")
            if provider and model:
                return cls(provider=provider, model=model)
        return None


# ---------------------------------------------------------------------------
# ThreadConfig
# ---------------------------------------------------------------------------


@dataclass
class _ThreadConfig:
    columns: dict[str, bool] = field(
        default_factory=lambda: {
            "thread_id": True,
            "agent_name": False,
            "messages": False,
            "created_at": False,
            "updated_at": True,
            "git_branch": False,
            "cwd": False,
            "initial_prompt": False,
        }
    )


# ---------------------------------------------------------------------------
# Stub functions
# ---------------------------------------------------------------------------


def clear_caches() -> None:
    """No-op stub: no caches to clear in standalone mode."""


def is_warning_suppressed(  # noqa: ARG001
    key: str,
    config_path: "Path | None" = None,  # noqa: ARG001
) -> bool:
    """Stub: returns False (no warnings suppressed by default)."""
    return False


def get_available_models() -> list[Any]:
    """Stub: returns empty list."""
    return []


def get_model_profiles(*, cli_override: Any = None) -> list[Any]:  # noqa: ARG001
    """Stub: returns empty list."""
    return []


def get_credential_env_var(provider: str | None) -> str | None:  # noqa: ARG001
    """Stub: returns None."""
    return None


def has_provider_credentials(provider: str | None) -> bool | None:  # noqa: ARG001
    """Stub: returns None (unknown)."""
    return None


def save_recent_model(model_spec: str) -> None:  # noqa: ARG001
    """Stub: no-op."""


def save_default_model(model_spec: str) -> bool:  # noqa: ARG001
    """Stub: returns False (config writes not supported)."""
    return False


def clear_default_model() -> bool:
    """Stub: returns False (config writes not supported)."""
    return False


def load_thread_config() -> _ThreadConfig:
    """Stub: returns default thread display config."""
    return _ThreadConfig()


def load_thread_relative_time() -> bool:
    """Stub: returns False (use absolute timestamps)."""
    return False


def load_thread_sort_order() -> str:
    """Stub: returns 'updated_at' (sort by most recently updated)."""
    return "updated_at"
