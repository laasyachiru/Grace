"""Core logic tests (no AI needed). Run:  python -m pytest -q"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skillbridge import company, config, gap, roadmap  # noqa: E402
from skillbridge import skills as sk  # noqa: E402


def test_skills_file_is_valid():
    skills = sk.load_skills()
    assert len(skills) >= 50
    for sid, s in skills.items():
        for p in s["prereqs"]:
            assert p in skills, f"{sid} has unknown prereq {p}"
        assert s["resources"], f"{sid} has no resources"


def test_keyword_extraction_handles_tricky_names():
    found = sk.find_by_keyword("Experience with C#, ASP.NET Core, K8s, Node.js and PostgreSQL. JavaScript a plus.")
    assert {"csharp", "aspnet-core", "kubernetes", "nodejs", "postgresql", "javascript"} <= found
    assert "java" not in found          # JavaScript must not count as Java
    assert "sql" not in found           # PostgreSQL must not count as plain SQL


def test_normalize_maps_aliases():
    assert sk.normalize(["K8s", "Postman", "made-up tool"]) == {"kubernetes", "api-testing"}


def test_gap_math():
    demand = {"docker": 1.0, "kubernetes": 0.5, "python": 0.5, "rare": 0.1}
    res = gap.analyze(demand, {"python"}, min_demand=0.2, top_n=5)
    assert res.score == 25              # 0.5 / (1.0 + 0.5 + 0.5)
    assert res.focus == ["docker", "kubernetes"]
    learned = gap.analyze(demand, {"python"}, done={"docker"}, min_demand=0.2)
    assert learned.score == 75


def test_learning_path_orders_prerequisites():
    path = roadmap.learning_path(["kubernetes"], have=set())
    assert path.index("linux") < path.index("docker") < path.index("kubernetes")
    assert roadmap.learning_path(["kubernetes"], have={"linux", "docker"}) == ["kubernetes"]
    dot = roadmap.to_dot(path, have=set(), done=set(), focus={"kubernetes"})
    assert dot.startswith("digraph") and "Kubernetes" in dot


def test_sample_company_profile_and_trend():
    profile = company.build_profile("sample-cloudnova", use_ai=False)
    assert profile["n_postings"] == 6
    assert profile["demand"]["aws"] == 1.0
    rising, _ = company.rising_falling(profile)
    assert "kubernetes" in [s for s, _ in rising]


def test_sample_resume_against_sample_company():
    from skillbridge.resume import read_path

    mine = sk.find_by_keyword(read_path(config.SAMPLE_RESUME))
    assert {"manual-testing", "api-testing", "selenium", "java", "git"} <= mine
    profile = company.build_profile("sample-finedge", use_ai=False)
    res = gap.analyze(profile["demand"], mine)
    assert 0 < res.score < 100
    assert "playwright" in res.focus
