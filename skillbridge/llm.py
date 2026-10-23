"""Thin wrapper around the local Ollama model.

Every function fails soft: if Ollama is not running, callers get None / a friendly message
and the app keeps working in keyword-only mode.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Iterator

from . import config

try:
    import ollama
except ImportError:  # app still runs without the package (keyword mode)
    ollama = None


@lru_cache(maxsize=1)
def is_available() -> bool:
    """True if the Ollama server answers. Cached; call is_available.cache_clear() to re-check."""
    if ollama is None:
        return False
    try:
        ollama.list()
        return True
    except Exception:
        return False


def list_models() -> list[str]:
    """Names of models pulled into Ollama, e.g. ['qwen2.5:7b']."""
    if ollama is None:
        return []
    try:
        resp = ollama.list()
    except Exception:
        return []
    models = resp.get("models", []) if isinstance(resp, dict) else getattr(resp, "models", [])
    names = []
    for m in models:
        if isinstance(m, dict):
            names.append(m.get("model") or m.get("name"))
        else:
            names.append(getattr(m, "model", None) or getattr(m, "name", None))
    return [n for n in names if n]


def model_installed(model: str | None = None) -> bool:
    model = model or config.MODEL
    names = list_models()
    return any(n == model or n == f"{model}:latest" or n.split(":")[0] == model for n in names)


def ai_ready() -> bool:
    return is_available() and model_installed()


def chat_json(system: str, user: str, model: str | None = None, retries: int = 1) -> dict | None:
    """Ask the model for a JSON object. Returns a dict, or None if anything fails."""
    if ollama is None:
        return None
    for _ in range(retries + 1):
        try:
            resp = ollama.chat(
                model=model or config.MODEL,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                format="json",
                options={"temperature": 0},
            )
            data = json.loads(resp["message"]["content"])
            if isinstance(data, dict):
                return data
        except Exception:
            continue
    return None


def stream_text(system: str, user: str, model: str | None = None) -> Iterator[str]:
    """Yield the model's answer piece by piece (for st.write_stream)."""
    if ollama is None:
        yield "The `ollama` package is not installed, so the AI explanation is unavailable."
        return
    try:
        for chunk in ollama.chat(
            model=model or config.MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            stream=True,
            options={"temperature": 0.3},
        ):
            yield chunk["message"]["content"]
    except Exception as exc:
        yield f"\n\n_Could not reach the local model ({exc}). Is Ollama running?_"
