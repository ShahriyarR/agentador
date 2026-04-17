"""Tests for DeepAgents skills helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_tui.services.deep_agents.skills import (
    get_skill_sources,
    list_available_skills,
)


class TestGetSkillSources:
    """Tests for get_skill_sources()."""

    def test_returns_empty_list_when_neither_directory_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert get_skill_sources() == []

    def test_returns_user_level_path_when_it_exists(self, tmp_path, monkeypatch, mock_home):
        monkeypatch.chdir(tmp_path)
        (mock_home / ".deepagents").mkdir()
        (mock_home / ".deepagents" / "skills").mkdir()

        sources = get_skill_sources()
        assert "~/.deepagents/skills" in sources

    def test_returns_project_level_path_when_it_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()

        sources = get_skill_sources()
        assert ".deepagents/skills" in sources

    def test_returns_both_paths_when_both_exist(self, tmp_path, monkeypatch, mock_home):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (mock_home / ".deepagents").mkdir()
        (mock_home / ".deepagents" / "skills").mkdir()

        sources = get_skill_sources()
        assert "~/.deepagents/skills" in sources
        assert ".deepagents/skills" in sources
        assert sources.index("~/.deepagents/skills") < sources.index(".deepagents/skills")

    def test_returns_paths_as_posix_strings(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()

        sources = get_skill_sources()
        assert isinstance(sources, list)
        assert all(isinstance(s, str) for s in sources)
        assert all("/" in s for s in sources)  # POSIX strings use forward slashes

    def test_ignores_files_and_only_returns_directories(self, tmp_path, monkeypatch, mock_home):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").write_text("not a directory")
        (mock_home / ".deepagents").mkdir()
        (mock_home / ".deepagents" / "skills").mkdir()

        sources = get_skill_sources()
        # Project-level is a file, so should not be included
        assert "~/.deepagents/skills" in sources
        assert ".deepagents/skills" not in sources


class TestListAvailableSkills:
    """Tests for list_available_skills()."""

    def test_returns_empty_list_when_sources_is_empty(self):
        assert list_available_skills([]) == []

    def test_returns_empty_list_when_no_md_files_in_sources(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()

        skills = list_available_skills([".deepagents/skills/"])
        assert skills == []

    def test_finds_md_files_and_extracts_name_from_stem(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "web-search.md").write_text("# Web Search\nSearch the web")

        skills = list_available_skills([".deepagents/skills/"])
        assert len(skills) == 1
        assert skills[0]["name"] == "web-search"

    def test_extracts_description_from_first_non_heading_line(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "search.md").write_text(
            "# Search\n# Subtitle\nThis is the description"
        )

        skills = list_available_skills([".deepagents/skills/"])
        assert len(skills) == 1
        assert skills[0]["description"] == "This is the description"

    def test_returns_empty_description_when_file_is_all_headings(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "analyze.md").write_text("# Analyze\n## Code\n### Analysis")

        skills = list_available_skills([".deepagents/skills/"])
        assert len(skills) == 1
        assert skills[0]["name"] == "analyze"
        assert skills[0]["description"] == ""

    def test_returns_empty_description_when_file_is_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "empty.md").write_text("")

        skills = list_available_skills([".deepagents/skills/"])
        assert len(skills) == 1
        assert skills[0]["name"] == "empty"
        assert skills[0]["description"] == ""

    def test_skips_unreadable_files_silently(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "readable.md").write_text("Readable skill")
        (tmp_path / ".deepagents" / "skills" / "unreadable.md").write_text("Unreadable")

        original_read_text = Path.read_text

        def mock_read_text(self, *args, **kwargs):
            if str(self).endswith("unreadable.md"):
                raise OSError("Permission denied")
            return original_read_text(self, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", mock_read_text)
        skills = list_available_skills([".deepagents/skills/"])
        # Should only have the readable one
        assert len(skills) == 1
        assert skills[0]["name"] == "readable"

    def test_returns_results_sorted_by_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "zebra.md").write_text("Zebra skill")
        (tmp_path / ".deepagents" / "skills" / "apple.md").write_text("Apple skill")
        (tmp_path / ".deepagents" / "skills" / "middle.md").write_text("Middle skill")

        skills = list_available_skills([".deepagents/skills/"])
        assert len(skills) == 3
        assert [s["name"] for s in skills] == ["apple", "middle", "zebra"]

    def test_handles_multiple_sources(self, tmp_path, monkeypatch, mock_home):
        monkeypatch.chdir(tmp_path)
        # User-level skills
        (mock_home / ".deepagents").mkdir()
        (mock_home / ".deepagents" / "skills").mkdir()
        (mock_home / ".deepagents" / "skills" / "user-skill.md").write_text("User skill")
        # Project-level skills
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "project-skill.md").write_text("Project skill")

        skills = list_available_skills(["~/.deepagents/skills", ".deepagents/skills"])
        assert len(skills) == 2
        names = [s["name"] for s in skills]
        assert "user-skill" in names
        assert "project-skill" in names

    def test_handles_duplicate_skills_from_multiple_sources(self, tmp_path, monkeypatch, mock_home):
        """When same skill exists in multiple sources, last one wins."""
        monkeypatch.chdir(tmp_path)
        # User-level skill
        (mock_home / ".deepagents").mkdir()
        (mock_home / ".deepagents" / "skills").mkdir()
        (mock_home / ".deepagents" / "skills" / "search.md").write_text("User search description")
        # Project-level skill (same name)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "search.md").write_text("Project search description")

        skills = list_available_skills(["~/.deepagents/skills", ".deepagents/skills"])
        assert len(skills) == 1
        assert skills[0]["name"] == "search"
        assert skills[0]["description"] == "Project search description"

    def test_ignores_non_md_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "skill.md").write_text("Real skill")
        (tmp_path / ".deepagents" / "skills" / "notskill.txt").write_text("Not a skill")
        (tmp_path / ".deepagents" / "skills" / "readme").write_text("Also not")

        skills = list_available_skills([".deepagents/skills/"])
        assert len(skills) == 1
        assert skills[0]["name"] == "skill"

    def test_handles_utf8_encoded_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "unicode.md").write_text(
            "Skill: 你好 мир 🚀", encoding="utf-8"
        )

        skills = list_available_skills([".deepagents/skills/"])
        assert len(skills) == 1
        assert skills[0]["description"] == "Skill: 你好 мир 🚀"

    def test_skips_subdirectories_non_recursive(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "top-level.md").write_text("Top level")
        (tmp_path / ".deepagents" / "skills" / "subdir").mkdir()
        (tmp_path / ".deepagents" / "skills" / "subdir" / "nested.md").write_text("Nested")

        skills = list_available_skills([".deepagents/skills/"])
        assert len(skills) == 1
        assert skills[0]["name"] == "top-level"

    def test_trims_whitespace_from_description(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "whitespace.md").write_text(
            "# Title\n   This has leading spaces   \nMore text"
        )

        skills = list_available_skills([".deepagents/skills/"])
        assert len(skills) == 1
        assert skills[0]["description"] == "This has leading spaces"

    def test_skips_empty_lines_to_find_first_non_heading(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "multiline.md").write_text(
            "# Title\n\n\nThis is the actual description\n# Another heading"
        )

        skills = list_available_skills([".deepagents/skills/"])
        assert len(skills) == 1
        assert skills[0]["description"] == "This is the actual description"

    def test_handles_heading_with_spaces(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "heading.md").write_text(
            "#   Title with spaces   \nDescription here"
        )

        skills = list_available_skills([".deepagents/skills/"])
        assert len(skills) == 1
        assert skills[0]["description"] == "Description here"

    def test_handles_nonexistent_source_path_silently(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        skills = list_available_skills([".deepagents/skills/"])
        assert skills == []

    def test_returns_list_of_dicts_with_name_and_description(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".deepagents").mkdir()
        (tmp_path / ".deepagents" / "skills").mkdir()
        (tmp_path / ".deepagents" / "skills" / "test.md").write_text("Test description")

        skills = list_available_skills([".deepagents/skills/"])
        assert isinstance(skills, list)
        assert len(skills) == 1
        skill = skills[0]
        assert isinstance(skill, dict)
        assert set(skill.keys()) == {"name", "description"}
        assert isinstance(skill["name"], str)
        assert isinstance(skill["description"], str)
