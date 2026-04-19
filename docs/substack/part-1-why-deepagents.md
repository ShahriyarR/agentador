# Building AI Coding Agents with DeepAgents — Part 1: Why DeepAgents?

> A byte-sized guide to understanding when and why to use the DeepAgents framework.

---

## The Problem with Building Agents from Scratch

Building AI agents is exciting. You start with a simple idea: "Let me create an agent that can read files and answer questions." 

Soon you need:
- Tool calling with structured outputs
- Conversation memory across sessions
- File system access with safety controls
- Human approval for sensitive operations
- Task planning for multi-step workflows
- Subagents for specialized work

Each of these is a rabbit hole. Before you know it, you're maintaining infrastructure instead of building your actual agent.

## Enter DeepAgents

[DeepAgents](https://github.com/langchain-ai/deepagents/) is an opinionated framework built on LangChain and LangGraph. It provides **batteries-included** agent capabilities through middleware:

| Capability | What You Get |
|------------|--------------|
| **Task Planning** | `write_todos` tool for breaking down complex tasks |
| **Filesystem** | `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `ls` |
| **Shell Execution** | `execute` tool for running commands |
| **Subagents** | `task` tool for spawning specialized agents |
| **Memory** | Persistent storage across threads via Store |
| **Human-in-the-loop** | Approval workflows for sensitive operations |
| **Skills** | On-demand loading of specialized capabilities |

## When to Use DeepAgents

Use DeepAgents when your agent needs:

✅ **Multi-step tasks** requiring planning  
✅ **Large context** requiring file management  
✅ **Specialized subagents** for different domains  
✅ **Persistent memory** across sessions  

Use vanilla LangChain's `create_agent` when:

✅ Simple, single-purpose tasks  
✅ Context fits in a single prompt  
✅ Single agent is sufficient  
✅ Ephemeral, single-session work  

## The Philosophy: Configure, Don't Implement

DeepAgents follows a simple principle: **you configure capabilities, not implement them.**

Instead of writing code to handle file operations, you configure a backend:

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True)
)
```

The agent now has access to file tools. No boilerplate. No infrastructure.

## What's Next

In this series, we'll build a coding agent CLI step by step:

1. **Part 1** (this article): Understanding DeepAgents
2. **Part 2**: Creating your first agent
3. **Part 3**: Adding custom tools
4. **Part 4**: Filesystem and shell backends
5. **Part 5**: Memory with AGENTS.md
6. **Part 6**: Skills system
7. **Part 7**: Human-in-the-loop approval
8. **Part 8**: Building the CLI
9. **Part 9**: Testing and debugging
10. **Part 10**: Production considerations

Each article builds on the previous one. By the end, you'll have a fully functional coding agent.

## Key Takeaway

DeepAgents lets you focus on **what your agent does**, not **how it does it**. The framework handles the infrastructure; you handle the logic.

---

*Next: [Part 2: Your First Agent](part-2-first-agent.md)*
