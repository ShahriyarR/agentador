"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def mock_home(tmp_path, monkeypatch):
    """Create a fake home directory and patch Path.expanduser to use it."""
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    original = Path.expanduser

    def _expand(self):
        if self.parts and self.parts[0] == "~":
            rest = self.parts[1:]
            return home_dir / Path(*rest) if rest else home_dir
        return original(self)

    monkeypatch.setattr(Path, "expanduser", _expand)
    return home_dir
