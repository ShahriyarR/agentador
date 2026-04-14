"""DeepAgentsAdapter — wraps DeepAgents as an AgentProtocol implementation."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from agent_tui.domain.protocol import AgentEvent
from agent_tui.services.deep_agents.event_translator import EventTranslator


class DeepAgentsAdapter:
    """Implements AgentProtocol by wrapping DeepAgents.

    This adapter uses lazy loading for the DeepAgents package - it attempts
    to import DeepAgents on first use rather than at module load time.
    This allows the TUI to run even if DeepAgents is not installed.

    If DeepAgents is not available, calling stream() will raise an informative
    error explaining that deepagents needs to be installed.
    """

    def __init__(self, model: str = "openai:gpt-4o") -> None:
        """Initialize the adapter.

        Args:
            model: The model to use for DeepAgents. Defaults to "openai:gpt-4o".
        """
        self._model = model
        self._agent: Any = None
        self._translator = EventTranslator()
        self._deepagents_available: bool
        self._cancelled = False
        self._approval_event: asyncio.Event | None = None
        self._approval_result: bool = False
        self._answer_event: asyncio.Event | None = None
        self._user_answer: str = ""

        self._deepagents_available = self._check_deepagents_available()

    def _check_deepagents_available(self) -> bool:
        """Check if DeepAgents package is available."""
        try:
            import deepagents  # noqa: F401

            return True
        except ImportError:
            return False

    def _ensure_agent(self) -> Any:
        """Ensure the DeepAgents agent is initialized.

        Returns:
            The DeepAgents agent instance.

        Raises:
            RuntimeError: If DeepAgents is not installed.
        """
        if not self._deepagents_available:
            raise RuntimeError(
                "DeepAgents is not installed. Please install it with:\n"
                "    pip install deepagents\n"
                "Or check that the package is available in your environment."
            )

        if self._agent is None:
            import deepagents

            self._agent = deepagents.Agent(model=self._model)

        return self._agent

    async def stream(self, message: str, *, thread_id: str | None = None) -> AsyncIterator[AgentEvent]:
        """Send a user message, receive a stream of events.

        Args:
            message: The user message to send.
            thread_id: Optional thread identifier for conversation context.

        Yields:
            AgentEvent objects from the DeepAgents agent, translated via
            EventTranslator.

        Raises:
            RuntimeError: If DeepAgents is not installed.
        """
        if not self._deepagents_available:
            raise RuntimeError(
                "DeepAgents is not installed. Please install it with:\n"
                "    pip install deepagents\n"
                "Or check that the package is available in your environment."
            )

        self._cancelled = False
        self._approval_event = asyncio.Event()
        self._approval_result = False
        self._answer_event = asyncio.Event()
        self._user_answer = ""

        agent = self._ensure_agent()

        try:
            async for raw_event in agent.stream(message, thread_id=thread_id):
                if self._cancelled:
                    return

                translated = self._translator.translate(raw_event)
                for event in translated:
                    if event.type == AgentEvent.type:
                        if event.type == "tool_call":
                            self._approval_event.set()
                            await self._approval_event.wait()
                            self._approval_event = None
                            if not self._approval_result:
                                continue
                        elif event.type == "ask_user":
                            self._answer_event.set()
                            await self._answer_event.wait()
                            self._answer_event = None
                    yield event

                if raw_event.get("event_type") == "on_chain_end":
                    break
        except Exception as e:
            yield AgentEvent(
                type="error",
                text=f"DeepAgents error: {str(e)}",
            )

    async def approve_tool(self, tool_id: str, approved: bool) -> None:
        """Respond to a TOOL_CALL event (approve or deny).

        Args:
            tool_id: The ID of the tool call to respond to.
            approved: Whether to approve (True) or deny (False) the tool call.
        """
        self._approval_result = approved
        if self._approval_event is not None:
            self._approval_event.set()

    async def answer_question(self, answer: str) -> None:
        """Respond to an ASK_USER event.

        Args:
            answer: The user's answer to the question.
        """
        self._user_answer = answer
        if self._answer_event is not None:
            self._answer_event.set()

    async def cancel(self) -> None:
        """Cancel the current execution."""
        self._cancelled = True
        if self._approval_event is not None:
            self._approval_event.set()
        if self._answer_event is not None:
            self._answer_event.set()

    async def get_threads(self) -> list[dict[str, Any]]:
        """List available conversation threads.

        Returns:
            A list of thread dictionaries with id, title, updated_at,
            created_at, and message_count fields.
        """
        if not self._deepagents_available:
            return [
                {
                    "id": "thread_default",
                    "title": "Default conversation",
                    "updated_at": "2026-04-14T00:00:00Z",
                    "created_at": "2026-04-14T00:00:00Z",
                    "message_count": 0,
                },
            ]

        agent = self._ensure_agent()
        threads = await agent.get_threads()
        return threads

    async def get_models(self) -> list[dict[str, Any]]:
        """List available models.

        Returns:
            A list of model dictionaries with name, provider, context_limit,
            and description fields.
        """
        return [
            {
                "name": "openai:gpt-4o",
                "provider": "openai",
                "context_limit": 128_000,
                "description": "OpenAI GPT-4o model",
            },
            {
                "name": "openai:gpt-4o-mini",
                "provider": "openai",
                "context_limit": 128_000,
                "description": "OpenAI GPT-4o Mini model",
            },
            {
                "name": "anthropic:claude-3-5-sonnet",
                "provider": "anthropic",
                "context_limit": 200_000,
                "description": "Anthropic Claude 3.5 Sonnet",
            },
        ]

    async def set_model(self, model_name: str) -> None:
        """Switch the active model.

        Args:
            model_name: The name of the model to switch to.
        """
        self._model = model_name
        self._agent = None

    async def get_skills(self) -> list[dict[str, Any]]:
        """List available skills.

        Returns:
            A list of skill dictionaries with name and description fields.
        """
        if not self._deepagents_available:
            return [
                {
                    "name": "search",
                    "description": "Search the web for information",
                },
                {
                    "name": "summarize",
                    "description": "Summarize a document or URL",
                },
                {
                    "name": "analyze",
                    "description": "Analyze code or data",
                },
            ]

        agent = self._ensure_agent()
        skills = await agent.get_skills()
        return skills

    async def invoke_skill(self, name: str, args: str) -> None:
        """Invoke a skill by name.

        Args:
            name: The name of the skill to invoke.
            args: Arguments to pass to the skill.
        """
        if not self._deepagents_available:
            return

        agent = self._ensure_agent()
        await agent.invoke_skill(name, args)
