# Cole setup — kb-gateway MCP

**Repo:** `KeyFlo-ai/kb-gateway`  
**Purpose:** Query the learning corpus via MCP (`route_query`, `query_namespace`, `graph_query`) from Cursor or any MCP client.

**No Tailscale required** — use the public HTTPS endpoint (same pattern as `kb-api.keyflo.ai`).

---

## Quick start (5 minutes)

1. **Clone the repo**
   ```bash
   git clone git@github.com:KeyFlo-ai/kb-gateway.git
   cd kb-gateway
   gh auth login   # once, as cwrightson
   ```

2. **Pull MCP config from GitHub variables**
   ```bash
   chmod +x scripts/setup-cole-mcp.sh
   ./scripts/setup-cole-mcp.sh
   cat config/cole-mcp.json
   ```

3. **Add to Cursor** → Settings → MCP → paste the `keyflo-learning-kb` block from `config/cole-mcp.json`.

4. **Verify** — ask your agent: *"Use keyflo-learning-kb route_query: what is PAS copy structure?"*

---

## MCP endpoint

| Item | Value |
|------|-------|
| URL | `https://kb-mcp.keyflo.ai/mcp` |
| Auth | `Authorization: Bearer <token>` (from GitHub variable `KB_GATEWAY_MCP_TOKEN`) |
| Tools | `route_query`, `query_namespace`, `graph_query`, `list_namespaces`, `health` |

Manual test:
```bash
source config/cole-mcp.json  # or export token from gh variable
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $KB_GATEWAY_MCP_TOKEN" \
  https://kb-mcp.keyflo.ai/mcp
```
Expect `406` (MCP handshake), not `401`.

---

## Alternative: HTTP query API (no MCP)

If you only need Q&A without MCP tools, use the existing API:

| Item | Value |
|------|-------|
| Repo | `KeyFlo-ai/knowledge-base` |
| URL | `https://kb-api.keyflo.ai/v1/query` |
| Setup | `./scripts/setup-cole-env.sh` |

Same corpus, simpler for scripts.

---

## Optional: Tailscale (private path)

James's personal tailnet (`smithjsfamily@gmail.com`) also exposes the gateway at `http://100.122.28.113:8790/mcp` for tailnet members only.

**To join:** James sends a Tailscale invite to `cole@keyflo.ai` from https://login.tailscale.com/admin/users → **Invite external users**. Install Tailscale, accept invite, then use the tailnet URL above with the same bearer token.

---

## GitHub variables (pre-configured)

| Variable | Purpose |
|----------|---------|
| `KB_GATEWAY_MCP_URL` | `https://kb-mcp.keyflo.ai/mcp` |
| `KB_GATEWAY_MCP_TOKEN` | Bearer token (same as learning KB API cole token) |
| `COLE_SETUP` | Pointer to this file |

---

## Which tool to use

| Question type | Tool |
|---------------|------|
| Not sure | `route_query` |
| How-to / passages | `query_namespace` |
| Coverage / disputes | `graph_query` |

Read [`AGENTS.md`](../AGENTS.md) for full routing rules.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `401` | Re-run `setup-cole-mcp.sh`; token may have rotated |
| Cursor can't connect | Check URL ends with `/mcp`; restart Cursor |
| `502` / timeout | Ping James — `systemctl status kb-gateway` on server |
| Tailscale URL fails | Not on tailnet — use HTTPS URL instead |
