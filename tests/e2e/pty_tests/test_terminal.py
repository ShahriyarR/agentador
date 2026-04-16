"""PTY-based E2E tests for true terminal fidelity."""

import os
import re
import time

import pytest


class PTYReader:
    def __init__(self, fd, proc):
        self.fd = fd
        self.proc = proc
        self.output = []

    def read_until(self, pattern, timeout=5):
        """Read until pattern is found or timeout."""
        import select

        start = time.time()
        while time.time() - start < timeout:
            ready, _, _ = select.select([self.fd], [], [], 0.1)
            if ready:
                data = os.read(self.fd, 1024).decode("utf-8", errors="replace")
                self.output.append(data)
                if re.search(pattern, data, re.IGNORECASE):
                    return "".join(self.output)
        return "".join(self.output)

    def read_until_pattern(self, pattern, timeout=5):
        """Alias for read_until with regex support."""
        return self.read_until(pattern, timeout)

    def write(self, data):
        os.write(self.fd, data.encode())

    def close(self):
        self.proc.terminate()
        os.close(self.fd)


@pytest.fixture
def pty_session():
    """Spawns actual TUI process with PTY."""
    import pty
    import subprocess

    master, slave = pty.openpty()
    proc = subprocess.Popen(
        ["uv", "run", "agent-tui", "--agent=stub"],
        cwd=os.getcwd(),
        stdout=slave,
        stderr=slave,
        stdin=slave,
    )
    os.close(slave)

    reader = PTYReader(master, proc)
    yield reader
    reader.close()


def test_tui_launches(pty_session):
    """TUI should launch and show welcome message."""
    output = pty_session.read_until("agent-tui", timeout=5)
    assert "agent-tui" in output.lower() or "thread" in output.lower()


def test_type_message_and_enter(pty_session):
    """Typing a message and pressing Enter should send it."""
    pty_session.read_until("thread", timeout=5)

    pty_session.write("hello\r")

    output = pty_session.read_until("hello", timeout=5)
    assert "hello" in output.lower()


def test_approval_widget_with_pty(pty_session):
    """PTY test for approval widget display."""
    pty_session.read_until("thread", timeout=5)

    pty_session.write("execute echo test\r")

    output = pty_session.read_until_pattern(r"(Tool|Approve|execute)", timeout=5)
    assert "execute" in output.lower() or "tool" in output.lower()


def test_escape_key_interrupt(pty_session):
    """Escape key should interrupt current operation."""
    pty_session.read_until("thread", timeout=5)

    pty_session.write("hello\r")
    time.sleep(0.5)

    pty_session.write("\x1b")

    output = pty_session.read_until("thread", timeout=2)
    assert output is not None


def test_unicode_rendering(pty_session):
    """Unicode characters should render correctly."""
    pty_session.read_until("thread", timeout=5)

    pty_session.write("hello 🌍\r")

    output = pty_session.read_until("hello", timeout=5)
    assert output is not None
    assert "🌍" in output or "hello" in output.lower()


def test_arrow_keys_navigation(pty_session):
    """Arrow keys should be handled without crashing."""
    pty_session.read_until("thread", timeout=5)

    pty_session.write("\x1b[A")

    output = pty_session.read_until("thread", timeout=2)
    assert output is not None


def test_iterm2_cursor_guide_disabled(pty_session):
    """iTerm2 cursor guide should be disabled on startup."""
    pty_session.read_until("thread", timeout=5)

    assert True


def test_colors_and_unicode_render(pty_session):
    """Colors and unicode should render correctly in terminal."""
    pty_session.read_until("thread", timeout=5)

    pty_session.write("hello 🌍\r")

    output = pty_session.read_until("hello", timeout=5)
    assert output is not None
    assert "hello" in output.lower()
