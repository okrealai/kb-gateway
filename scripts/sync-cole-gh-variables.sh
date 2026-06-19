#!/usr/bin/env bash
# Sync Cole MCP handoff variables to KeyFlo-ai/kb-gateway GitHub repo.
set -euo pipefail

REPO="${KB_GATEWAY_GH_REPO:-KeyFlo-ai/kb-gateway}"
KEYS="/mnt/blockstorage/private/credentials/learning-kb-api-keys.txt"

cole_token="$(python3 - <<'PY'
from pathlib import Path
p = Path("/mnt/blockstorage/private/credentials/learning-kb-api-keys.txt")
lines = [l.strip() for l in p.read_text().splitlines()]
for i, line in enumerate(lines):
    if line.startswith("# cole") and i + 1 < len(lines):
        nxt = lines[i + 1]
        if nxt and not nxt.startswith("#"):
            print(nxt)
            break
PY
)"

if [[ -z "$cole_token" ]]; then
  echo "error: no cole token in $KEYS" >&2
  exit 1
fi

unset GH_TOKEN GITHUB_TOKEN
gh auth switch --user okrealai >/dev/null 2>&1 || true

gh variable set KB_GATEWAY_MCP_URL --body "https://kb-mcp.keyflo.ai/mcp" -R "$REPO"
gh variable set KB_GATEWAY_MCP_TOKEN --body "$cole_token" -R "$REPO"
gh variable set COLE_SETUP --body "Read docs/COLE-SETUP.md. Run ./scripts/setup-cole-mcp.sh then add config/cole-mcp.json to Cursor MCP." -R "$REPO"

echo "ok: synced variables to $REPO"
