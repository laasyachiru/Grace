"""Central settings. Change values here (or via environment variables) instead of hard-coding them."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
JOBS_DIR = DATA_DIR / "jobs"
CACHE_DIR = DATA_DIR / "cache"
SKILLS_FILE = DATA_DIR / "skills.json"
PROGRESS_FILE = DATA_DIR / "progress.json"
SAMPLE_RESUME = DATA_DIR / "samples" / "sample_resume.txt"

# Local open-weight model served by Ollama. Override with: SKILLBRIDGE_MODEL=qwen2.5:1.5b
MODEL = os.getenv("SKILLBRIDGE_MODEL", "qwen2.5:7b")

# A skill counts as "expected by the company" if it appears in at least this share of its job descriptions.
MIN_DEMAND = float(os.getenv("SKILLBRIDGE_MIN_DEMAND", "0.2"))

# How many skills go into the "focus on these" list.
FOCUS_COUNT = int(os.getenv("SKILLBRIDGE_FOCUS_COUNT", "5"))

# Max characters of a document sent to the model (keeps local inference fast).
MAX_DOC_CHARS = 6000
