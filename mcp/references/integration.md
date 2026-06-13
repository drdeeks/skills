# MCP Integration Guide

## Native MCP Client
Configure servers in `config.yaml` for automatic tool discovery.

```yaml
mcp_servers:
  - name: "github"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
  - name: "filesystem"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
```

## mcporter CLI Bridge
Ad-hoc server interaction without persistent config.

```bash
# List tools on server
mcporter --server "npx @modelcontextprotocol/server-github" tools list

# Call tool
mcporter --server "npx @modelcontextprotocol/server-github" tools call get_repo --args '{"owner":"octocat","repo":"Hello-World"}'
```

## Server Development

### Python SDK
```python
from mcp import Server, Tool

server = Server("my-server")

@server.tool()
def my_tool(param: str) -> str:
    return f"Result: {param}"

if __name__ == "__main__":
    server.run()
```

### Node SDK
```javascript
const { Server } = require("@modelcontextprotocol/sdk");

const server = new Server({
  name: "my-server",
  version: "1.0.0"
});

server.tool("my_tool", { param: "string" }, async ({ param }) => {
  return { content: [{ type: "text", text: `Result: ${param}` }] };
});

server.run();
```

## Security
- Validate all inputs
- Use environment variables for secrets
- Implement rate limiting
- Audit tool permissions
