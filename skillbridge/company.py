"""Company Skill Radar: what a company expects, and how that changes over time.

Job descriptions live in data/jobs/<company-folder>/YYYY-MM-DD_role-title.txt
Each one is turned into a set of skills (cached in data/cache/extractions.json so the
local model only reads each file once). A skill's "demand" = share of the company's
job descriptions that ask for it.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from . import config
from . import skills as sk
from .extract import extract_skills

_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})[_\- ]?(.*)$")
_TEXT_EXT = {".txt", ".md"}


@dataclass
class JobPosting:
    company: str
    posted: date
    title: str
    path: Path
    text: str
    skills: set[str] = field(default_factory=set)


# ---------- loading ----------

def list_companies(jobs_dir: Path | None = None) -> list[str]:
    jobs_dir = jobs_dir or config.JOBS_DIR
    if not jobs_dir.exists():
        return []
    return sorted(
        p.name for p in jobs_dir.iterdir()
        if p.is_dir() and not p.name.startswith(".") and any(f.suffix in _TEXT_EXT for f in p.iterdir())
    )


def display_name(folder: str) -> str:
    label = re.sub(r"[-_]+", " ", folder).strip().title()
    return label.replace("Sample ", "Sample: ", 1) if label.startswith("Sample ") else label


def _parse_filename(path: Path) -> tuple[date, str]:
    m = _DATE_RE.match(path.stem)
    if m:
        try:
            posted = datetime.strptime(m.group(1), "%Y-%m-%d").date()
            title = m.group(2) or "Job description"
            return posted, re.sub(r"[-_]+", " ", title).strip().title()
        except ValueError:
            pass
    posted = datetime.fromtimestamp(path.stat().st_mtime).date()
    return posted, re.sub(r"[-_]+", " ", path.stem).strip().title()


def load_postings(company: str, jobs_dir: Path | None = None) -> list[JobPosting]:
    folder = (jobs_dir or config.JOBS_DIR) / company
    postings = []
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() not in _TEXT_EXT:
            continue
        posted, title = _parse_filename(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        postings.append(JobPosting(company, posted, title, path, text))
    return sorted(postings, key=lambda p: p.posted)


def signature(company: str, jobs_dir: Path | None = None) -> tuple:
    """Changes whenever a job file is added/edited, so cached profiles refresh automatically."""
    folder = (jobs_dir or config.JOBS_DIR) / company
    return tuple(sorted((p.name, p.stat().st_size, int(p.stat().st_mtime)) for p in folder.iterdir()))


# ---------- extraction cache ----------

def _cache_file() -> Path:
    return config.CACHE_DIR / "extractions.json"


def _load_cache() -> dict:
    try:
        return json.loads(_cache_file().read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(cache: dict) -> None:
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_file().write_text(json.dumps(cache, indent=1), encoding="utf-8")


def _cache_key(text: str, use_ai: bool) -> str:
    mode = f"ai:{config.MODEL}" if use_ai else "kw"
    return hashlib.sha1(f"{mode}|{text}".encode("utf-8")).hexdigest()


def extract_postings(postings: list[JobPosting], use_ai: bool) -> list[JobPosting]:
    """Fill posting.skills, reusing cached results when possible."""
    from . import llm

    ai = use_ai and llm.ai_ready()
    cache = _load_cache()
    changed = False
    for p in postings:
        key = _cache_key(p.text, ai)
        if key in cache:
            p.skills = set(cache[key])
        else:
            p.skills = extract_skills(p.text, use_ai=ai)
            cache[key] = sorted(p.skills)
            changed = True
    if changed:
        _save_cache(cache)
    return postings


# ---------- profile ----------

def _period(d: date) -> str:
    return f"{d.year}-Q{(d.month - 1) // 3 + 1}"


def build_profile(company: str, use_ai: bool = True, jobs_dir: Path | None = None) -> dict:
    postings = extract_postings(load_postings(company, jobs_dir), use_ai)
    n = len(postings)
    counts = Counter(s for p in postings for s in p.skills)
    demand = {s: c / n for s, c in counts.items()} if n else {}

    # Trend: share of postings per quarter that mention each skill.
    periods = sorted({_period(p.posted) for p in postings})
    trend_rows = {}
    for per in periods:
        group = [p for p in postings if _period(p.posted) == per]
        c = Counter(s for p in group for s in p.skills)
        trend_rows[per] = {s: c.get(s, 0) / len(group) for s in demand}
    trend = pd.DataFrame.from_dict(trend_rows, orient="index").sort_index() if trend_rows else pd.DataFrame()

    return {
        "company": company,
        "n_postings": n,
        "first_date": postings[0].posted if postings else None,
        "last_date": postings[-1].posted if postings else None,
        "demand": dict(sorted(demand.items(), key=lambda kv: (-kv[1], sk.name(kv[0])))),
        "trend": trend,
        "postings": [
            {"date": p.posted.isoformat(), "title": p.title, "file": p.path.name, "skills": sorted(p.skills)}
            for p in postings
        ],
    }


def demand_frame(profile: dict, top: int = 15) -> pd.DataFrame:
    rows = [
        {"Skill": sk.name(s), "Category": sk.load_skills()[s]["category"], "Demand %": round(w * 100)}
        for s, w in list(profile["demand"].items())[:top]
    ]
    return pd.DataFrame(rows, columns=["Skill", "Category", "Demand %"])


def trend_frame(profile: dict, top: int = 6) -> pd.DataFrame:
    """Trend table for the top skills, with skill names as columns and % values."""
    trend = profile["trend"]
    if trend.empty:
        return trend
    ids = [s for s in profile["demand"] if s in trend.columns][:top]
    out = (trend[ids] * 100).round()
    out.columns = [sk.name(s) for s in ids]
    return out


def rising_falling(profile: dict, threshold: float = 0.25) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    """Skills whose demand moved by at least `threshold` between the first and latest quarter."""
    trend = profile["trend"]
    if trend.empty or len(trend.index) < 2:
        return [], []
    first, last = trend.iloc[0], trend.iloc[-1]
    delta = (last - first).sort_values()
    rising = [(s, float(v)) for s, v in delta[::-1].items() if v >= threshold]
    falling = [(s, float(v)) for s, v in delta.items() if v <= -threshold]
    return rising, falling
