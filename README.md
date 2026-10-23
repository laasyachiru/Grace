# 🌉 SkillBridge AI

**Your personal roadmap to the company you want, built from what they're actually hiring for.**

Track: **Best Open-Source AI Project** · Hacktoberfest Hack Day Bengaluru 2026 (AWS Student Builder Group, Atria) · License: **MIT**

---

## The problem

Colleges teach a fixed set of tools from year one, and students build their resumes around them. But every company hires for a different skill set, and that skill set keeps changing. Students don't know what a *specific* company expects today, so they spend months learning the wrong things. Generic roadmaps (like roadmap.sh) show everyone the same path.

## What SkillBridge AI does

| Feature | What it means |
|---|---|
| 📡 **Company Skill Radar** | Reads a company's real job descriptions and shows what it expects, e.g. *AWS 100%, Docker 67%* |
| 📈 **Hiring trends** | Every job description has a date, so you see which skills are rising or falling over time |
| 🎯 **Focus list** | Compares your resume (and college subjects) with the company and ranks the top 5 skills to learn |
| 👔 **Role selection** | Starts from the combined requirements in a company's job descriptions and filters them for a selected path, such as fresher, frontend, QA, DevOps, or engineering manager |
| 🗺️ **Personal roadmap** | A roadmap.sh-style graph from what you know to what they want, prerequisites first |
| 🔄 **Tool Translator** | The local AI explains how your current skills carry over to each new one |
| ✅ **Progress tracker** | Tick skills as you learn them and watch your match score rise (like Codecademy) |
| 📘 **Free resources only** | Every step links to hand-picked free learning material (no made-up links) |

## Why it's open-source AI

- **Open-weight model:** `qwen2.5:7b` (Apache 2.0), running **locally** through [Ollama](https://ollama.com). No paid or closed API.
- **Privacy first:** resumes never leave the device. It even works with Wi-Fi off.
- **Reliable by design:** the model picks skills only from a fixed list (`data/skills.json`) and **scores are calculated in code**, so results are the same on every run.
- **Agent skill:** the core logic is packaged as `skill/company-skill-gap/SKILL.md` (Agent Skill Open Standard), so any AI agent can reuse it.
- **MIT licensed:** any college, placement cell or bootcamp can deploy it for free.

## How it works

```
Company job descriptions (data/jobs/<company>/YYYY-MM-DD_role.txt)
        │
        ▼
 Skill extraction ── keyword match on fixed skill list  +  local open model (Ollama)
        │                                   (cached in data/cache/ so each file is read once)
        ▼
 Company profile: demand % per skill + trend per quarter
        │
        ├── Role selection ──► role-relevant subset of skills supported by those job descriptions
        │
Your resume / subjects ──► your skills (editable in the UI)
        │
        ▼
 Gap analysis (pure math) ──► match score + focus list
        │
        ▼
 Roadmap (prerequisite map) ──► Graphviz graph + Tool Translator (local model) + free resources
```

The role filter can use Ollama when the local model is enabled. It only selects from
skills already detected in that company's job descriptions; it does not create new
company requirements. If there are no postings for a selected role, add relevant job
descriptions to that company's folder to provide evidence for the filter.

---

## 🚀 Setup (every teammate, ~10 minutes)

### 1. Install the basics
- **Python 3.10 or newer**: <https://www.python.org/downloads/> (Windows: tick **"Add Python to PATH"** during install)
- **Git**: <https://git-scm.com/downloads>
- **Ollama**: <https://ollama.com/download> (install, then open it once so it runs in the background)

### 2. Pull the open model (do this first, it downloads ~4.7 GB)
```bash
ollama pull qwen2.5:7b
```
On a weaker laptop (less than 16 GB RAM), use the smaller model instead:
```bash
ollama pull qwen2.5:1.5b
```
Then tell the app to use it before running (see step 5):
- macOS/Linux: `export SKILLBRIDGE_MODEL=qwen2.5:1.5b`
- Windows PowerShell: `$env:SKILLBRIDGE_MODEL="qwen2.5:1.5b"`

> Both models are Apache 2.0. Avoid the 3B Qwen variants: they use a restricted research license.

### 3. Get the code
Download and unzip the project (or clone the team repo once it's on GitHub), then open a terminal in the `skillbridge-ai` folder.

### 4. Create a virtual environment and install packages
**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
> If PowerShell blocks activation: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.

### 5. Run the app
```bash
streamlit run app.py
```
It opens at <http://localhost:8501>. Pick a company → tick **Use sample resume** → click **Analyze my skills**.

### 6. Check everything works
```bash
python -m pytest -q                      # 7 tests, no AI needed
python scripts/process_jobs.py           # reads all job descriptions (uses AI if Ollama is running)
```

### Open it on a phone (for the demo)
Connect the laptop and phone to the **same phone hotspot** (college Wi-Fi often blocks device-to-device traffic), then:
```bash
streamlit run app.py --server.address 0.0.0.0
```
On the phone, open `http://<laptop-IP>:8501` (find the IP with `ipconfig` on Windows or `ifconfig` / `ip a` on macOS/Linux). Allow Python through the firewall if asked.

---

## 📁 Project structure and owners

| Path | What it does | Owner |
|---|---|---|
| `app.py` | Streamlit UI: sidebar, 3 tabs (Radar, Gap, Roadmap) | **Frontend** |
| `skillbridge/config.py` | Settings: model name, thresholds, paths | Anyone (agree first) |
| `skillbridge/llm.py` | Talks to Ollama; fails soft if it's offline | **AI lead** |
| `skillbridge/extract.py` | Text → skills (keywords + local model), extraction prompt | **AI lead** |
| `skillbridge/translator.py` | Tool Translator prompt + offline fallback | **AI lead** |
| `skill/company-skill-gap/` | The agent skill: `SKILL.md` + CLI script | **AI lead** |
| `skillbridge/skills.py` | Loads the skill list, keyword matching, alias cleanup | **Logic lead** |
| `data/skills.json` | ~60 skills: aliases, prerequisites, free resources | **Logic lead** |
| `skillbridge/company.py` | Company profiles, demand %, trends, extraction cache | **Logic lead** |
| `skillbridge/gap.py` | Match score + focus list (pure math) | **Logic lead** |
| `skillbridge/roadmap.py` | Learning order + Graphviz roadmap | **Logic lead** |
| `skillbridge/progress.py` | Saves ticked skills to `data/progress.json` | **Logic lead** |
| `skillbridge/resume.py` | Reads PDF / TXT resumes | **Logic lead** |
| `data/jobs/` | Real job descriptions per company | **Product lead** |
| `data/samples/` | Sample resume for testing/demo | **Product lead** |
| `scripts/process_jobs.py` | Pre-processes all job descriptions (run before demo) | **Product lead** |
| `tests/test_core.py` | Core tests | **Logic lead** |
| `README.md`, `LICENSE` | Docs + MIT license | **Product lead** |

---

## 👥 Who does what

The starter code already works end to end with sample data. Each person **improves their part** without touching the others' files.

### 🧠 AI lead: `extract.py`, `translator.py`, `llm.py`, `skill/`
- [ ] Ollama running, `qwen2.5:7b` pulled, sidebar shows **"Local model ready"**
- [ ] Test extraction on real job descriptions; tune `EXTRACT_SYSTEM` in `extract.py` if it misses or invents skills
- [ ] Tune the Tool Translator prompt in `translator.py` (keep answers short and practical)
- [ ] Run the agent skill script and check the JSON:
      `python skill/company-skill-gap/scripts/skill_gap.py --jobs data/jobs/<company> --resume data/samples/sample_resume.txt`
- [ ] Check `SKILL.md` against the Agent Skill Open Standard
- [ ] Demo prep: show the same skill being used by an agent

### 🧮 Logic lead: `skills.json`, `skills.py`, `company.py`, `gap.py`, `roadmap.py`
- [ ] Add any skills that appear in the real job descriptions but are missing from `data/skills.json`
      (each needs `id`, `name`, `category`, `aliases`, `prereqs`, `resources`; only add **real** free URLs)
- [ ] Check prerequisites make sense (e.g. Linux → Docker → Kubernetes)
- [ ] Tune `MIN_DEMAND` / `FOCUS_COUNT` in `config.py` if the focus list looks off
- [ ] Keep `python -m pytest -q` passing after every change

### 🎨 Frontend: `app.py`
- [ ] Polish the 3 tabs: spacing, headings, colours, wording
- [ ] Make it look good on a phone (test over the hotspot)
- [ ] Optional: a bar chart comparing your skills with the company, or company logos
- [ ] Optional: a "compare two companies" view

### 📣 Product lead: `data/jobs/`, README, demo, submission
- [ ] **Most urgent:** collect 5–8 real job descriptions for each of 3 target companies (see below)
- [ ] Prepare 1–2 demo resumes (get permission or remove personal details)
- [ ] Run `python scripts/process_jobs.py` so the demo is instant
- [ ] Record a 90-second backup demo video at 4:15
- [ ] Final README polish, then **submit on MLH at 5:00**: Best Open-Source AI Project

---

## ➕ Adding real job descriptions

1. Create a folder per company in `data/jobs/`, lowercase with dashes: `data/jobs/infosys/`, `data/jobs/zoho/`
2. Save each job description as a text file named **`YYYY-MM-DD_role-title.txt`**, using the posting date:
   ```
   data/jobs/zoho/2026-09-12_software-developer.txt
   data/jobs/zoho/2026-10-03_qa-automation-engineer.txt
   ```
3. Paste the full job description text inside (copy from the company's careers page).
4. Run `python scripts/process_jobs.py`, then refresh the app.

Tips: postings from **different months** make the trend chart work. Delete the `sample-*` folders before the final demo if you have enough real data. Collect job descriptions by copying them by hand; don't scrape sites.

## ➕ Adding a skill to `data/skills.json`
```json
{"id": "fastapi", "name": "FastAPI / Flask", "category": "Backend",
 "aliases": ["FastAPI", "Flask"], "prereqs": ["python", "rest-api"],
 "resources": [{"title": "FastAPI tutorial", "url": "https://fastapi.tiangolo.com/tutorial/"}]}
```
Avoid very short or common aliases ("Go", "R", "Node") because they cause false matches. Prerequisites must be ids that already exist.

---

## 🌿 Git workflow (so nobody overwrites each other)

1. One person creates the GitHub repo (**public**, MIT license already included) and pushes this starter.
2. Everyone clones it and works on **their own branch**: `git checkout -b ai-lead` (or `logic`, `frontend`, `product`).
3. Commit small and often: `git add -A && git commit -m "Tune extraction prompt"`.
4. Every ~45 minutes: `git pull origin main`, then merge your branch into `main` and push.
5. Stick to your own files (see the table above). Only edit `config.py` after telling the team.

---

## ⏱️ Timeline for today

| Time | Goal |
|---|---|
| 12:45–1:15 | Everyone set up, app running with sample data, repo on GitHub |
| 1:15–2:30 | Real job descriptions added, extraction tuned (lunch in turns) |
| 2:30–3:30 | Skills/prereqs tuned, UI polish, Tool Translator tuned |
| 3:30–4:00 | Agent skill checked, extras if time |
| 4:00–4:30 | README final, backup video, rehearse the demo twice |
| **4:30** | **Code freeze** |
| **5:00** | **Submit on MLH: Best Open-Source AI Project** |
| 5:30 | Judging starts |

---

## 🎬 Demo script (2 minutes)

1. **Hook:** "My college taught me manual testing. The company I want is hiring for something else. What exactly?"
2. **Company Radar:** pick the company, show its top skills, then the trend chart ("Kubernetes is rising").
3. **My Gap:** analyze the resume. "You match 52%. Focus on just these 5 skills."
4. **My Roadmap:** walk the graph from what you know to what they want, then click **Tool Translator** on one step.
5. **Progress:** tick a skill and the match score jumps live.
6. **Open source proof:** turn Wi-Fi off and it still works. Show `SKILL.md` and the MIT license on GitHub.

**Close:** "roadmap.sh shows everyone the same roadmap. SkillBridge builds yours, for the company you want, from what they're actually hiring for."

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| Sidebar says "Ollama isn't running" | Open the Ollama app, then click **Re-check model** |
| "Model not found" | Run `ollama pull qwen2.5:7b` (or set `SKILLBRIDGE_MODEL` to the model you pulled) |
| First load is slow | The model is reading every job description once. Run `python scripts/process_jobs.py` beforehand; results are cached |
| Results look stale after editing a job file | Refresh the page; the cache updates automatically when files change. To force it, delete `data/cache/` |
| `streamlit: command not found` | Activate the virtual environment first, or use `python -m streamlit run app.py` |
| Phone can't open the app | Use a phone hotspot, run with `--server.address 0.0.0.0`, allow the firewall prompt |
| Resume PDF shows no skills | Scanned PDFs have no text layer; use a text-based PDF or paste skills in the subjects box |

---

## 🔭 What's next
- Automatic collection of job descriptions from public career pages (respecting each site's terms)
- More companies and roles, shared community skill list
- Syllabus mapping for every university (VTU first)
- A mobile app with the model running on the phone itself

## 🙏 Credits and transparency
- Open model: Qwen2.5 (Apache 2.0) via Ollama. UI: Streamlit. PDF reading: pypdf.
- Learning resources link to their original free sources (official docs, roadmap.sh, MDN and others).
- Starter code was drafted with the help of an AI assistant (Claude) and then built on by the team. This is noted here in line with hackathon transparency practice.

## 📄 License
[MIT](LICENSE): free to use, modify and share.
