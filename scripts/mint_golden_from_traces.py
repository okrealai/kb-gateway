#!/usr/bin/env python3
"""W18 — Mint eval/golden_ragas.jsonl from regression seeds + LangSmith MCP traces."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGRESSION = ROOT / "eval/regression_queries.json"
OUT = ROOT / "eval/golden_ragas.jsonl"
AUDIT = ROOT / "logs/audit.jsonl"


def norm_q(q: str) -> str:
    return re.sub(r"\s+", " ", q.strip().lower())


def qid(text: str, prefix: str = "q") -> str:
    h = hashlib.sha256(text.encode()).hexdigest()[:12]
    return f"{prefix}-{h}"


def load_regression() -> list[dict]:
    rows = json.loads(REGRESSION.read_text())
    out = []
    for row in rows:
        q = row["question"]
        out.append({
            "id": row.get("id") or qid(q, "reg"),
            "question": q,
            "expected_route": row.get("expected_route"),
            "source": "regression",
            "ground_truth": None,
        })
    return out


def load_audit_hashes() -> set[str]:
    hashes: set[str] = set()
    if not AUDIT.is_file():
        return hashes
    for line in AUDIT.read_text().splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if h := row.get("question_hash"):
            hashes.add(h)
    return hashes


def fetch_langsmith_questions(days: int = 30, mcp_only: bool = True) -> list[dict]:
    sys.path.insert(0, "/root/langchain-course")
    import bootstrap

    bootstrap.load_env()
    from langsmith import Client

    since = datetime.now(timezone.utc) - timedelta(days=days)
    project = os.environ.get("LANGSMITH_PROJECT", "LANGCHAIN-APP")
    client = Client()
    filt = None
    if mcp_only:
        filt = 'and(eq(name, "agentic_router"), eq(metadata_key, "surface"), eq(metadata_value, "mcp"))'
    else:
        filt = 'eq(name, "agentic_router")'

    out: list[dict] = []
    try:
        runs = client.list_runs(
            project_name=project,
            start_time=since,
            filter=filt,
            limit=100,
        )
    except Exception as exc:
        print(f"WARN: langsmith fetch failed: {exc}", file=sys.stderr)
        return out

    for run in runs:
        inputs = run.inputs or {}
        q = inputs.get("question") or inputs.get("input") or inputs.get("query")
        if not q or not isinstance(q, str) or len(q) < 8:
            continue
        route = None
        if isinstance(run.outputs, dict):
            route = run.outputs.get("route")
        out.append({
            "id": qid(q, "trace"),
            "question": q.strip(),
            "expected_route": route,
            "source": "langsmith-mcp" if mcp_only else "langsmith",
            "ground_truth": None,
            "run_id": str(run.id),
        })
    return out


def merge_dedupe(*sources: list[dict]) -> list[dict]:
    seen: set[str] = set()
    merged: list[dict] = []
    for src in sources:
        for row in src:
            key = norm_q(row["question"])
            if key in seen:
                continue
            seen.add(key)
            merged.append(row)
    return merged


def main() -> int:
    seeds = load_regression()
    traces_mcp = fetch_langsmith_questions(mcp_only=True)
    traces_all = fetch_langsmith_questions(mcp_only=False) if len(traces_mcp) < 8 else []

    merged = merge_dedupe(seeds, traces_mcp, traces_all)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for row in merged:
            f.write(json.dumps(row, default=str) + "\n")

    print(f"minted {len(merged)} rows → {OUT}")
    print(f"  regression seeds: {len(seeds)}")
    print(f"  langsmith mcp traces: {len(traces_mcp)}")
    print(f"  langsmith all traces added: {len(traces_all)}")
    if len(merged) < 20:
        print(f"WARN: {len(merged)} < 20 — add regression rows or wait for MCP traffic")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
