# Client setup — wire remote agents to kb-gateway

## Cole / remote MCP (HTTPS — no Tailscale needed)

```json
{
  "mcpServers": {
    "keyflo-learning-kb": {
      "url": "https://kb-mcp.keyflo.ai/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_KB_GATEWAY_MCP_TOKEN"
      }
    }
  }
}
```

**Cole:** clone `KeyFlo-ai/kb-gateway`, run `./scripts/setup-cole-mcp.sh` — pulls token from GitHub variables. Full guide: [`docs/COLE-SETUP.md`](COLE-SETUP.md).

## Tailscale (optional private path)

On tailnet `smithjsfamily@gmail.com`: `http://100.122.28.113:8790/mcp` with same bearer token. Invite Cole at https://login.tailscale.com/admin/users.

## Cursor on the server (stdio)

```json
{
  "mcpServers": {
    "keyflo-learning-kb": {
      "command": "/root/.venv-langchain-course/bin/python",
      "args": ["-m", "kb_gateway", "--transport", "stdio", "--no-auth"],
      "cwd": "/mnt/blockstorage/business/Keyflo_AI/08_Development/kb-gateway",
      "env": {}
    }
  }
}
```

## Which tool to call

When unsure → **`route_query`**. See [`routing.md`](routing.md). Read [`AGENTS.md`](../AGENTS.md).
