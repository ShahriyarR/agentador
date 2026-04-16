#!/usr/bin/env python3
"""CLI runner for E2E tests with multiple execution modes."""

from __future__ import annotations

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Run E2E tests for agent-tui")
    parser.add_argument(
        "--pilot-only",
        action="store_true",
        help="Run only fast pilot tests (default: deepagents backend)",
    )
    parser.add_argument(
        "--pty-only",
        action="store_true",
        help="Run only PTY terminal tests",
    )
    parser.add_argument(
        "--agent",
        choices=["stub", "deepagents"],
        default="deepagents",
        help="Agent backend to use (default: deepagents)",
    )
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Additional arguments to pass to pytest",
    )
    args = parser.parse_args()

    import subprocess

    pytest_args = ["uv", "run", "pytest", "tests/e2e/"]

    if args.pilot_only:
        pytest_args = ["uv", "run", "pytest", "tests/e2e/pilot_tests/"]
    elif args.pty_only:
        pytest_args = ["uv", "run", "pytest", "tests/e2e/pty_tests/"]
    else:
        pass

    env = None
    if args.agent == "stub":
        import os

        env = os.environ.copy()
        env["AGENT_TUI_E2E_AGENT"] = "stub"

    pytest_args.extend(args.pytest_args)

    if "-v" not in pytest_args:
        pytest_args.append("-v")

    result = subprocess.run(pytest_args, env=env)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
