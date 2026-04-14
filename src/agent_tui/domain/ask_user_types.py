"""Lightweight types for the ask-user interrupt protocol.

Extracted from `ask_user` so `textual_adapter` can import `AskUserRequest` at
module level — and `app` can reference the types at type-check time — without
pulling in the langchain middleware stack.
"""

from __future__ import annotations

from typing import Literal, NotRequired

from typing_extensions import TypedDict


class Choice(TypedDict):
    """A single choice option for a multiple choice question."""

    value: str  # The display label for this choice.


class Question(TypedDict):
    """A question to ask the user."""

    question: str  # The question text to display.

    type: Literal["text", "multiple_choice"]
    # 'text' for free-form input, 'multiple_choice' for predefined options.

    choices: NotRequired[list[Choice]]
    # Options for multiple_choice questions. An 'Other' free-form option is
    # always appended automatically.

    required: NotRequired[bool]
    # Whether the user must answer. Defaults to true if omitted.


class AskUserRequest(TypedDict):
    """Request payload sent via interrupt when asking the user questions."""

    type: Literal["ask_user"]
    """Discriminator tag, always `'ask_user'`."""

    questions: list[Question]
    """Questions to present to the user."""

    tool_call_id: str
    """ID of the originating tool call, used to route the response back."""


class AskUserAnswered(TypedDict):
    """Widget result when the user submits answers."""

    type: Literal["answered"]
    """Discriminator tag, always `'answered'`."""

    answers: list[str]
    """User-provided answers, one per question."""


class AskUserCancelled(TypedDict):
    """Widget result when the user cancels the prompt."""

    type: Literal["cancelled"]
    """Discriminator tag, always `'cancelled'`."""


AskUserWidgetResult = AskUserAnswered | AskUserCancelled
"""Discriminated union for the ask_user widget Future result."""
