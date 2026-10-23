"""Codecademy-style progress: skills the student has ticked as learned, saved locally."""

from __future__ import annotations

import json

from . import config


def load_done() -> set[str]:
    try:
        return set(json.loads(config.PROGRESS_FILE.read_text(encoding="utf-8")).get("done", []))
    except Exception:
        return set()


def save_done(done: set[str]) -> None:
    config.PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.PROGRESS_FILE.write_text(json.dumps({"done": sorted(done)}, indent=2), encoding="utf-8")


def set_done(sid: str, value: bool) -> set[str]:
    done = load_done()
    (done.add if value else done.discard)(sid)
    save_done(done)
    return done


def reset() -> None:
    save_done(set())
