"""SkillBridge AI: Streamlit app.

Run:  streamlit run app.py
Phone on the same hotspot:  streamlit run app.py --server.address 0.0.0.0
"""

import streamlit as st

from skillbridge import company, config, gap, llm, progress, roadmap, roles, translator, ui
from skillbridge import skills as sk
from skillbridge.extract import extract_skills
from skillbridge.resume import read_path, read_upload

st.set_page_config(page_title="SkillBridge AI", page_icon="🌉", layout="wide", initial_sidebar_state="expanded")
ui.apply_theme()


@st.cache_data(show_spinner=False)
def cached_profile(name: str, use_ai: bool, sig: tuple, model: str) -> dict:
    # sig and model are only here so the cache refreshes when job files or the model change.
    return company.build_profile(name, use_ai=use_ai)


@st.cache_data(show_spinner=False)
def cached_role_skills(name: str, role: str, demand_items: tuple, titles: tuple,
                       use_ai: bool, sig: tuple, model: str) -> list[str]:
    demand = dict(demand_items)
    return sorted(roles.filter_requirements(demand, role, list(titles), use_ai))


def pct(x: float) -> str:
    return f"{round(x * 100)}%"


def sample_resumes() -> list:
    folder = config.SAMPLE_RESUME.parent
    files = sorted(p for p in folder.glob("*") if p.suffix.lower() in {".txt", ".md", ".pdf"}) if folder.exists() else []
    # Only offer examples that can produce skills from the fixed catalog.
    usable = []
    for path in files:
        try:
            if sk.find_by_keyword(read_path(path)):
                usable.append(path)
        except Exception:
            continue
    return sorted(usable, key=lambda p: (p.name != config.SAMPLE_RESUME.name, p.name.lower()))


def resume_label(path) -> str:
    return "Sample student (testing)" if path.name == config.SAMPLE_RESUME.name else path.stem.replace("_", " ").title()


if "page" not in st.session_state:
    st.session_state["page"] = "landing"

# ======================= Landing page =======================
if st.session_state["page"] == "landing":
    ui.landing_mode()
    all_companies = company.list_companies()
    real = [c for c in all_companies if not c.startswith("sample-")] or all_companies
    n_postings = sum(len(company.load_postings(c)) for c in real)
    ui.landing_hero(len(real), len(sk.all_ids()), n_postings)

    _, mid, _ = st.columns([1.2, 1, 1.2])
    with mid:
        if st.button("Get started  →", type="primary", use_container_width=True):
            st.session_state["page"] = "app"
            st.rerun()

    ui.landing_sections()

    _, mid2, _ = st.columns([1.2, 1, 1.2])
    with mid2:
        if st.button("Build my roadmap  →", type="primary", use_container_width=True, key="cta_bottom"):
            st.session_state["page"] = "app"
            st.rerun()
    ui.footer()
    st.stop()

# ======================= Sidebar: setup + inputs =======================
with st.sidebar:
    if st.button("←  Home", use_container_width=True):
        st.session_state["page"] = "landing"
        st.rerun()

    st.header("⚙️ Setup")
    available = llm.is_available()
    ai_ok = available and llm.model_installed()
    if not available:
        st.error("Ollama isn't running. Start the Ollama app, then click Re-check. Keyword mode still works.")
    elif not ai_ok:
        st.warning(f"Model not found. Run:\n\n`ollama pull {config.MODEL}`")
    else:
        st.success(f"Local model ready: `{config.MODEL}`")
    if st.button("Re-check model", use_container_width=True):
        llm.is_available.cache_clear()
        st.rerun()
    use_ai = st.toggle("Use AI extraction", value=ai_ok, disabled=not ai_ok,
                       help="On = the local model finds implied skills and tailors company requirements to the selected role.")

    companies = company.list_companies()
    if not companies:
        st.error("No job descriptions found. Add files to data/jobs/<company>/ (see README).")
        st.stop()
    real_first = sorted(companies, key=lambda c: (c.startswith("sample-"), c))
    target = st.selectbox("🎯 Target company", real_first, format_func=company.display_name)
    target_label = company.display_name(target)
    target_role = st.selectbox("👔 Role", roles.ROLE_OPTIONS,
                               help="Requirements are filtered from the skills found in this company's job descriptions.")

    st.divider()
    st.header("👤 You")
    uploaded = st.file_uploader("Resume (PDF or TXT)", type=["pdf", "txt", "md"])
    samples = sample_resumes()
    use_sample = st.checkbox("Use a sample resume", value=uploaded is None, disabled=not samples)
    chosen_sample = None
    if use_sample and samples and uploaded is None:
        chosen_sample = st.selectbox("Sample resume", samples, format_func=resume_label)
        st.caption("Only samples with skills recognized by the catalog are listed.")
    syllabus = st.text_area("College subjects / extra skills (optional)",
                            placeholder="e.g. Software Testing, DBMS, Java Programming, Linux lab")

    if st.button("🔍 Analyze my skills", type="primary", use_container_width=True):
        text = ""
        if uploaded is not None:
            text = read_upload(uploaded)
        elif chosen_sample is not None:
            text = read_path(chosen_sample)
        text = f"{text}\n{syllabus}".strip()
        if not text:
            st.warning("Upload a resume, pick a sample resume or type your subjects first.")
        else:
            with st.spinner("Reading your resume with the local model…" if use_ai else "Matching skills…"):
                found = extract_skills(text, use_ai=use_ai)
            st.session_state["my_skills"] = sorted(found, key=lambda s: sk.name(s).lower())
            if found:
                st.toast(f"Found {len(found)} skills", icon="✨")
            else:
                st.warning("No skills from the catalog were detected. Choose a technical sample or add your skills in the list below.")

    st.multiselect("Your skills (fix anything the AI missed)", options=sk.all_ids(),
                   format_func=sk.name, key="my_skills")

    st.divider()
    if st.button("Reset learning progress", use_container_width=True):
        progress.reset()
        st.rerun()

my_skills = set(st.session_state.get("my_skills", []))
done = progress.load_done()
if st.session_state.pop("celebrate", False):
    st.balloons()

# ======================= Header =======================
ui.hero(
    "SkillBridge", "AI",
    "Your personal roadmap to the company you want, built from what they're actually hiring for. "
    "Runs 100% locally on an open model: your resume never leaves this device.",
    badge="Open-source · Local AI · Private",
)

ui.context_bar(target_role, target_label, len(company.load_postings(target)), bool(use_ai))

with st.spinner(f"Reading {target_label}'s job descriptions with the local model (first time only)…"):
    company_profile = cached_profile(target, use_ai, company.signature(target), config.MODEL)

with st.spinner(f"Tailoring requirements for {target_role}…"):
    role_skill_ids = cached_role_skills(
        target, target_role, tuple(company_profile["demand"].items()),
        tuple(p["title"] for p in company_profile["postings"]), use_ai,
        company.signature(target), config.MODEL,
    )

profile = dict(company_profile)
profile["demand"] = {
    sid: weight for sid, weight in company_profile["demand"].items() if sid in role_skill_ids
}
profile["trend"] = company_profile["trend"].reindex(
    columns=[sid for sid in company_profile["trend"].columns if sid in role_skill_ids]
)
profile["postings"] = [
    {**posting, "skills": [sid for sid in posting["skills"] if sid in role_skill_ids]}
    for posting in company_profile["postings"]
]

if target.startswith("sample-"):
    st.info("You're viewing **sample** job descriptions included for testing. Add real ones in `data/jobs/` (see README).")

result = gap.analyze(profile["demand"], my_skills, done)
base = gap.analyze(profile["demand"], my_skills)

tab_radar, tab_gap, tab_road = st.tabs(["📡 Company Radar", "🎯 My Gap", "🗺️ My Roadmap"])

# ======================= Tab 1: Company Radar =======================
with tab_radar:
    ui.section_title(f"{target_role} requirements at {target_label}")
    st.caption("Filtered from the combined requirements evidenced by the job descriptions currently in the project. The AI can only select skills already found in that company's postings.")
    if not profile["demand"]:
        st.info(f"The current {target_label} job descriptions do not contain catalog skills for **{target_role}**. Add postings for this role, or choose another role / company-wide requirements.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Company job descriptions analysed", profile["n_postings"])
    if profile["first_date"]:
        same = profile["first_date"] == profile["last_date"]
        c2.metric("Posted", f"{profile['first_date']:%b %Y}" if same
                  else f"{profile['first_date']:%b %Y} – {profile['last_date']:%b %Y}")
    c3.metric("Skills detected", len(profile["demand"]))

    st.dataframe(
        company.demand_frame(profile),
        hide_index=True,
        use_container_width=True,
        column_config={"Demand %": st.column_config.ProgressColumn(
            "Asked in % of job descriptions", min_value=0, max_value=100, format="%d%%")},
    )

    ui.section_title("How it's changing")
    trend = company.trend_frame(profile)
    if len(trend.index) >= 2:
        st.line_chart(trend, y_label="% of job descriptions", x_label="Quarter")
        rising, falling = company.rising_falling(profile)
        r, f = st.columns(2)
        with r:
            st.markdown("**📈 Rising**")
            ui.chips([f"{sk.name(s)}  +{pct(v)}" for s, v in rising[:5]], have=True)
            if not rising:
                st.caption("No big risers yet.")
        with f:
            st.markdown("**📉 Falling**")
            ui.chips([f"{sk.name(s)}  {pct(v)}" for s, v in falling[:5]])
            if not falling:
                st.caption("No big fallers yet.")
    else:
        st.caption("Add job descriptions from different months (named YYYY-MM-DD_role.txt) to see trends.")

    with st.expander(f"Job descriptions used ({profile['n_postings']})"):
        for p in profile["postings"]:
            st.markdown(f"**{p['date']} · {p['title']}**")
            ui.chips(sk.names(p["skills"]))

# ======================= Tab 2: My Gap =======================
with tab_gap:
    if not my_skills and not done:
        st.info("👈 Pick a sample resume (or upload yours) and click **Analyze my skills**.")
    else:
        ui.score_ring(result.score, f"{target_role} · {target_label}",
                      delta=result.score - base.score, n_focus=len(result.focus))

        left, right = st.columns(2)
        with left:
            ui.section_title("You already have")
            ui.chips([sk.name(s) + (" (learned)" if s in done and s not in my_skills else "") for s in result.matched], have=True)
            if not result.matched:
                st.caption("None of the company's core skills yet. The roadmap fixes that.")
        with right:
            ui.section_title(f"Focus only on these {len(result.focus)}")
            ui.focus_cards([
                {"name": sk.name(s), "demand": profile["demand"][s],
                 "url": (sk.resources(s) or [{}])[0].get("url")}
                for s in result.focus
            ])
            if not result.focus:
                st.success("You cover everything this company commonly asks for! 🎉")

        others = result.missing[len(result.focus):]
        if others:
            ui.section_title("Also asked, lower priority")
            ui.chips([sk.name(s) for s in others])
        if result.extra:
            ui.section_title("Your extra strengths")
            ui.chips([sk.name(s) for s in result.extra], have=True)

# ======================= Tab 3: My Roadmap =======================
with tab_road:
    if not my_skills and not done:
        st.info("👈 Analyze your skills first to get a personal roadmap.")
    else:
        path = roadmap.learning_path(base.focus, my_skills)
        ui.section_title(f"Your path to {target_role} at {target_label}")
        st.graphviz_chart(roadmap.to_dot(path, my_skills, done, set(base.focus)), use_container_width=True)
        ui.roadmap_legend()

        if path:
            learned = sum(1 for s in path if s in done)
            st.progress(learned / len(path), text=f"{learned} of {len(path)} steps learned")

        for i, sid in enumerate(path, 1):
            status = "✅ " if sid in done else ""
            with st.expander(f"{status}Step {i}: {sk.name(sid)}", expanded=(i == 1)):
                if sid in profile["demand"]:
                    st.markdown(f"Asked in **{pct(profile['demand'][sid])}** of {target_label}'s job descriptions.")
                else:
                    needed_for = [sk.name(x) for x in path if sid in sk.prereqs(x)]
                    st.markdown(f"Prerequisite for **{', '.join(needed_for)}**.")
                for r in sk.resources(sid):
                    st.markdown(f"- 📘 [{r['title']}]({r['url']})")

                checked = st.checkbox("I've learned this", value=sid in done, key=f"done_{sid}")
                if checked != (sid in done):
                    progress.set_done(sid, checked)
                    st.session_state["celebrate"] = checked
                    st.rerun()

                if st.button("🔄 Tool Translator: how does what I know help?", key=f"tt_{sid}"):
                    if ai_ok:
                        st.write_stream(translator.explain_stream(sid, my_skills | done, target_label))
                    else:
                        st.markdown(translator.fallback(sid, my_skills | done))

ui.footer()
