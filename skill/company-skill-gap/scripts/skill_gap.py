"""CLI behind the company-skill-gap agent skill. Prints a JSON report.

Example (from the repo root):
  python skill/company-skill-gap/scripts/skill_gap.py --jobs data/jobs/sample-cloudnova --resume data/samples/sample_resume.txt
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from skillbridge import company, gap, roadmap  # noqa: E402
from skillbridge import skills as sk  # noqa: E402
from skillbridge.extract import extract_skills  # noqa: E402
from skillbridge.resume import read_path  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Company skill gap report")
    ap.add_argument("--jobs", required=True, help="Folder with the company's job description files")
    ap.add_argument("--resume", required=True, help="Resume file (.pdf, .txt, .md)")
    ap.add_argument("--no-ai", action="store_true", help="Keyword matching only (no local model)")
    args = ap.parse_args()

    jobs = Path(args.jobs).resolve()
    if not jobs.is_dir():
        print(json.dumps({"error": f"Not a folder: {jobs}"}))
        return 1

    use_ai = not args.no_ai
    profile = company.build_profile(jobs.name, use_ai=use_ai, jobs_dir=jobs.parent)
    mine = extract_skills(read_path(args.resume), use_ai=use_ai)
    result = gap.analyze(profile["demand"], mine)
    path = roadmap.learning_path(result.focus, mine)

    report = {
        "company": company.display_name(jobs.name),
        "job_descriptions_analysed": profile["n_postings"],
        "match_score": result.score,
        "company_expects": {sk.name(s): round(w, 2) for s, w in profile["demand"].items()},
        "you_have": [sk.name(s) for s in result.matched],
        "focus": [sk.name(s) for s in result.focus],
        "learning_path": [
            {"step": i, "skill": sk.name(s), "resources": sk.resources(s)} for i, s in enumerate(path, 1)
        ],
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
