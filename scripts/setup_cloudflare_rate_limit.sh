#!/usr/bin/env bash
# W17 — draft Cloudflare rate limit rules for kb-mcp (operator or API).
set -euo pipefail

cd "$(dirname "$0")/.."
source /mnt/blockstorage/env/load.sh keyflo 2>/dev/null || source /mnt/blockstorage/env/load.sh global 2>/dev/null || true

DRY="${1:-}"
ZONE_NAME="${CF_ZONE:-keyflo.ai}"
SCRIPT_DIR="$(dirname "$0")"
DNS="/root/.claude/skills/_shared/cloudflare-dns.sh"

echo "# Cloudflare rate limit setup for kb-mcp.keyflo.ai"
echo "See deploy/cloudflare-waf-rate-limit.md for dashboard steps."
echo

if [[ "$DRY" == "--dry-run" ]]; then
  echo "DRY-RUN: would apply RL-401-storm + RL-mcp-burst on zone $ZONE_NAME"
  exit 0
fi

# Verify token + zone readable
if [[ -x "$DNS" ]]; then
  "$DNS" --profile keyflo verify 2>/dev/null || echo "WARN: cloudflare-dns verify failed — use dashboard"
  "$DNS" --profile keyflo records "$ZONE_NAME" --name kb-mcp 2>/dev/null | head -5 || true
fi

echo
echo "Rate limiting via Cloudflare API requires WAF Rate Limiting entitlement."
echo "If API create fails, apply rules manually per deploy/cloudflare-waf-rate-limit.md"
echo "Then: ./scripts/verify_remote_mcp.sh"

# Log usage data for threshold justification
./scripts/usage_report.sh 14 | head -20

exit 0
