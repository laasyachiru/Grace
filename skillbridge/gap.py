"""Compare what the student has with what the company expects. Pure math, no AI, so it is
consistent on every run and easy to explain to judges."""

from __future__ import annotations

from dataclasses import dataclass

from . import config
from . import skills as sk


@dataclass
class GapResult:
    score: int                # 0-100, weighted by how often the company asks for each skill
    matched: list[str]        # skills the student has that the company wants (most-demanded first)
    missing: list[str]        # skills the company wants that the student lacks (most-demanded first)
    focus: list[str]          # top N of `missing`, the "learn only these" list
    extra: list[str]          # student skills this company doesn't ask for


def analyze(
    demand: dict[str, float],
    user_skills: set[str],
    done: set[str] | frozenset = frozenset(),
    min_demand: float | None = None,
    top_n: int | None = None,
) -> GapResult:
    min_demand = config.MIN_DEMAND if min_demand is None else min_demand
    top_n = config.FOCUS_COUNT if top_n is None else top_n

    have = set(user_skills) | set(done)
    relevant = {s: w for s, w in demand.items() if w >= min_demand}
    total = sum(relevant.values())

    order = lambda s: (-relevant[s], sk.name(s).lower())
    matched = sorted((s for s in relevant if s in have), key=order)
    missing = sorted((s for s in relevant if s not in have), key=order)
    score = round(100 * sum(relevant[s] for s in matched) / total) if total else 0
    extra = sorted((s for s in user_skills if s not in demand), key=lambda s: sk.name(s).lower())

    return GapResult(score=score, matched=matched, missing=missing, focus=missing[:top_n], extra=extra)
