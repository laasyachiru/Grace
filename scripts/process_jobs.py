"""Pre-process every company's job descriptions so the demo is instant.

Run this after adding new job descriptions (and once before the demo):
  python scripts/process_jobs.py          # uses the local model if Ollama is running
  python scripts/process_jobs.py --no-ai  # keyword matching only
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skillbridge import company, config, llm  # noqa: E402
from skillbridge import skills as sk  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-ai", action="store_true")
    args = ap.parse_args()

    use_ai = not args.no_ai and llm.ai_ready()
    print(f"Mode: {'AI (' + config.MODEL + ')' if use_ai else 'keyword only'}")
    if not args.no_ai and not use_ai:
        print(f"  (Ollama or model '{config.MODEL}' not available, falling back to keywords)")

    for name in company.list_companies():
        t = time.time()
        profile = company.build_profile(name, use_ai=use_ai)
        top = ", ".join(f"{sk.name(s)} {round(w * 100)}%" for s, w in list(profile["demand"].items())[:6])
        print(f"\n{company.display_name(name)}: {profile['n_postings']} JDs in {time.time() - t:.1f}s")
        print(f"  Top skills: {top}")


if __name__ == "__main__":
    main()
