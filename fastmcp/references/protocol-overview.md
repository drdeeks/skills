# FastMCP Protocol Overview

## What is MCP?

Model Context Protocol (MCP) enables LLMs to interact with external tools and data sources.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   LLM Host  │────▶│  MCP Server │────▶│   Tool/API  │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Core Concepts

| Concept | Description |
|---------|-------------|
| Tool | Function the LLM can call |
| Resource | Data the LLM can access |
| Prompt | Template for LLM interactions |
| Transport | Communication protocol (stdio, HTTP) |

## FastMCP Features

- Simple Python decorators
- Auto-generated schemas
- Built-in error handling
- Support for async tools
- Type-safe parameters

## Quick Start

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    mcp.run()
```
