#!/usr/bin/env bash
# W21 — confirm Cole client in audit log or report pending handoff.
set -euo pipefail

cd "$(dirname "$0")/.."
AUDIT="${KB_GATEWAY_AUDIT_LOG:-logs/audit.jsonl}"

cole_count=0
if [[ -f "$AUDIT" ]]; then
  cole_count=$(grep -c '"client": "cole"' "$AUDIT" 2>/dev/null || echo 0)
fi

echo "cole audit entries: $cole_count"
if [[ "$cole_count" -ge 1 ]]; then
  echo "COLE_HANDOFF OK — client=cole seen in audit log"
  exit 0
fi

echo "COLE_HANDOFF PENDING — no client=cole in audit yet"
echo "Action: Cole runs ./scripts/setup-cole-mcp.sh and one route_query in Cursor"
echo "See docs/COLE-SETUP.md"
exit 0
