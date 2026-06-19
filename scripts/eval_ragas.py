#!/usr/bin/env python3
"""W19 — Answer quality batch: groundedness + answer_relevance (openevals judges).

Uses langchain-course judges (same metrics family as RAGAS faithfulness/relevancy).
RAGAS package import blocked by optional vertex dep — see D-OP-002 in run/DECISIONS.md.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, "/root/langchain-course")

GOLDEN = ROOT / "eval/golden_ragas.jsonl"
REPORTS = ROOT / "eval/reports"


def _context_from_result(r: dict) -> str:
    docs = r.get("source_documents") or r.get("documents") or []
    parts = []
    for d in docs[:5]:
        if isinstance(d, dict):
            parts.append(d.get("page_content") or d.get("content") or str(d)[:2000])
        else:
            parts.append(str(d)[:2000])
    return "\n\n".join(parts)


def main() -> int:
    if not GOLDEN.is_file():
        print(f"FAIL: missing {GOLDEN} — run mint_golden_from_traces.py first")
        return 1

    import bootstrap

    bootstrap.load_env()
    from lib.langsmith_judges import answer_relevance_evaluator, groundedness_evaluator
    from kb_gateway.tools import route_query

    rows = [json.loads(l) for l in GOLDEN.read_text().splitlines() if l.strip()]
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else min(5, len(rows))
    rows = rows[:cap]

    scores_g: list[float] = []
    scores_a: list[float] = []
    details = []

    for i, row in enumerate(rows):
        q = row["question"]
        print(f"[{i+1}/{len(rows)}] {row['id']} …")
        try:
            r = route_query(q, k=3, max_retries=1)
        except Exception as exc:
            print(f"  skip error: {exc}")
            continue
        answer = (r.get("answer") or "").strip()
        context = _context_from_result(r)
        if not answer or not context:
            print("  skip: empty answer or context")
            continue
        run = {"inputs": {"question": q}, "outputs": {"answer": answer, "context": context}}
        example = {"inputs": {"question": q}, "outputs": {}}
        try:
            g = groundedness_evaluator(run, example)
            a = answer_relevance_evaluator(run, example)
        except Exception as exc:
            print(f"  judge error: {exc}")
            continue
        sg = float(g.get("score", 0))
        sa = float(a.get("score", 0))
        scores_g.append(sg)
        scores_a.append(sa)
        details.append({"id": row["id"], "groundedness": sg, "answer_relevance": sa})
        print(f"  groundedness={sg:.3f} answer_relevance={sa:.3f}")

    if not details:
        print("FAIL: no evaluable rows")
        return 1

    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "method": "openevals-judges (groundedness + answer_relevance)",
        "n": len(details),
        "mean_groundedness": sum(scores_g) / len(scores_g),
        "mean_answer_relevance": sum(scores_a) / len(scores_a),
        "details": details,
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    report_path = REPORTS / f"ragas-baseline-{stamp}.json"
    report_path.write_text(json.dumps(payload, indent=2))
    print(json.dumps({k: payload[k] for k in ("n", "mean_groundedness", "mean_answer_relevance")}, indent=2))
    print(f"report → {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
