"""Tool Translator: explain how what the student already knows carries over to a new skill."""

from __future__ import annotations

from typing import Iterator

from . import llm
from . import skills as sk

TRANSLATOR_SYSTEM = (
    "You are a friendly, practical career mentor for Indian engineering students. "
    "Explain how skills they already have transfer to a new tool. Be specific and encouraging, "
    "use simple English, and never invent facts about any company."
)


def build_prompt(target: str, known: list[str], company: str) -> str:
    known_txt = ", ".join(known) if known else "basic programming from college"
    return (
        f"The student already knows: {known_txt}.\n"
        f"Their target company ({company}) expects: {target}.\n\n"
        "In 4 short bullet points:\n"
        f"1. Which of their existing skills or concepts carry over to {target}, and how.\n"
        f"2. What is genuinely new about {target}.\n"
        "3. A first hands-on mini-project they can finish in a weekend.\n"
        f"4. One line on how to describe {target} learning on their resume once done."
    )


def explain_stream(target_id: str, known_ids: set[str], company: str) -> Iterator[str]:
    prompt = build_prompt(sk.name(target_id), sk.names(known_ids), company)
    yield from llm.stream_text(TRANSLATOR_SYSTEM, prompt)


def fallback(target_id: str, known_ids: set[str]) -> str:
    """Rule-based explanation used when the local model is offline."""
    name = sk.name(target_id)
    bridges = [sk.name(p) for p in sk.prereqs(target_id) if p in known_ids]
    if bridges:
        return (
            f"**{name}** builds directly on what you already know: **{', '.join(bridges)}**. "
            f"Start from those concepts, then follow the free resources below."
        )
    return f"**{name}** is new for you. Start with the first free resource below and build one small project."
