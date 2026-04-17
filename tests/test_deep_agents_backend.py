"""Tests for DeepAgents backend."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agent_tui.services.deep_agents.backend import create_store


class TestCreateStore:
    def test_returns_in_memory_store_instance(self):
        mock_store = MagicMock()
        with patch("langgraph.store.memory.InMemoryStore", return_value=mock_store) as MockStore:
            result = create_store()
        MockStore.assert_called_once()
        assert result is mock_store

    def test_creates_new_store_each_call(self):
        """create_store() always returns a fresh instance — callers must cache the result.

        The adapter reuses the store across model switches via the
        ``if self._store is None`` guard in _ensure_agent().  This test
        confirms the contract: create_store() itself provides no caching, so
        the guard is necessary and sufficient for store reuse.
        """
        mock1, mock2 = MagicMock(), MagicMock()
        with patch("langgraph.store.memory.InMemoryStore", side_effect=[mock1, mock2]):
            r1 = create_store()
            r2 = create_store()
        assert r1 is mock1
        assert r2 is mock2
