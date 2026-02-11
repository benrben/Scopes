#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScoreResult:
    name: str
    score: float
    max_score: float


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: scripts/score_evals.py <results.json>")
        return 2

    path = Path(argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))

    # Expected format (manual):
    # {
    #   "evaluations": [
    #     {"name": "planning-idea", "checks": [{"id":"...","weight":2,"pass":true}]}
    #   ]
    # }
    results: list[ScoreResult] = []
    for ev in data.get("evaluations", []):
        name = ev.get("name", "(unknown)")
        checks = ev.get("checks", [])
        max_score = float(sum(c.get("weight", 1) for c in checks))
        score = float(sum(c.get("weight", 1) for c in checks if c.get("pass") is True))
        results.append(ScoreResult(name=name, score=score, max_score=max_score))

    if not results:
        print("no evaluations found")
        return 1

    for r in results:
        pct = 0.0 if r.max_score == 0 else (100.0 * r.score / r.max_score)
        print(f"{r.name}: {r.score:.1f}/{r.max_score:.1f} ({pct:.1f}%)")

    total_score = sum(r.score for r in results)
    total_max = sum(r.max_score for r in results)
    total_pct = 0.0 if total_max == 0 else (100.0 * total_score / total_max)
    print(f"TOTAL: {total_score:.1f}/{total_max:.1f} ({total_pct:.1f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

