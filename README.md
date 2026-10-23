# 🌉 SkillBridge AI

**Bridge your skills to the company you want: a personal roadmap built from what that company is actually hiring for.**

🏆 **Track:** Best Open-Source AI Project · Hacktoberfest Hack Day Bengaluru 2026 (AWS Student Builder Group, Atria Institute of Technology)
🧠 **Model:** Qwen2.5-7B (Apache 2.0), running locally via Ollama · 📄 **License:** [MIT](LICENSE)

---

## ❗ The problem

Colleges teach a fixed set of tools from year one, and students build their resumes around them. But every company hires for a **different** skill set, and that skill set **keeps changing**.

So students don't know what a *specific* company expects today, and spend months learning the wrong things. Generic roadmaps like roadmap.sh show **everyone the same path**.

## ✅ Our solution

SkillBridge AI is a **100% open-source, local-first career agent**:

1. It reads a company's **real job descriptions** to learn what that company expects.
2. It compares that with the student's **resume** (and college subjects).
3. It builds a **personal learning roadmap** to close the gap, so students focus only on the skills that matter for the company and role they want.

## ✨ Features

| Feature | What it does |
|---|---|
| 🚀 **Landing page** | Animated intro with live stats from the data, then one click into the app |
| 📡 **Company Skill Radar** | Shows which skills a company asks for, as the % of its job descriptions that mention each one |
| 👔 **Role selection** | Filters the company's requirements for a path: fresher, frontend, backend, data/AI, QA, DevOps, senior or engineering manager. It only selects skills that actually appear in that company's job descriptions |
| 📈 **Hiring trends** | Job descriptions carry a date, so you see rising and falling skills by quarter |
| 🎯 **Match score + focus list** | An animated match score and the top 5 skills to learn, ranked by how much the company asks for them |
| 🗺️ **Personal roadmap** | A roadmap.sh-style graph from what you know to what they want, prerequisites first |
| 🔄 **Tool Translator** | The local AI explains how your current skills carry over to each new one |
| ✅ **Progress tracker** | Tick skills as you learn them and watch your match score rise |
| 📘 **Free resources** | Every step links to hand-picked free learning material, so there are no made-up links |

## 🔓 Why it's open-source AI

- **Open-weight model doing real work:** Qwen2.5-7B (Apache 2.0) extracts skills, tailors requirements to a role, and writes the Tool Translator explanations.
- **Runs locally through Ollama:** no paid or closed AI API.
- **Private by design:** resumes never leave the device, and the app works with Wi-Fi off.
- **Agent skill:** the core logic is packaged as [`skill/company-skill-gap/SKILL.md`](skill/company-skill-gap/SKILL.md), following the Agent Skill Open Standard, so any AI agent can reuse it.
- **MIT licensed:** any college, placement cell or bootcamp can deploy and extend it for free.

## ⚙️ How it works

```
Company job descriptions ─┐                       ┌─► Company profile (demand % per skill + trend)
                          ├─► Skill extraction ───┤          │
Your resume + subjects ───┘   keywords on a fixed │          ├─► Role filter (only skills found in the JDs)
                              list of 62 skills   │          │
                              + local open model  └─► Your skills (editable in the UI)
                              (cached)                       │
                                                             ▼
                                      Gap analysis (pure math) ─► match score + top 5 focus list
                                                             │
                                                             ▼
                                      Personal roadmap ─► graph + Tool Translator + free resources
```

### 🧮 How the match score works

The AI reads documents; **the score is plain math**, so it's the same on every run.

- **Demand** = the share of the company's job descriptions that ask for a skill.
- A skill counts as "expected" if its demand is **20% or more**.
- **Match score** = (sum of demand for expected skills you have) ÷ (sum of demand for all expected skills) × 100.

**Example:** Docker is asked for in 100% of postings, Kubernetes 50%, Python 50%. You have only Python, so 0.5 ÷ 2.0 = **25%**. Learn Docker and it becomes 1.5 ÷ 2.0 = **75%**.

### 🛡️ Design choices for reliable AI

- **Fixed skill list** (`data/skills.json`): "K8s", "Kubernetes" and "kubernetes" all count as one skill.
- **The model can only pick from that list**, so it can't invent skills or requirements.
- **Editable skills:** if extraction misses something, the student fixes it in the UI.
- **Graceful fallback:** if Ollama is off, keyword matching still works.
- **Caching:** each job description is read by the model once, so the demo is instant.

## 🧰 Tech stack

Qwen2.5-7B via **Ollama** · **Python** · **Streamlit** · **pandas** · **Graphviz** · **pypdf** · SKILL.md agent skill · GitHub (MIT)

---

## 🚀 Run it locally

**You need:** Python 3.10+, Git and [Ollama](https://ollama.com/download).

```bash
# 1. Get the open model (about 4.7 GB)
ollama pull qwen2.5:7b

# 2. Get the code
git clone https://github.com/laasyachiru/Grace.git
cd Grace

# 3. Install
python -m venv .venv
# Windows:      .venv\Scripts\Activate.ps1
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

Open <http://localhost:8501>, click **Get started**, pick a company and role, choose a sample resume, then click **Analyze my skills**.

**Weaker laptop?** Run `ollama pull qwen2.5:1.5b` and set `SKILLBRIDGE_MODEL=qwen2.5:1.5b` before starting the app.

**Other commands:**
```bash
python -m pytest -q                 # core tests (no AI needed)
python scripts/process_jobs.py      # pre-read all job descriptions so the app loads instantly
python skill/company-skill-gap/scripts/skill_gap.py --jobs data/jobs/google --resume data/samples/sample_resume.txt
                                    # run the agent skill directly (prints a JSON report)
```

## 📂 Project structure

```
app.py                          Streamlit app: landing page, Company Radar, My Gap, My Roadmap
skillbridge/
  extract.py                    Text → skills (keywords + local model)
  company.py                    Company profiles, demand %, trends, cache
  roles.py                      Role filter (selects only from skills found in the job descriptions)
  gap.py                        Match score + focus list (pure math)
  roadmap.py                    Learning order + roadmap graph
  translator.py                 Tool Translator prompts
  skills.py · llm.py · resume.py · progress.py · config.py
  ui.py                         Theme, animations, landing page
data/
  skills.json                   62 skills: aliases, prerequisites, free resources
  jobs/<company>/               Job descriptions per company
  samples/                      Sample resumes for the demo
skill/company-skill-gap/        Agent skill: SKILL.md + script
tests/                          Core tests
```

## 📊 Data

- Job descriptions for **Amazon, Apple, Flipkart, Google, Meta, Myntra, Swiggy and Zepto**, copied by hand from public job postings, plus two **sample** companies used to demonstrate trends.
- To add a company, create `data/jobs/<company>/` and save each posting as `YYYY-MM-DD_role-title.txt`. Postings from different months enable the trend chart.
- Sample resumes in `data/samples/` are for demonstration only.

## ⚠️ Limitations (honestly)

- The dataset is small today: a few job descriptions per company, so demand percentages are indicative.
- Trends need postings spread over several months.
- A local model is slower than cloud AI, so we pre-process and cache.

## 🔭 What's next

- Automatic job description collection from public career pages (respecting each site's terms)
- More companies and a community-maintained skill list
- University syllabus mapping (VTU first)
- A mobile app with the model running on the phone

## 👥 Team

| Name | Role |
|---|---|
| _Name_ | AI lead: extraction, Tool Translator, agent skill |
| _Name_ | Logic lead: skill list, scoring, roadmap |
| _Name_ | Frontend: UI, landing page |
| _Name_ | Product lead: data, demo, documentation |

## 🙏 Credits and transparency

- Open model: [Qwen2.5](https://huggingface.co/Qwen) (Apache 2.0) via [Ollama](https://ollama.com). UI: [Streamlit](https://streamlit.io). PDF reading: [pypdf](https://pypi.org/project/pypdf/).
- Learning resources link to their original free sources (official docs, roadmap.sh, MDN and others).
- Parts of the starter code and UI were drafted with an AI assistant (Claude) and then built on, tuned and extended by the team.

## 📄 License

[MIT](LICENSE): free to use, modify and share.
