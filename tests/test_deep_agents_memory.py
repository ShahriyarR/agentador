"""Tests for DeepAgents memory helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_tui.services.deep_agents.memory import (
    get_memory_sources,
    get_memory_summary,
    read_memory_content,
)


class TestGetMemorySources:
    """Tests for get_memory_sources()."""

    def test_returns_empty_list_when_neither_file_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert get_memory_sources() == []

    def test_returns_user_level_path_when_it_exists(self, tmp_path, monkeypatch, mock_home):
        monkeypatch.chdir(tmp_path)
        (mock_home / ".deepagents").mkdir()
        (mock_home / ".deepagents" / "AGENTS.md").write_text("user memory")

        sources = get_memory_sources()
        assert "~/.deepagents/AGENTS.md" in sources

    def test_returns_project_level_path_when_it_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "AGENTS.md").write_text("project memory")

        sources = get_memory_sources()
        assert ".deepagents/AGENTS.md" in sources

    def test_returns_both_paths_when_both_exist(self, tmp_path, monkeypatch, mock_home):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "AGENTS.md").write_text("project memory")
        (mock_home / ".deepagents").mkdir()
        (mock_home / ".deepagents" / "AGENTS.md").write_text("user memory")

        sources = get_memory_sources()
        assert "~/.deepagents/AGENTS.md" in sources
        assert ".deepagents/AGENTS.md" in sources
        assert sources.index("~/.deepagents/AGENTS.md") < sources.index(".deepagents/AGENTS.md")

    def test_returns_paths_as_posix_strings(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "AGENTS.md").write_text("project memory")

        sources = get_memory_sources()
        assert isinstance(sources, list)
        assert all(isinstance(s, str) for s in sources)
        assert all("/" in s for s in sources)  # POSIX strings use forward slashes


class TestReadMemoryContent:
    """Tests for read_memory_content()."""

    def test_returns_empty_dict_when_no_sources(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert read_memory_content() == {}

    def test_reads_project_level_file_content(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "AGENTS.md").write_text("project memory content")

        content = read_memory_content()
        assert ".deepagents/AGENTS.md" in content
        assert content[".deepagents/AGENTS.md"] == "project memory content"

    def test_reads_user_level_file_content(self, tmp_path, monkeypatch, mock_home):
        (mock_home / ".deepagents").mkdir()
        (mock_home / ".deepagents" / "AGENTS.md").write_text("user memory content")

        content = read_memory_content()
        assert "~/.deepagents/AGENTS.md" in content
        assert content["~/.deepagents/AGENTS.md"] == "user memory content"

    def test_reads_both_files_when_both_exist(self, tmp_path, monkeypatch, mock_home):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "AGENTS.md").write_text("project memory")
        (mock_home / ".deepagents").mkdir()
        (mock_home / ".deepagents" / "AGENTS.md").write_text("user memory")

        content = read_memory_content()
        assert len(content) == 2
        assert content["~/.deepagents/AGENTS.md"] == "user memory"
        assert content[".deepagents/AGENTS.md"] == "project memory"

    def test_skips_unreadable_files_silently(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "AGENTS.md").write_text("project memory")

        original_read_text = Path.read_text

        def mock_read_text(self, *args, **kwargs):
            if str(self).endswith("AGENTS.md"):
                raise OSError("Permission denied")
            return original_read_text(self, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", mock_read_text)
        assert read_memory_content() == {}

    def test_uses_utf8_encoding(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        test_content = "Memory: 你好 мир 🚀"
        (tmp_path / ".deepagents" / "AGENTS.md").write_text(test_content, encoding="utf-8")

        content = read_memory_content()
        assert content[".deepagents/AGENTS.md"] == test_content


class TestGetMemorySummary:
    """Tests for get_memory_summary()."""

    def test_returns_no_files_message_when_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        summary = get_memory_summary()
        assert summary == "No AGENTS.md files found. Create ~/.deepagents/AGENTS.md to add persistent memory."

    def test_includes_source_count_and_line_counts(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "AGENTS.md").write_text("line1\nline2\nline3")

        summary = get_memory_summary()
        assert "Memory loaded from 1 source(s):" in summary
        assert ".deepagents/AGENTS.md (3 lines)" in summary

    def test_lists_multiple_sources_with_line_counts(self, tmp_path, monkeypatch, mock_home):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "AGENTS.md").write_text("\n".join(["line"] * 8))
        (mock_home / ".deepagents").mkdir()
        (mock_home / ".deepagents" / "AGENTS.md").write_text("\n".join(["line"] * 42))

        summary = get_memory_summary()
        assert "Memory loaded from 2 source(s):" in summary
        assert "~/.deepagents/AGENTS.md (42 lines)" in summary
        assert ".deepagents/AGENTS.md (8 lines)" in summary

    def test_handles_single_line_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "AGENTS.md").write_text("single line")

        summary = get_memory_summary()
        assert ".deepagents/AGENTS.md (1 line)" in summary

    def test_handles_empty_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "AGENTS.md").write_text("")

        summary = get_memory_summary()
        assert ".deepagents/AGENTS.md (0 lines)" in summary

    def test_handles_multiline_with_trailing_newline(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "AGENTS.md").write_text("line1\nline2\n")

        summary = get_memory_summary()
        assert ".deepagents/AGENTS.md (2 lines)" in summary
