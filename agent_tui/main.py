"""Main entry point and CLI for agent-tui (TUI-only)."""

import argparse
import logging
import os
import sys
from typing import Any

from agent_tui._version import __version__

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Agent TUI - Terminal User Interface for AI Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"agent-tui {__version__}",
    )

    return parser.parse_args()


def cli_main() -> None:
    """Entry point for console script."""
    # Fix for gRPC fork issue on macOS
    # https://github.com/grpc/grpc/issues/37642
    if sys.platform == "darwin":
        os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "0"

    # Note: LANGSMITH_PROJECT override is handled lazily by config.py's
    # _ensure_bootstrap() (triggered on first access of `settings`).
    # This ensures agent traces use AGENT_TUI_LANGSMITH_PROJECT while
    # shell commands use the user's original LANGSMITH_PROJECT.

    # Fast path: print version without loading heavy dependencies
    if len(sys.argv) == 2 and sys.argv[1] in {"-v", "--version"}:  # noqa: PLR2004
        print(f"agent-tui {__version__}")  # noqa: T201
        sys.exit(0)

    try:
        _args = parse_args()

        # Bootstrap config (triggers _ensure_bootstrap via settings access)
        from agent_tui.config import settings  # noqa: F401

        from agent_tui.app import DeepAgentsApp
        from agent_tui.stub_agent import StubAgent

        agent = StubAgent()
        app = DeepAgentsApp(agent=agent)
        app.run()

    except KeyboardInterrupt:
        # Clean exit on Ctrl+C — suppress ugly traceback.
        sys.stderr.write("\n\nInterrupted\n")
        sys.exit(0)


if __name__ == "__main__":
    cli_main()
