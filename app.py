"""SkillBridge AI: Streamlit app.

Run:  streamlit run app.py
Phone on the same hotspot:  streamlit run app.py --server.address 0.0.0.0
"""

import streamlit as st

from skillbridge import company, config, gap, llm, progress, roadmap, translator, ui
from skillbridge import skills as sk
from skillbridge.extract import extract_skills
from skillbridge.resume import read_path, read_upload

st.set_page_config(page_title="SkillBridge AI", page_icon="🌉", layout="wide")
ui.apply_theme()


@st.cache_data(show_spinner=False)
def cached_profile(name: str, use_ai: bool, sig: tuple, model: str) -> dict:
    # sig and model are only here so the cache refreshes when job files or the model change.
    return company.build_profile(name, use_ai=use_ai)


def pct(x: float) -> str:
    return f"{round(x * 100)}%"


# ---------------- Sidebar: setup + inputs ----------------
with st.sidebar:
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
                       help="Off = fast keyword matching only. On = the local model also finds implied skills.")

    companies = company.list_companies()
    if not companies:
        st.error("No job descriptions found. Add files to data/jobs/<company>/ (see README).")
        st.stop()
    target = st.selectbox("🎯 Target company", companies, format_func=company.display_name)
    target_label = company.display_name(target)

    st.divider()
    st.header("👤 You")
    uploaded = st.file_uploader("Resume (PDF or TXT)", type=["pdf", "txt", "md"])
    use_sample = st.checkbox("Use sample resume", value=uploaded is None)
    syllabus = st.text_area("College subjects / extra skills (optional)",
                            placeholder="e.g. Software Testing, DBMS, Java Programming, Linux lab")

    if st.button("🔍 Analyze my skills", type="primary", use_container_width=True):
        text = ""
        if uploaded is not None:
            text = read_upload(uploaded)
        elif use_sample and config.SAMPLE_RESUME.exists():
            text = read_path(config.SAMPLE_RESUME)
        text = f"{text}\n{syllabus}".strip()
        if not text:
            st.warning("Upload a resume, tick 'Use sample resume' or type your subjects first.")
        else:
            with st.spinner("Reading your resume with the local model…" if use_ai else "Matching skills…"):
                found = extract_skills(text, use_ai=use_ai)
            st.session_state["my_skills"] = sorted(found, key=lambda s: sk.name(s).lower())

    st.multiselect("Your skills (fix anything the AI missed)", options=sk.all_ids(),
                   format_func=sk.name, key="my_skills")

    st.divider()
    if st.button("Reset learning progress", use_container_width=True):
        progress.reset()
        st.rerun()

my_skills = set(st.session_state.get("my_skills", []))
done = progress.load_done()

# ---------------- Header ----------------
ui.hero(
    "SkillBridge", "AI",
    "Your personal roadmap to the company you want, built from what they're actually hiring for. "
    "Runs 100% locally on an open model: your resume never leaves this device.",
    badge="Open-source · Local AI · Private",
)

with st.spinner(f"Reading {target_label}'s job descriptions with the local model (first time only)…"):
    profile = cached_profile(target, use_ai, company.signature(target), config.MODEL)

if target.startswith("sample-"):
    st.info("You're viewing **sample** job descriptions included for testing. Add real ones in `data/jobs/` (see README).")

result = gap.analyze(profile["demand"], my_skills, done)
base = gap.analyze(profile["demand"], my_skills)

tab_radar, tab_gap, tab_road = st.tabs(["📡 Company Radar", "🎯 My Gap", "🗺️ My Roadmap"])

# ---------------- Tab 1: Company Radar ----------------
with tab_radar:
    st.subheader(f"What {target_label} expects")
    c1, c2, c3 = st.columns(3)
    c1.metric("Job descriptions analysed", profile["n_postings"])
    if profile["first_date"]:
        c2.metric("Date range", f"{profile['first_date']:%b %Y} – {profile['last_date']:%b %Y}")
    c3.metric("Skills detected", len(profile["demand"]))

    st.dataframe(
        company.demand_frame(profile),
        hide_index=True,
        use_container_width=True,
        column_config={"Demand %": st.column_config.ProgressColumn(
            "Asked in % of job descriptions", min_value=0, max_value=100, format="%d%%")},
    )

    st.subheader("How it's changing")
    trend = company.trend_frame(profile)
    if len(trend.index) >= 2:
        st.line_chart(trend, y_label="% of job descriptions", x_label="Quarter")
        rising, falling = company.rising_falling(profile)
        r, f = st.columns(2)
        with r:
            st.markdown("**📈 Rising**")
            for sid, v in rising[:5] or []:
                st.markdown(f"- {sk.name(sid)} (+{pct(v)})")
            if not rising:
                st.caption("No big risers yet.")
        with f:
            st.markdown("**📉 Falling**")
            for sid, v in falling[:5] or []:
                st.markdown(f"- {sk.name(sid)} ({pct(v)})")
            if not falling:
                st.caption("No big fallers yet.")
    else:
        st.caption("Add job descriptions from different months to see trends.")

    with st.expander(f"Job descriptions used ({profile['n_postings']})"):
        for p in profile["postings"]:
            st.markdown(f"**{p['date']} · {p['title']}**  \n{', '.join(sk.names(p['skills'])) or '_no skills found_'}")

# ---------------- Tab 2: My Gap ----------------
with tab_gap:
    if not my_skills and not done:
        st.info("👈 Upload your resume (or use the sample) and click **Analyze my skills**.")
    else:
        delta = result.score - base.score
        st.metric(f"Your match with {target_label}", f"{result.score}%",
                  delta=f"+{delta}% from skills you've learned" if delta > 0 else None)
        st.progress(result.score / 100)

        left, right = st.columns(2)
        with left:
            st.markdown("### ✅ You already have")
            for sid in result.matched:
                tag = " (learned)" if sid in done and sid not in my_skills else ""
                st.markdown(f"<span style='color:{ui.PALETTE['teal']}'>●</span> **{sk.name(sid)}**{tag}, "
                            f"asked in {pct(profile['demand'][sid])}", unsafe_allow_html=True)
            if not result.matched:
                st.caption("None of the company's core skills yet. The roadmap fixes that.")
        with right:
            st.markdown(f"### 🎯 Focus only on these {len(result.focus)}")
            for i, sid in enumerate(result.focus, 1):
                res = sk.resources(sid)
                link = f" · [start here]({res[0]['url']})" if res else ""
                st.markdown(f"**{i}. {sk.name(sid)}**, asked in {pct(profile['demand'][sid])}{link}")
            if not result.focus:
                st.success("You cover everything this company commonly asks for! 🎉")

        others = result.missing[len(result.focus):]
        if others:
            st.markdown("**Also asked, lower priority**")
            ui.chips([sk.name(s) for s in others])
        if result.extra:
            st.markdown("**Your extra strengths** (this company doesn't ask for them)")
            ui.chips([sk.name(s) for s in result.extra], have=True)

# ---------------- Tab 3: My Roadmap ----------------
with tab_road:
    if not my_skills and not done:
        st.info("👈 Analyze your skills first to get a personal roadmap.")
    else:
        path = roadmap.learning_path(base.focus, my_skills)
        st.subheader(f"Your path to {target_label}")
        st.graphviz_chart(roadmap.to_dot(path, my_skills, done, set(base.focus)), use_container_width=True)
        ui.roadmap_legend()

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
                    st.rerun()

                if st.button("🔄 Tool Translator: how does what I know help?", key=f"tt_{sid}"):
                    if ai_ok:
                        st.write_stream(translator.explain_stream(sid, my_skills | done, target_label))
                    else:
                        st.markdown(translator.fallback(sid, my_skills | done))

ui.footer()
