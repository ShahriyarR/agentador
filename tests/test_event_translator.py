"""Tests for EventTranslator."""

import pytest

from agent_tui.domain.protocol import EventType
from agent_tui.services.deep_agents.event_translator import EventTranslator


@pytest.fixture
def translator() -> EventTranslator:
    return EventTranslator()


class TestMessageChunk:
    def test_content_block_delta_yields_message_chunk(self, translator: EventTranslator):
        event = {
            "event_type": "on_chain_stream",
            "data": {
                "name": "content_block_delta",
                "data": {"content": "Hello"},
            },
        }
        results = list(translator.translate(event))
        assert len(results) == 1
        assert results[0].type == EventType.MESSAGE_CHUNK
        assert results[0].text == "Hello"

    def test_content_block_delta_empty_content_yields_no_events(self, translator: EventTranslator):
        event = {
            "event_type": "on_chain_stream",
            "data": {
                "name": "content_block_delta",
                "data": {"content": ""},
            },
        }
        results = list(translator.translate(event))
        assert len(results) == 0

    def test_unknown_chain_stream_name_yields_no_events(self, translator: EventTranslator):
        event = {
            "event_type": "on_chain_stream",
            "data": {
                "name": "unknown",
                "data": {},
            },
        }
        results = list(translator.translate(event))
        assert len(results) == 0


class TestToolCall:
    def test_on_tool_start_yields_tool_call(self, translator: EventTranslator):
        event = {
            "event_type": "on_tool_start",
            "data": {
                "name": "bash",
                "input": {"command": "ls -la"},
            },
            "run_id": "run_123",
        }
        results = list(translator.translate(event))
        assert len(results) == 1
        assert results[0].type == EventType.TOOL_CALL
        assert results[0].tool_name == "bash"
        assert results[0].tool_args == {"command": "ls -la"}
        assert results[0].tool_id == "run_123"

    def test_on_tool_start_empty_name_yields_no_events(self, translator: EventTranslator):
        event = {
            "event_type": "on_tool_start",
            "data": {
                "name": "",
                "input": {},
            },
        }
        results = list(translator.translate(event))
        assert len(results) == 0

    def test_on_tool_start_missing_input_yields_tool_call_with_empty_args(self, translator: EventTranslator):
        event = {
            "event_type": "on_tool_start",
            "data": {
                "name": "bash",
            },
        }
        results = list(translator.translate(event))
        assert len(results) == 1
        assert results[0].tool_args == {}


class TestToolResult:
    def test_on_tool_end_yields_tool_result(self, translator: EventTranslator):
        event = {
            "event_type": "on_tool_end",
            "data": {
                "output": "file1.txt\nfile2.txt",
            },
        }
        results = list(translator.translate(event))
        assert len(results) == 1
        assert results[0].type == EventType.TOOL_RESULT
        assert results[0].tool_output == "file1.txt\nfile2.txt"

    def test_on_tool_end_with_none_output_yields_no_events(self, translator: EventTranslator):
        event = {
            "event_type": "on_tool_end",
            "data": {
                "output": None,
            },
        }
        results = list(translator.translate(event))
        assert len(results) == 0

    def test_on_tool_end_missing_output_yields_no_events(self, translator: EventTranslator):
        event = {
            "event_type": "on_tool_end",
            "data": {},
        }
        results = list(translator.translate(event))
        assert len(results) == 0


class TestMessageEnd:
    def test_on_chain_end_yields_message_end(self, translator: EventTranslator):
        event = {
            "event_type": "on_chain_end",
            "data": {},
        }
        results = list(translator.translate(event))
        assert len(results) == 1
        assert results[0].type == EventType.MESSAGE_END


class TestError:
    def test_on_tool_error_yields_error(self, translator: EventTranslator):
        event = {
            "event_type": "on_tool_error",
            "data": {
                "error": "Connection timeout",
            },
        }
        results = list(translator.translate(event))
        assert len(results) == 1
        assert results[0].type == EventType.ERROR
        assert "Connection timeout" in results[0].text

    def test_on_tool_error_without_explicit_error_field_yields_error_with_data(self, translator: EventTranslator):
        event = {
            "event_type": "on_tool_error",
            "data": {"some": "data"},
        }
        results = list(translator.translate(event))
        assert len(results) == 1
        assert results[0].type == EventType.ERROR
        assert "Tool error:" in results[0].text


class TestUnknownEvent:
    def test_unknown_event_type_yields_no_events(self, translator: EventTranslator):
        event = {
            "event_type": "on_unknown_event",
            "data": {},
        }
        results = list(translator.translate(event))
        assert len(results) == 0

    def test_event_with_missing_event_type_yields_no_events(self, translator: EventTranslator):
        event = {
            "data": {},
        }
        results = list(translator.translate(event))
        assert len(results) == 0

    def test_event_with_missing_data_yields_no_events(self, translator: EventTranslator):
        event = {
            "event_type": "on_chain_end",
        }
        results = list(translator.translate(event))
        assert len(results) == 0


class TestTranslateReturnsIterator:
    def test_translate_returns_iterator(self, translator: EventTranslator):
        event = {
            "event_type": "on_chain_end",
            "data": {},
        }
        result = translator.translate(event)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")
