# Building AI Coding Agents with DeepAgents

A byte-sized, 10-part series on building production-ready AI coding agents using the DeepAgents framework.

## Series Overview

This series teaches you to build a CLI-based AI coding agent from scratch using **DeepAgents**, an opinionated framework built on LangChain and LangGraph. Each article builds on the previous one, following the laws of simplicity with practical, working code examples.

## Articles

### Part 1: [Why DeepAgents?](part-1-why-deepagents.md)
- Understanding the DeepAgents philosophy
- When to use DeepAgents vs. vanilla LangChain
- The "configure, don't implement" approach

### Part 2: [Your First Agent](part-2-first-agent.md)
- Installation and setup
- Creating a working agent in 10 lines
- Understanding conversation context with `thread_id`
- Streaming responses

### Part 3: [Adding Custom Tools](part-3-custom-tools.md)
- The `@tool` decorator
- Building domain-specific capabilities
- Async tools and Pydantic schemas
- Web search implementation with Tavily

### Part 4: [Filesystem and Shell Backends](part-4-backends.md)
- LocalShellBackend configuration
- Virtual mode for clean paths
- Security considerations
- Common file operation patterns

### Part 5: [Memory and AGENTS.md](part-6-skills.md)
- Conversation persistence with checkpointers
- Knowledge memory with AGENTS.md files
- Cross-thread memory with Store
- Best practices for organizing memory

### Part 6: [Skills System](part-6-skills.md)
- On-demand capability loading
- Creating SKILL.md files
- Skill directory organization
- When to use skills vs. memory

### Part 7: [Human-in-the-Loop](part-7-hitl.md)
- Configuring approval workflows
- Handling interrupts with `Command`
- Building approval UIs
- Security best practices

### Part 8: [Building a CLI](part-8-cli.md)
- The protocol pattern
- Event translation layer
- CLI interface design
- Environment configuration

### Part 9: [Testing and Debugging](part-9-testing.md)
- Unit testing components
- Mocking and stub agents
- Integration testing
- Debugging techniques and common issues

### Part 10: [Production Considerations](part-10-production.md)
- Security checklist
- Performance optimization
- Observability and monitoring
- Deployment strategies

## Key Principles

### 1. Byte-Sized Learning
Each article focuses on one concept with working code you can run immediately.

### 2. Laws of Simplicity
Following John Maeda's principles:
- **REDUCE**: Only what's essential
- **ORGANIZE**: Clear structure and boundaries
- **LEARN**: Prioritize clarity
- **TIME**: Optimize for efficiency

### 3. Sequential Progression
Each part builds on the previous. Start at Part 1 and work through to Part 10.

## Prerequisites

- Python 3.9+
- OpenAI API key (or other LLM provider)
- Basic Python knowledge

## Quick Start

```bash
# Install dependencies
pip install deepagents langchain-openai

# Set your API key
export OPENAI_API_KEY="sk-..."

# Start with Part 2
python your_first_agent.py
```

## What You'll Build

By the end of this series, you'll have:

- ✅ A working CLI coding agent
- ✅ File and shell access with safety controls
- ✅ Persistent memory and skills
- ✅ Human approval workflows
- ✅ Comprehensive test suite
- ✅ Production-ready configuration

## Target Audience

- Developers wanting to build AI coding assistants
- Teams exploring agent-based workflows
- Anyone curious about LangChain/LangGraph in practice

## About DeepAgents

DeepAgents is an opinionated agent framework from LangChain that provides:

- **Task Planning**: Built-in todo tracking
- **Filesystem**: File operations out of the box
- **Subagents**: Delegate to specialized agents
- **Memory**: Persistent storage across sessions
- **Human-in-the-loop**: Approval workflows
- **Skills**: On-demand capability loading

Learn more at [github.com/langchain-ai/deepagents](https://github.com/langchain-ai/deepagents/)

## License

These articles are provided as educational content. Code examples are MIT licensed unless otherwise noted.

---

*Start your journey: [Part 1: Why DeepAgents?](part-1-why-deepagents.md)*
