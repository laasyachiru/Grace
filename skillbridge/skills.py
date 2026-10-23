"""The fixed skill list (data/skills.json) and deterministic keyword matching.

Why a fixed list? So "K8s", "Kubernetes" and "kubernetes" all become one skill id,
and scores stay identical on every run.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache

from . import config

# Boundaries that treat C#, C++, .NET and Node.js as whole words.
_BEFORE = r"(?<![A-Za-z0-9+#.])"
_AFTER = r"(?![A-Za-z0-9+#])"


@lru_cache(maxsize=1)
def load_skills() -> dict[str, dict]:
    """All skills keyed by id, in file order."""
    with open(config.SKILLS_FILE, encoding="utf-8") as f:
        items = json.load(f)
    return {s["id"]: s for s in items}


@lru_cache(maxsize=1)
def _patterns() -> list[tuple[str, re.Pattern]]:
    pats = []
    for sid, s in load_skills().items():
        terms = {s["name"], *s.get("aliases", [])}
        alts = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
        pats.append((sid, re.compile(f"{_BEFORE}(?:{alts}){_AFTER}", re.IGNORECASE)))
    return pats


@lru_cache(maxsize=1)
def _lookup() -> dict[str, str]:
    """Lower-cased id / name / alias -> skill id. Used to clean up model output."""
    table = {}
    for sid, s in load_skills().items():
        for term in (sid, s["name"], *s.get("aliases", [])):
            table[term.lower().strip()] = sid
    return table


def find_by_keyword(text: str) -> set[str]:
    """Skill ids whose name or alias appears in the text."""
    return {sid for sid, pat in _patterns() if pat.search(text or "")}


def normalize(terms) -> set[str]:
    """Map names/aliases the model returned onto known skill ids; unknown terms are dropped."""
    table = _lookup()
    out = set()
    for t in terms or []:
        if isinstance(t, str) and t.lower().strip() in table:
            out.add(table[t.lower().strip()])
    return out


def name(sid: str) -> str:
    return load_skills().get(sid, {}).get("name", sid)


def names(ids) -> list[str]:
    return sorted((name(i) for i in ids), key=str.lower)


def prereqs(sid: str) -> list[str]:
    return [p for p in load_skills().get(sid, {}).get("prereqs", []) if p in load_skills()]


def resources(sid: str) -> list[dict]:
    return load_skills().get(sid, {}).get("resources", [])


def all_ids() -> list[str]:
    return list(load_skills().keys())
