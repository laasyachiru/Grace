"""Turn any text (job description, resume, syllabus) into a set of skill ids.

Two layers:
1. Keyword matching against the fixed skill list (instant, deterministic, works offline without a model).
2. The local open model (Ollama) adds skills that are clearly implied, chosen ONLY from the fixed list.
"""

from __future__ import annotations

from . import config, llm
from . import skills as sk

EXTRACT_SYSTEM = (
    "You extract technical skills from documents for a career tool. "
    "You may ONLY use skill names from the allowed list. "
    "Include a skill if it is explicitly mentioned or clearly required/used. "
    "Do not include soft skills. Do not invent skills. "
    'Reply with JSON only, in the form {"skills": ["Skill name", ...]}.'
)


def _allowed_list() -> str:
    return ", ".join(s["name"] for s in sk.load_skills().values())


def extract_with_ai(text: str) -> set[str]:
    prompt = (
        f"Allowed skills: {_allowed_list()}\n\n"
        f"Document:\n\"\"\"\n{text[: config.MAX_DOC_CHARS]}\n\"\"\"\n\n"
        "Return the JSON now."
    )
    result = llm.chat_json(EXTRACT_SYSTEM, prompt)
    if not result:
        return set()
    return sk.normalize(result.get("skills", []))


def extract_skills(text: str, use_ai: bool = True) -> set[str]:
    """Keyword skills, plus model-found skills when use_ai is True and Ollama is ready."""
    found = sk.find_by_keyword(text)
    if use_ai and llm.ai_ready():
        found |= extract_with_ai(text)
    return found
