"""Personal roadmap (roadmap.sh style): put the focus skills, plus any missing prerequisites,
in a valid learning order, and draw it as a Graphviz graph."""

from __future__ import annotations

from . import skills as sk


def learning_path(focus: list[str], have: set[str]) -> list[str]:
    """Focus skills plus missing prerequisites, prerequisites first, focus priority kept."""
    path: list[str] = []
    visiting: set[str] = set()

    def visit(sid: str) -> None:
        if sid in path or sid in have:
            return
        if sid in visiting:  # cycle guard (shouldn't happen with a clean skills.json)
            return
        visiting.add(sid)
        for p in sk.prereqs(sid):
            visit(p)
        visiting.discard(sid)
        path.append(sid)

    for sid in focus:
        visit(sid)
    return path


def _q(text: str) -> str:
    return '"' + text.replace('"', '\\"') + '"'


def to_dot(path: list[str], have: set[str], done: set[str], focus: set[str]) -> str:
    """Graphviz DOT for st.graphviz_chart.
    Green = you know it, blue = learned (ticked), red = company wants it, amber = prerequisite to learn first."""
    known = {p for sid in path for p in sk.prereqs(sid) if p in have}
    lines = [
        "digraph roadmap {",
        "  rankdir=LR; bgcolor=transparent; nodesep=0.35; ranksep=0.6;",
        '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=12, penwidth=0];',
        '  edge [color="#8a8f98", arrowsize=0.7];',
        '  start [label="You today", shape=oval, fillcolor="#e8eaf0", fontcolor="#333333"];',
        '  goal [label="Company ready", shape=oval, fillcolor="#1f2937", fontcolor="white"];',
    ]
    for sid in sorted(known):
        lines.append(f"  {_q(sid)} [label={_q(sk.name(sid))}, fillcolor=\"#d1fae5\", fontcolor=\"#065f46\"];")
    for i, sid in enumerate(path, 1):
        if sid in done:
            fill, font = "#dbeafe", "#1e3a8a"
        elif sid in focus:
            fill, font = "#fee2e2", "#991b1b"
        else:
            fill, font = "#fef3c7", "#92400e"
        lines.append(f"  {_q(sid)} [label={_q(f'{i}. {sk.name(sid)}')}, fillcolor=\"{fill}\", fontcolor=\"{font}\"];")

    shown = set(path) | known
    for sid in path:
        pres = [p for p in sk.prereqs(sid) if p in shown]
        if pres:
            for p in pres:
                lines.append(f"  {_q(p)} -> {_q(sid)};")
        else:
            lines.append(f"  start -> {_q(sid)};")
    for sid in sorted(known):
        lines.append(f"  start -> {_q(sid)} [style=dashed];")
    # Leaves (nothing in the path depends on them) lead to the goal.
    needed_by_others = {p for sid in path for p in sk.prereqs(sid)}
    for sid in path:
        if sid not in needed_by_others:
            lines.append(f"  {_q(sid)} -> goal;")
    if not path:
        lines.append("  start -> goal;")
    lines.append("}")
    return "\n".join(lines)
