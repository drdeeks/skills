# Model Context Protocol (MCP) Reference

## Overview
MCP is an open protocol for connecting AI assistants to external tools and data sources.

## Core Concepts

### Server
- Provides tools, resources, and prompts
- Communicates via JSON-RPC 2.0
- Can be local (stdio) or remote (HTTP/SSE)

### Client
- Discovers server capabilities
- Invokes tools
- Reads resources
- Uses prompts

### Transport
- **stdio**: Local process communication
- **HTTP/SSE**: Remote server communication
- **WebSocket**: Real-time bidirectional

## Protocol Messages

### Initialize
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "client", "version": "1.0"}
  }
}
```

### List Tools
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

### Call Tool
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {"arg": "value"}
  }
}
```

## Capabilities
- **tools**: Executable functions
- **resources**: Readable data sources
- **prompts**: Reusable prompt templates

## Error Handling
Standard JSON-RPC errors:
- `-32600`: Invalid Request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
