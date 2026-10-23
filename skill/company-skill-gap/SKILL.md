---
name: company-skill-gap
description: Find what a specific company expects from candidates by reading its job descriptions, compare that with a student's resume, and return a match score, a ranked "focus on these" skill list and an ordered learning path with free resources. Use when someone asks what skills a company wants, how ready their resume is for a company, or what to learn next for a target employer. Runs on a local open-weight model via Ollama (falls back to keyword matching).
license: MIT
compatibility: Requires Python 3.10+, the SkillBridge AI repository (this skill calls its `skillbridge` package), and optionally Ollama with an open model such as qwen2.5:7b.
metadata:
  project: SkillBridge AI
  version: "0.1.0"
---

# Company Skill Gap

Use this skill when a user wants to know **what a target company is hiring for** and **what they personally need to learn** to be ready for it.

## Inputs
- A folder of the company's job descriptions as `.txt` or `.md` files. Name them `YYYY-MM-DD_role.txt` so trends over time can be computed.
- The user's resume as a `.pdf`, `.txt` or `.md` file (or pasted text saved to a file).

## Steps
1. Run the script from the repository root:
   ```bash
   python skill/company-skill-gap/scripts/skill_gap.py --jobs data/jobs/<company> --resume path/to/resume.pdf
   ```
   Add `--no-ai` to skip the local model and use keyword matching only (faster, fully deterministic).
2. The script prints JSON with:
   - `match_score`: 0–100, weighted by how often the company asks for each skill
   - `company_expects`: skills with the share of job descriptions asking for each
   - `you_have` and `focus`: what the user already matches and the top skills to learn, most important first
   - `learning_path`: focus skills plus missing prerequisites, in learning order, each with free resources
3. Present the result to the user in this order: match score → focus list → learning path.
4. Be honest about the data: say how many job descriptions the profile was built from.

## Rules
- Only recommend skills that appear in the company's job descriptions or are prerequisites of them.
- Never invent company facts or salary data.
- Link only the resources returned by the script (they are hand-checked); do not make up URLs.
