# Cloudflare WAF / rate limit — kb-mcp.keyflo.ai (W17)

**Profile:** Keyflo (`cole@keyflo.ai`) · **Zone:** `keyflo.ai`  
**Data source:** `usage_report.sh 14` before applying (Phase 6 D-P2)

## Observed baseline (2026-06-19)

| Metric | Value | Source |
|---|---|---|
| Audit requests (14d) | low single-digit/day | `logs/audit.jsonl` |
| Clients | unknown (smoke), cole (test) | audit log |
| p95 latency | ~774ms (health/route) | usage_report |

**Starting rules** (conservative — tune when traffic grows):

| Rule | Match | Limit | Action |
|---|---|---|---|
| RL-401-storm | URI Path contains `/mcp` AND Response Code 401 | 20 req / 1 min / IP | Block |
| RL-mcp-burst | URI Path equals `/mcp` | 120 req / 1 min / IP | Block |

Managed WAF: enable **Bot Fight Mode** + **OWASP Core Ruleset** on zone (dashboard).

## Apply via dashboard (~2 min)

1. Cloudflare → `keyflo.ai` → **Security** → **WAF** → **Rate limiting rules**
2. Create **RL-401-storm** (block unauthenticated abuse)
3. Create **RL-mcp-burst** (generous authenticated burst)
4. **Security** → **Settings** → enable Bot Fight Mode

## Verify after apply

```bash
./scripts/verify_remote_mcp.sh   # expect 406 with token, 401 without
curl -s -o /dev/null -w "%{http_code}\n" https://kb-mcp.keyflo.ai/mcp  # 401
```

## API script (optional)

```bash
./scripts/setup_cloudflare_rate_limit.sh --dry-run
./scripts/setup_cloudflare_rate_limit.sh   # requires token Zone WAF Edit scope
```

Token: `KEYFLO_CLOUDFLARE_API_TOKEN` via `load.sh keyflo`.

## Operator approval

Log approval in `run/DECISIONS.md` D-P2 when rules are live.
