"""Role-aware views over the skills evidenced by a company's job descriptions.

Role filtering only selects from skills already found in that company's postings;
it never invents or adds requirements that the source data does not support.
"""

from __future__ import annotations

from . import llm
from . import skills as sk

ROLE_OPTIONS = [
    "Company core requirements",
    "Fresher / Entry-level",
    "Frontend Engineer",
    "Backend Engineer",
    "Data Analyst / AI Engineer",
    "QA / Test Engineer",
    "DevOps / Cloud Engineer",
    "Senior / Tech Lead",
    "Engineering Manager",
]

_FAMILY_SKILLS = {
    "Frontend Engineer": {
        "javascript", "typescript", "html-css", "react", "angular", "nodejs",
        "graphql", "rest-api", "api-testing", "playwright", "git", "dsa", "oop",
        "networking", "security", "system-design",
    },
    "Backend Engineer": {
        "python", "java", "csharp", "go", "nodejs", "rest-api", "graphql",
        "dotnet", "aspnet-core", "ef-core", "spring-boot", "django", "fastapi",
        "microservices", "sql", "postgresql", "mysql", "oracle-db", "sql-server",
        "mongodb", "redis", "kafka", "docker", "git", "dsa", "oop", "networking",
        "security", "system-design", "unit-testing",
    },
    "Data Analyst / AI Engineer": {
        "python", "sql", "pandas", "machine-learning", "deep-learning", "genai",
        "bi-reporting", "spark", "kafka", "dsa", "git", "system-design",
    },
    "QA / Test Engineer": {
        "manual-testing", "api-testing", "selenium", "playwright", "test-automation",
        "unit-testing", "performance-testing", "python", "java", "javascript",
        "typescript", "sql", "git", "cicd", "jenkins", "github-actions", "docker",
    },
    "DevOps / Cloud Engineer": {
        "linux", "networking", "python", "bash", "git", "aws", "azure", "gcp",
        "docker", "kubernetes", "cicd", "github-actions", "jenkins", "terraform",
        "ansible", "monitoring", "security", "production-support", "microservices",
    },
    "Engineering Manager": {
        "agile", "system-design", "security", "monitoring", "production-support",
        "cicd",
    },
}

_ROLE_GUIDANCE = {
    "Fresher / Entry-level": "Select skills suitable as entry-level requirements; prefer fundamentals and skills explicitly requested, and avoid treating senior ownership as a prerequisite.",
    "Frontend Engineer": "Select skills relevant to building and maintaining frontend and browser applications.",
    "Backend Engineer": "Select skills relevant to backend services, APIs, databases, and service reliability.",
    "Data Analyst / AI Engineer": "Select skills relevant to data analysis, BI, machine learning, and data engineering.",
    "QA / Test Engineer": "Select skills relevant to software quality, test design, and test automation.",
    "DevOps / Cloud Engineer": "Select skills relevant to infrastructure, cloud platforms, deployment, and observability.",
    "Senior / Tech Lead": "Select the technical skills most relevant to senior technical ownership, architecture, reliability, and delivery.",
    "Engineering Manager": "Select only technical requirements relevant to engineering management, architecture, delivery, and operational oversight. The catalog does not represent people-management skills.",
}


def filter_requirements(
    demand: dict[str, float],
    role: str,
    posting_titles: list[str] | None = None,
    use_ai: bool = True,
) -> set[str]:
    """Choose a role-relevant subset from company requirements, with a safe fallback."""
    available = set(demand)
    if role == ROLE_OPTIONS[0]:
        return available

    family = _FAMILY_SKILLS.get(role)
    candidates = available & family if family is not None else available
    if role == "Senior / Tech Lead":
        senior = {"system-design", "microservices", "security", "monitoring", "cicd", "kubernetes", "terraform", "production-support"}
        narrowed = candidates & senior
        candidates = narrowed or candidates
    if not candidates:
        return set()

    # When the local model is unavailable or switched off, use the conservative
    # role-family match above and leave broad levels inclusive rather than guess.
    if not use_ai or not llm.ai_ready():
        return candidates

    allowed = [
        {"id": sid, "name": sk.name(sid), "demand": round(demand[sid], 3)}
        for sid in sorted(candidates)
    ]
    system = (
        "You tailor company job requirements to a selected candidate role. "
        "Choose only skill ids from the supplied candidate list; never invent skills. "
        "Keep the selection useful and inclusive, and do not remove ordinary must-haves. "
        'Reply as JSON: {"skills": ["skill-id", ...]}.'
    )
    user = (
        f"Selected role: {role}.\n{_ROLE_GUIDANCE.get(role, '')}\n"
        f"Job titles in the company's source data: {', '.join(posting_titles or []) or 'not provided'}.\n"
        f"Candidate requirements (only these may be returned): {allowed}\n"
        "Return the subset that is relevant to this role."
    )
    result = llm.chat_json(system, user)
    if not result or not isinstance(result.get("skills"), list):
        return candidates
    selected = sk.normalize(result["skills"]) & candidates
    return selected or candidates
