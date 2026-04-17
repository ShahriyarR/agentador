"""DeepAgents skills helpers — skill directory discovery and listing."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def get_skill_sources() -> list[str]:
    """Return a list of skill directory paths that exist on disk, as POSIX path strings.

    Checks these paths in order:
    1. ~/.deepagents/skills (user-level)
    2. ./.deepagents/skills (project-level, relative to cwd)

    Only includes paths that exist as directories.

    Returns:
        List of POSIX path strings for existing skill directories.
        Empty list if none exist.
    """
    sources = []
    candidates = [
        "~/.deepagents/skills",
        "./.deepagents/skills",
    ]

    for candidate in candidates:
        path = Path(candidate).expanduser().resolve()
        if path.is_dir():
            sources.append(Path(candidate).as_posix())

    return sources


def list_available_skills(sources: list[str]) -> list[dict[str, Any]]:
    """Scan skill directories for available skills.

    For each source directory, scans for .md files (non-recursive, top level only).
    For each .md file found:
    - name: the filename stem (e.g. "web-search" from "web-search.md")
    - description: extract from the first non-empty line that is NOT a markdown heading
      (doesn't start with #). If all lines are headings or the file is empty, use "".

    Args:
        sources: List of skill directory paths as POSIX strings.

    Returns:
        List of dicts with name and description, sorted by name.
        Empty list if no sources or no skills found.
        Skips unreadable files silently.
    """
    skills: dict[str, dict[str, Any]] = {}

    for source in sources:
        try:
            source_path = Path(source).expanduser().resolve()
            if not source_path.is_dir():
                continue

            # Find all .md files in the directory (non-recursive)
            for md_file in source_path.glob("*.md"):
                if not md_file.is_file():
                    continue

                skill_name = md_file.stem
                description = ""

                try:
                    content = md_file.read_text(encoding="utf-8")
                    # Find first non-empty line that is not a heading
                    for line in content.splitlines():
                        stripped = line.strip()
                        if stripped and not stripped.startswith("#"):
                            description = stripped
                            break
                except (OSError, ValueError):
                    # OSError: permission denied or missing; ValueError: invalid encoding.
                    # continue skips the dict assignment below — no entry added for this file.
                    continue

                skills[skill_name] = {"name": skill_name, "description": description}

        except (OSError, ValueError):
            # Skip directories that can't be read
            continue

    # Sort by name and return as list
    return sorted(skills.values(), key=lambda s: s["name"])
