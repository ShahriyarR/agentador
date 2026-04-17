"""Interrupt overlay widget for HITL - using modal screen pattern."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, ClassVar

from textual.binding import Binding, BindingType
from textual.containers import Container, Vertical
from textual.content import Content
from textual.screen import ModalScreen
from textual.widgets import Static

if TYPE_CHECKING:
    from textual import events
    from textual.app import ComposeResult

from agent_tui.configurator import theme
from agent_tui.configurator.glyphs import get_glyphs

# Max length for argument value display
_ARG_TRUNCATE_LENGTH: int = 200


class InterruptOverlay(ModalScreen):
    """Modal overlay for interrupt-based tool execution approval.

    Displays tool information and provides approve/reject actions.
    Edit mode is currently a stub that falls through to approve.

    Key design decisions:
    - ModalScreen base for modal overlay behavior
    - BINDINGS for key handling (y, n, e)
    - Future-based result communication
    - Simple Static widgets for display
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("y", "approve", "Approve", show=False),
        Binding("n", "reject", "Reject", show=False),
        Binding("e", "edit", "Edit", show=False),
        Binding("1", "approve", "Approve (1)", show=False),
        Binding("2", "edit", "Edit (2)", show=False),
        Binding("3", "reject", "Reject (3)", show=False),
        Binding("escape", "reject", "Reject", show=False),
    ]

    CSS = """
    InterruptOverlay {
        align: center middle;
    }

    .interrupt-container {
        width: 80;
        height: auto;
        max-height: 50;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    .interrupt-title {
        text-align: center;
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
    }

    .interrupt-tool-info {
        margin-bottom: 1;
    }

    .interrupt-tool-name {
        text-style: bold;
        margin-bottom: 1;
    }

    .interrupt-args {
        color: $text-muted;
        margin-bottom: 1;
    }

    .interrupt-separator {
        margin: 1 0;
    }

    .interrupt-options {
        margin-top: 1;
    }

    .interrupt-option {
        padding: 0 1;
    }

    .interrupt-option-selected {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    .interrupt-help {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }

    .interrupt-edit-stub {
        text-align: center;
        color: $warning;
        text-style: italic;
        margin: 1 0;
    }
    """

    def __init__(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        tool_id: str,
        id: str | None = None,  # noqa: A002
        **kwargs: Any,
    ) -> None:
        """Initialize the InterruptOverlay.

        Args:
            tool_name: The name of the tool being requested
            tool_args: Dictionary of arguments for the tool call
            tool_id: Unique identifier for this tool call
            id: Optional widget ID
            **kwargs: Additional keyword arguments passed to ModalScreen
        """
        super().__init__(id=id, **kwargs)
        self._tool_name = tool_name
        self._tool_args = tool_args
        self._tool_id = tool_id
        self._future: asyncio.Future[dict[str, Any]] | None = None
        self._selected = 0  # 0 = approve, 1 = edit, 2 = reject
        self._option_widgets: list[Static] = []
        self._in_edit_mode = False

    def set_future(self, future: asyncio.Future[dict[str, Any]]) -> None:
        """Set the future to resolve when user decides."""
        self._future = future

    def compose(self) -> ComposeResult:
        """Compose the modal overlay content.

        Yields:
            Widgets for title, tool info, options, and help text.
        """
        with Container(classes="interrupt-container"):
            # Title
            glyphs = get_glyphs()
            title = Content.from_markup(
                f"{glyphs.warning} Tool Execution Requested",
            )
            yield Static(title, classes="interrupt-title")

            # Tool info section
            with Vertical(classes="interrupt-tool-info"):
                # Tool name
                yield Static(
                    Content.from_markup(f"[bold]Tool:[/bold] {self._tool_name}"),
                    classes="interrupt-tool-name",
                )

                # Tool args preview
                args_text = self._format_args(self._tool_args)
                yield Static(
                    Content.from_markup(f"[dim]{args_text}[/dim]"),
                    classes="interrupt-args",
                )

            # Separator
            yield Static("─" * 50, classes="interrupt-separator")

            # Options container
            with Container(classes="interrupt-options"):
                # Create option widgets
                for _ in range(3):  # approve, edit, reject
                    widget = Static("", classes="interrupt-option")
                    self._option_widgets.append(widget)
                    yield widget

            # Edit mode stub message (hidden by default)
            self._edit_stub_widget = Static(
                "[dim]Edit mode: Not yet implemented[/dim]",
                classes="interrupt-edit-stub",
            )
            self._edit_stub_widget.display = False
            yield self._edit_stub_widget

            # Help text at bottom
            glyphs = get_glyphs()
            help_text = f"[1] Approve (y) {glyphs.bullet} [2] Edit (e) {glyphs.bullet} [3] Reject (n)"
            yield Static(help_text, classes="interrupt-help")

    def _format_args(self, args: dict[str, Any]) -> str:
        """Format tool arguments for display.

        Args:
            args: Dictionary of tool arguments

        Returns:
            Formatted string for display, truncated if too long
        """
        if not args:
            return "No arguments"

        lines = []
        for key, value in args.items():
            value_str = str(value)
            if len(value_str) > _ARG_TRUNCATE_LENGTH:
                value_str = value_str[:_ARG_TRUNCATE_LENGTH] + "..."
            lines.append(f"  {key}: {value_str}")

        return "\n".join(lines)

    def on_mount(self) -> None:
        """Focus and update UI on mount."""
        self._update_options()
        self.focus()

    def _update_options(self) -> None:
        """Update option widgets based on selection."""
        options = [
            "[1] Approve (y)",
            "[2] Edit Args (e)",
            "[3] Reject (n)",
        ]

        for i, (text, widget) in enumerate(zip(options, self._option_widgets, strict=True)):
            prefix = "> " if i == self._selected else "  "
            widget.update(f"{prefix}{text}")

            # Update classes for styling
            widget.remove_class("interrupt-option-selected")
            if i == self._selected:
                widget.add_class("interrupt-option-selected")

    def action_approve(self) -> None:
        """Handle approve action (key: y or 1)."""
        self._resolve_decision("approve")

    def action_reject(self) -> None:
        """Handle reject action (key: n, 3, or Escape)."""
        self._resolve_decision("reject")

    def action_edit(self) -> None:
        """Handle edit action (key: e or 2).

        Currently a stub - shows "not implemented" message and falls
        through to approve after a brief delay.
        """
        self._selected = 1
        self._update_options()

        # Show edit stub message
        self._in_edit_mode = True
        self._edit_stub_widget.display = True

        # For now, edit falls through to approve
        # In the future, this would open an editable text area
        self._resolve_decision("edit", edited_args={})

    def _resolve_decision(self, action: str, edited_args: dict[str, Any] | None = None) -> None:
        """Resolve the future with the user's decision.

        Args:
            action: The user's decision ("approve", "edit", or "reject")
            edited_args: Optional edited arguments (only for "edit" action)
        """
        result: dict[str, Any] = {"action": action}
        if edited_args is not None:
            result["edited_args"] = edited_args

        # Resolve the future
        if self._future and not self._future.done():
            self._future.set_result(result)

        # Dismiss the modal
        self.dismiss(result)

    def on_blur(self, event: events.Blur) -> None:  # noqa: ARG002
        """Re-focus on blur to keep focus trapped until decision is made."""
        self.call_after_refresh(self.focus)
