"""MCP server and tool metadata types for the TUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MCPTool:
    """Metadata for a single MCP tool."""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPServerInfo:
    """Metadata for an MCP server and its tools."""

    name: str
    tools: list[MCPTool] = field(default_factory=list)
    transport: str = "stdio"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MCPServerInfo:
        """Build an ``MCPServerInfo`` from a plain dict.

        Accepts the format returned by the stub agent or an external backend::

            {
                "name": "my-server",
                "transport": "stdio",          # optional
                "tools": [
                    {"name": "bash", "description": "Run shell commands"},
                ],
            }
        """
        tools = [
            MCPTool(
                name=t.get("name", ""),
                description=t.get("description", ""),
                input_schema=t.get("inputSchema", {}),
            )
            for t in data.get("tools", [])
        ]
        return cls(
            name=data.get("name", ""),
            tools=tools,
            transport=data.get("transport", "stdio"),
        )
