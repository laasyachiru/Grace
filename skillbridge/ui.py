"""Look and feel: deep warm charcoal, soft ivory and a touch of electric teal.

Everything visual lives here so app.py stays readable:
- apply_theme()      fonts, colours, animations (call once after st.set_page_config)
- landing_*()        the landing page
- score_ring()       animated match score
- focus_cards()      animated "learn these" cards
- chips(), roadmap_legend(), section_title(), footer()

If Google Fonts can't load (e.g. Wi-Fi off), the browser falls back to a system font.
Animations switch off automatically for users who prefer reduced motion.
"""

from html import escape

import streamlit as st

PALETTE = {
    "bg": "#1C1B19",           # warm charcoal
    "bg_deep": "#282621",      # sidebar, inputs
    "card": "#24221D",
    "line": "#454035",
    "ink": "#F4EFE4",          # warm ivory text
    "ink_soft": "#C0B8A8",
    "teal": "#20A9B7",         # buttons / links
    "teal_bright": "#16D3E2",  # glows and accents (electric)
    "teal_tint": "#18383B",
}


def _root_vars() -> str:
    p = PALETTE
    return (
        ":root{"
        f"--bg:{p['bg']};--bg-deep:{p['bg_deep']};--card:{p['card']};--line:{p['line']};"
        f"--ink:{p['ink']};--ink-soft:{p['ink_soft']};"
        f"--teal:{p['teal']};--teal-bright:{p['teal_bright']};--teal-tint:{p['teal_tint']};"
        "}"
    )


_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

/* animatable numbers for the score ring (falls back to the final value in older browsers) */
@property --p { syntax: '<number>'; initial-value: 0; inherits: false; }
@property --num { syntax: '<integer>'; initial-value: 0; inherits: false; }

/* ---------- typography ---------- */
html, body, [class*="css"], .stMarkdown, .stText, p, li, label, input, textarea, button {
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
h1, h2, h3, h4, [data-testid="stMetricValue"] {
  font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif !important;
  letter-spacing: -0.02em; color: var(--ink);
}
a { color: var(--teal-bright) !important; text-decoration: none; border-bottom: 1px solid transparent; transition: border-color .2s; }
a:hover { border-bottom-color: var(--teal-bright); }
::selection { background: rgba(22,211,226,.3); }

/* ---------- keyframes ---------- */
@keyframes sbFadeUp { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
@keyframes sbFadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes sbScaleIn { from { opacity: 0; transform: scale(.94); } to { opacity: 1; transform: none; } }
@keyframes sbShimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
@keyframes sbGlow { 0%, 100% { box-shadow: 0 0 0 0 rgba(22,211,226,0); } 50% { box-shadow: 0 0 0 7px rgba(22,211,226,.18); } }
@keyframes sbGrow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes sbBar { from { width: 0; } }
@keyframes sbFloatA { 0%, 100% { transform: translate(0,0) scale(1); } 50% { transform: translate(40px,-30px) scale(1.12); } }
@keyframes sbFloatB { 0%, 100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-50px,25px) scale(.9); } }
@keyframes sbRing { from { --p: 0; --num: 0; } }
@keyframes sbFlow { from { stroke-dashoffset: 24; } to { stroke-dashoffset: 0; } }
@keyframes sbPulse { 0%, 100% { opacity: .55; } 50% { opacity: 1; } }

/* ---------- page + transitions ---------- */
.stApp { background: radial-gradient(1200px 600px at 85% -10%, rgba(22,211,226,.07), transparent 60%), var(--bg); }
.block-container { padding-top: 2rem; max-width: 1180px; }
.block-container > div { animation: sbFadeUp .6s cubic-bezier(.2,.8,.2,1) both; }
[data-baseweb="tab-panel"] { animation: sbFadeUp .45s cubic-bezier(.2,.8,.2,1) both; }
.sb-d1 { animation-delay: .08s !important; } .sb-d2 { animation-delay: .16s !important; }
.sb-d3 { animation-delay: .24s !important; } .sb-d4 { animation-delay: .32s !important; }
.sb-d5 { animation-delay: .40s !important; } .sb-d6 { animation-delay: .48s !important; }

/* ---------- landing ---------- */
.sb-land { position: relative; overflow: hidden; border-radius: 28px; border: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(40,38,33,.9), rgba(28,27,25,.95));
  padding: clamp(2.4rem, 6vw, 4.6rem) clamp(1.4rem, 5vw, 3.6rem) 2.4rem; margin-bottom: 1.4rem; }
.sb-land::before { content: ""; position: absolute; inset: 0; pointer-events: none;
  background-image: linear-gradient(rgba(244,239,228,.04) 1px, transparent 1px), linear-gradient(90deg, rgba(244,239,228,.04) 1px, transparent 1px);
  background-size: 44px 44px; mask-image: radial-gradient(ellipse at 50% 30%, black 30%, transparent 75%); }
.sb-orb { position: absolute; border-radius: 50%; filter: blur(70px); pointer-events: none; }
.sb-orb.a { width: 380px; height: 380px; top: -120px; right: -80px; background: rgba(22,211,226,.22); animation: sbFloatA 14s ease-in-out infinite; }
.sb-orb.b { width: 320px; height: 320px; bottom: -140px; left: -90px; background: rgba(32,169,183,.16); animation: sbFloatB 16s ease-in-out infinite; }
.sb-land-inner { position: relative; text-align: center; max-width: 820px; margin: 0 auto; }
.sb-badge { display: inline-flex; align-items: center; gap: .5rem; font-size: .76rem; font-weight: 600; letter-spacing: .06em;
  text-transform: uppercase; color: var(--teal-bright); background: var(--teal-tint); padding: .35rem .8rem; border-radius: 999px;
  border: 1px solid rgba(22,211,226,.25); animation: sbScaleIn .6s cubic-bezier(.2,.8,.2,1) both; }
.sb-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--teal-bright); animation: sbGlow 2.4s ease-in-out infinite; }
.sb-land h1 { font-size: clamp(2.6rem, 7vw, 4.8rem); line-height: 1.02; margin: 1rem 0 .7rem; animation: sbFadeUp .8s .1s cubic-bezier(.2,.8,.2,1) both; }
.sb-accent { background: linear-gradient(90deg, var(--teal), var(--teal-bright), #8EF3FA, var(--teal-bright), var(--teal));
  background-size: 200% auto; -webkit-background-clip: text; background-clip: text; color: transparent; animation: sbShimmer 6s linear infinite; }
.sb-land .sb-sub { color: var(--ink-soft); font-size: clamp(1rem, 2vw, 1.18rem); line-height: 1.55; max-width: 640px; margin: 0 auto;
  animation: sbFadeUp .8s .2s cubic-bezier(.2,.8,.2,1) both; }
.sb-stats { display: flex; justify-content: center; flex-wrap: wrap; gap: .8rem; margin-top: 1.8rem; animation: sbFadeUp .8s .3s cubic-bezier(.2,.8,.2,1) both; }
.sb-stat { min-width: 140px; padding: .8rem 1.1rem; border-radius: 16px; border: 1px solid var(--line); background: rgba(36,34,29,.7);
  backdrop-filter: blur(6px); transition: transform .25s, border-color .25s; }
.sb-stat:hover { transform: translateY(-3px); border-color: rgba(22,211,226,.5); }
.sb-stat b { display: block; font-family: 'Space Grotesk', sans-serif; font-size: 1.6rem; color: var(--ink); }
.sb-stat span { font-size: .8rem; color: var(--ink-soft); }

.sb-h2 { text-align: center; font-family: 'Space Grotesk', sans-serif; font-size: clamp(1.5rem, 3vw, 2rem); font-weight: 600; color: var(--ink); margin: 2.6rem 0 .3rem; }
.sb-h2sub { text-align: center; color: var(--ink-soft); margin: 0 0 1.4rem; }
.sb-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; position: relative; }
.sb-step { position: relative; padding: 1.3rem 1.2rem; border-radius: 20px; border: 1px solid var(--line); background: var(--card);
  animation: sbFadeUp .7s cubic-bezier(.2,.8,.2,1) both; transition: transform .25s, border-color .25s, box-shadow .25s; }
.sb-step:hover { transform: translateY(-4px); border-color: rgba(22,211,226,.5); box-shadow: 0 18px 36px -24px rgba(22,211,226,.5); }
.sb-step .n { display: inline-grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; font-weight: 700;
  font-family: 'Space Grotesk', sans-serif; color: var(--bg); background: linear-gradient(135deg, var(--teal), var(--teal-bright)); }
.sb-step h4 { margin: .8rem 0 .3rem; font-size: 1.12rem; }
.sb-step p { margin: 0; color: var(--ink-soft); font-size: .93rem; line-height: 1.5; }
.sb-step:not(:last-child)::after { content: "→"; position: absolute; right: -.85rem; top: 50%; transform: translateY(-50%);
  color: var(--teal-bright); font-size: 1.1rem; z-index: 2; animation: sbPulse 2s ease-in-out infinite; }

.sb-feats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.sb-feat { padding: 1.2rem; border-radius: 18px; border: 1px solid var(--line); background: linear-gradient(180deg, var(--card), rgba(28,27,25,.6));
  animation: sbFadeUp .7s cubic-bezier(.2,.8,.2,1) both; transition: transform .25s, border-color .25s; }
.sb-feat:hover { transform: translateY(-4px); border-color: rgba(22,211,226,.45); }
.sb-feat .ic { font-size: 1.4rem; }
.sb-feat h4 { margin: .5rem 0 .25rem; font-size: 1.02rem; }
.sb-feat p { margin: 0; color: var(--ink-soft); font-size: .9rem; line-height: 1.5; }
.sb-pills { display: flex; justify-content: center; flex-wrap: wrap; gap: .5rem; margin: 2rem 0 .5rem; }
.sb-pill { font-size: .82rem; padding: .35rem .8rem; border-radius: 999px; border: 1px solid var(--line); color: var(--ink-soft); background: var(--card); }
@media (max-width: 760px) { .sb-steps, .sb-feats { grid-template-columns: 1fr; } .sb-step:not(:last-child)::after { content: "↓"; right: 50%; top: auto; bottom: -1rem; transform: translateX(50%); } }

/* ---------- app header ---------- */
.sb-hero { margin-bottom: 1.2rem; }
.sb-hero h1 { font-size: clamp(2rem, 4vw, 2.8rem); margin: .55rem 0 .2rem; line-height: 1.05; }
.sb-hero p { color: var(--ink-soft); font-size: 1rem; max-width: 720px; margin: 0; }
.sb-rule { height: 3px; width: 120px; margin-top: .9rem; border-radius: 3px; background: linear-gradient(90deg, var(--teal-bright), var(--teal));
  transform-origin: left; animation: sbGrow .9s .2s cubic-bezier(.2,.8,.2,1) both; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background: var(--bg-deep); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] > div { animation: sbFadeIn .5s ease-out both; }
[data-testid="stSidebar"] h2 { font-size: 1.05rem; }

/* ---------- buttons ---------- */
.stButton > button { border-radius: 12px; font-weight: 600; border: 1px solid var(--line);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease, filter .18s ease; }
.stButton > button:hover { transform: translateY(-2px); border-color: var(--teal-bright); box-shadow: 0 10px 24px -12px rgba(22,211,226,.6); }
.stButton > button:active { transform: translateY(0) scale(.98); }
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, var(--teal), var(--teal-bright)) !important; color: #0E1B1C !important; border: none !important;
  animation: sbGlow 2.8s ease-in-out infinite; }
.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover { filter: brightness(1.08); }

/* ---------- tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: .4rem; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { font-family: 'Space Grotesk', 'Inter', sans-serif; font-weight: 600; font-size: 1rem;
  padding: .55rem 1rem; border-radius: 10px 10px 0 0; color: var(--ink-soft); transition: color .2s, background .2s; }
.stTabs [data-baseweb="tab"]:hover { color: var(--ink); background: var(--bg-deep); }
.stTabs [aria-selected="true"] { color: var(--ink) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: linear-gradient(90deg, var(--teal), var(--teal-bright)) !important; height: 3px !important;
  transition: left .35s cubic-bezier(.2,.8,.2,1), width .35s cubic-bezier(.2,.8,.2,1) !important; }

/* ---------- cards ---------- */
[data-testid="stMetric"], [data-testid="stExpander"], [data-testid="stGraphVizChart"], [data-testid="stDataFrame"],
[data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] {
  background: var(--card); border: 1px solid var(--line); border-radius: 16px;
  transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease; }
[data-testid="stMetric"] { padding: 1rem 1.1rem; animation: sbScaleIn .5s cubic-bezier(.2,.8,.2,1) both; }
[data-testid="stMetric"]:hover, [data-testid="stExpander"]:hover { transform: translateY(-3px); border-color: rgba(22,211,226,.5);
  box-shadow: 0 16px 30px -20px rgba(0,0,0,.8); }
[data-testid="stMetricLabel"] { color: var(--ink-soft); font-weight: 500; }
[data-testid="stMetricValue"] { font-size: 2rem; }
[data-testid="stExpander"] summary { font-weight: 600; transition: color .2s; }
[data-testid="stExpander"] summary:hover { color: var(--teal-bright); }
[data-testid="stExpander"] details[open] > div { animation: sbFadeUp .35s ease-out both; }
[data-testid="stGraphVizChart"] { padding: .6rem; animation: sbScaleIn .6s cubic-bezier(.2,.8,.2,1) both; }

/* ---------- score ring ---------- */
.sb-score { display: flex; align-items: center; gap: 1.6rem; padding: 1.3rem 1.5rem; border-radius: 22px; border: 1px solid var(--line);
  background: linear-gradient(135deg, var(--card), rgba(24,56,59,.55)); margin-bottom: 1.2rem; animation: sbScaleIn .6s cubic-bezier(.2,.8,.2,1) both; }
.sb-ring { --size: 128px; width: var(--size); height: var(--size); flex: none; border-radius: 50%; display: grid; place-items: center;
  background: conic-gradient(var(--teal-bright) calc(var(--p) * 1%), rgba(244,239,228,.08) 0); animation: sbRing 1.4s cubic-bezier(.2,.8,.2,1) both;
  counter-reset: num var(--num); box-shadow: 0 0 40px -12px rgba(22,211,226,.55); }
.sb-ring::before { content: counter(num) "%"; display: grid; place-items: center; width: calc(var(--size) - 22px); height: calc(var(--size) - 22px);
  border-radius: 50%; background: var(--bg); font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 2rem; color: var(--ink); }
.sb-score-text h3 { margin: 0 0 .25rem; font-size: 1.35rem; }
.sb-score-text p { margin: 0; color: var(--ink-soft); }
.sb-delta { display: inline-block; margin-top: .55rem; font-size: .85rem; font-weight: 600; color: var(--teal-bright); background: var(--teal-tint);
  padding: .25rem .65rem; border-radius: 999px; animation: sbFadeUp .5s .6s ease-out both; }

/* ---------- focus cards ---------- */
.sb-focus { display: flex; align-items: center; gap: .9rem; padding: .85rem 1rem; margin-bottom: .55rem; border-radius: 14px;
  border: 1px solid var(--line); background: var(--card); animation: sbFadeUp .5s cubic-bezier(.2,.8,.2,1) both;
  transition: transform .2s, border-color .2s; }
.sb-focus:hover { transform: translateX(4px); border-color: rgba(22,211,226,.5); }
.sb-focus .rank { display: grid; place-items: center; width: 30px; height: 30px; flex: none; border-radius: 9px; font-weight: 700;
  color: var(--teal-bright); background: var(--teal-tint); font-family: 'Space Grotesk', sans-serif; }
.sb-focus .body { flex: 1; min-width: 0; }
.sb-focus .top { display: flex; justify-content: space-between; gap: .6rem; font-weight: 600; }
.sb-focus .top span { color: var(--ink-soft); font-weight: 500; font-size: .85rem; white-space: nowrap; }
.sb-focus .bar { height: 6px; border-radius: 99px; background: rgba(244,239,228,.08); margin-top: .45rem; overflow: hidden; }
.sb-focus .bar i { display: block; height: 100%; border-radius: 99px; background: linear-gradient(90deg, var(--teal), var(--teal-bright));
  animation: sbBar 1.1s cubic-bezier(.2,.8,.2,1) both; }
.sb-focus a { font-size: .82rem; }

/* ---------- section titles ---------- */
.sb-sec { display: flex; align-items: center; gap: .55rem; font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 600;
  color: var(--ink); margin: .4rem 0 .8rem; animation: sbFadeUp .5s ease-out both; }
.sb-sec::before { content: ""; width: 4px; height: 1.1em; border-radius: 4px; background: linear-gradient(180deg, var(--teal-bright), var(--teal)); }

/* ---------- progress, alerts, inputs, spinner ---------- */
.stProgress > div > div > div > div, [data-testid="stProgress"] div[role="progressbar"] > div > div {
  background: linear-gradient(90deg, var(--teal), var(--teal-bright), var(--teal)) !important; background-size: 200% 100% !important;
  animation: sbShimmer 2.5s linear infinite; }
[data-testid="stAlert"] { border-radius: 14px; border: 1px solid var(--line); animation: sbFadeUp .45s ease-out both; }
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div { border-radius: 12px !important; transition: border-color .2s, box-shadow .2s; }
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"] > div:focus-within { box-shadow: 0 0 0 3px rgba(22,211,226,.18); }
[data-testid="stFileUploaderDropzone"] { border-radius: 14px; border: 1.5px dashed rgba(32,169,183,.6); background: var(--card); transition: border-color .2s, background .2s; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--teal-bright); background: var(--teal-tint); }
[data-baseweb="tag"] { background: var(--teal-tint) !important; color: #A5E8EC !important; border-radius: 8px !important; }
[data-testid="stSpinner"] > div { color: var(--teal-bright); animation: sbPulse 1.4s ease-in-out infinite; }

/* ---------- chips & legend ---------- */
.sb-chip { display: inline-block; padding: .3rem .72rem; margin: .18rem .25rem .18rem 0; border-radius: 999px; font-size: .86rem; font-weight: 500;
  border: 1px solid var(--line); background: var(--card); color: var(--ink); animation: sbScaleIn .4s ease-out both; transition: transform .18s, border-color .18s; }
.sb-chip:hover { transform: translateY(-2px); border-color: var(--teal-bright); }
.sb-chip.have { background: var(--teal-tint); border-color: rgba(32,169,183,.45); color: #A5E8EC; }
.sb-legend { display: flex; flex-wrap: wrap; gap: .9rem; font-size: .84rem; color: var(--ink-soft); margin: .4rem 0 1rem; }
.sb-legend span::before { content: ""; display: inline-block; width: 11px; height: 11px; border-radius: 3px; margin-right: .4rem; vertical-align: -1px; }
.sb-legend .k::before { background: #18383B; border: 1px solid #4CBAC4; }
.sb-legend .f::before { background: #34312A; border: 1px solid #706A5E; }
.sb-legend .p::before { background: #282621; border: 1px solid #716B5E; }
.sb-legend .d::before { background: #087E89; border: 1px solid #16D3E2; }

/* ---------- context bar ---------- */
.sb-ctx { display: flex; flex-wrap: wrap; gap: .5rem; margin: -.2rem 0 1.1rem; }
.sb-ctx span { display: inline-flex; align-items: center; gap: .4rem; font-size: .84rem; padding: .32rem .75rem; border-radius: 999px;
  border: 1px solid var(--line); background: var(--card); color: var(--ink-soft); animation: sbFadeUp .5s cubic-bezier(.2,.8,.2,1) both; }
.sb-ctx span b { color: var(--ink); font-weight: 600; }
.sb-ctx span.on { color: var(--teal-bright); border-color: rgba(22,211,226,.35); background: var(--teal-tint); }
.sb-ctx span.on::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--teal-bright); animation: sbGlow 2.4s ease-in-out infinite; }

/* ---------- footer ---------- */
.sb-footer { text-align: center; color: var(--ink-soft); font-size: .82rem; padding: 1.6rem 0 .4rem; }
.sb-footer b { color: var(--teal-bright); }

@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
"""


def apply_theme() -> None:
    """Inject fonts, colours and animations. Call once, right after st.set_page_config."""
    st.markdown(f"<style>{_root_vars()}{_CSS}</style>", unsafe_allow_html=True)


# ---------------- landing page ----------------

def landing_mode() -> None:
    """Hide the sidebar on the landing page and mark the page for landing-only styles."""
    st.markdown(
        "<style>[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl'], "
        "[data-testid='collapsedControl'] { display: none !important; } "
        ".block-container { max-width: 1080px; } "
        ".stButton > button[kind='primary'], [data-testid='stBaseButton-primary'] "
        "{ font-size: 1.08rem; padding: .8rem 1.4rem; border-radius: 14px; }</style>",
        unsafe_allow_html=True,
    )


def landing_hero(n_companies: int, n_skills: int, n_postings: int) -> None:
    st.markdown(
        f"""
<div class="sb-land">
  <div class="sb-orb a"></div><div class="sb-orb b"></div>
  <div class="sb-land-inner">
    <span class="sb-badge"><span class="sb-dot"></span>Open-source · Local AI · Private</span>
    <h1>Bridge your skills to<br><span class="sb-accent">the company you want</span></h1>
    <p class="sb-sub">SkillBridge AI reads what a company is actually hiring for, compares it with what you already know,
    and builds your personal roadmap to get there. All on an open model running on your own laptop.</p>
    <div class="sb-stats">
      <div class="sb-stat"><b>{n_companies}</b><span>companies tracked</span></div>
      <div class="sb-stat"><b>{n_postings}</b><span>job descriptions read</span></div>
      <div class="sb-stat"><b>{n_skills}</b><span>skills mapped</span></div>
      <div class="sb-stat"><b>0</b><span>bytes sent to the cloud</span></div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def landing_sections() -> None:
    st.markdown(
        """
<div class="sb-h2">How it works</div>
<p class="sb-h2sub">Three steps from "what do they want?" to "I'm ready".</p>
<div class="sb-steps">
  <div class="sb-step sb-d1"><span class="n">1</span><h4>Company Radar</h4>
    <p>Pick a company. See which skills its job descriptions ask for, and which are rising or falling.</p></div>
  <div class="sb-step sb-d2"><span class="n">2</span><h4>Your Gap</h4>
    <p>Upload your resume. Get a match score and a focus list of only the skills that matter for that company.</p></div>
  <div class="sb-step sb-d3"><span class="n">3</span><h4>Your Roadmap</h4>
    <p>Follow a path in the right learning order, with free resources and tips on how your current skills carry over.</p></div>
</div>

<div class="sb-h2">Built different</div>
<p class="sb-h2sub">Not another generic roadmap.</p>
<div class="sb-feats">
  <div class="sb-feat sb-d1"><div class="ic">🎯</div><h4>Company-specific</h4>
    <p>Generic roadmaps show everyone the same path. Yours comes from what your target company is hiring for.</p></div>
  <div class="sb-feat sb-d2"><div class="ic">🔄</div><h4>Tool Translator</h4>
    <p>Know Postman but they want CI/CD? The local AI explains how your skills transfer.</p></div>
  <div class="sb-feat sb-d3"><div class="ic">📈</div><h4>Watch your score rise</h4>
    <p>Tick off skills as you learn them and see your match grow, step by step.</p></div>
  <div class="sb-feat sb-d4"><div class="ic">🔒</div><h4>Private by design</h4>
    <p>Your resume never leaves your device. It even works with Wi-Fi off.</p></div>
  <div class="sb-feat sb-d5"><div class="ic">🧮</div><h4>Scores you can trust</h4>
    <p>The AI reads documents; the score is plain math, so it's the same every time.</p></div>
  <div class="sb-feat sb-d6"><div class="ic">🧩</div><h4>Open agent skill</h4>
    <p>The same logic ships as a SKILL.md any AI agent can use. MIT licensed.</p></div>
</div>

<div class="sb-pills">
  <span class="sb-pill">Qwen2.5 · Apache 2.0</span><span class="sb-pill">Runs on Ollama</span>
  <span class="sb-pill">MIT licensed</span><span class="sb-pill">Agent Skill Open Standard</span>
</div>
""",
        unsafe_allow_html=True,
    )


# ---------------- app pieces ----------------

def hero(title_start: str, title_accent: str, subtitle: str, badge: str) -> None:
    st.markdown(
        f"""
<div class="sb-hero">
  <span class="sb-badge"><span class="sb-dot"></span>{escape(badge)}</span>
  <h1>{escape(title_start)} <span class="sb-accent">{escape(title_accent)}</span></h1>
  <p>{escape(subtitle)}</p>
  <div class="sb-rule"></div>
</div>
""",
        unsafe_allow_html=True,
    )


def context_bar(role: str, company: str, n_postings: int, ai_on: bool) -> None:
    """Pills under the header: what the user is looking at right now."""
    plural = "s" if n_postings != 1 else ""
    mode = '<span class="on sb-d3">Local AI on</span>' if ai_on else '<span class="sb-d3">Keyword mode</span>'
    st.markdown(
        f'<div class="sb-ctx"><span>Role <b>{escape(role)}</b></span>'
        f'<span class="sb-d1">Company <b>{escape(company)}</b></span>'
        f'<span class="sb-d2"><b>{n_postings}</b> job description{plural}</span>'
        f"{mode}</div>",
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    st.markdown(f'<div class="sb-sec">{escape(text)}</div>', unsafe_allow_html=True)


def score_ring(score: int, company: str, delta: int = 0, n_focus: int = 0) -> None:
    """Animated ring that counts up to the match score."""
    score = max(0, min(100, int(score)))
    delta_html = f'<span class="sb-delta">+{delta}% from skills you\'ve learned</span>' if delta > 0 else ""
    focus_txt = f"Focus on {n_focus} skill{'s' if n_focus != 1 else ''} to close the gap." if n_focus else "You cover what they ask for."
    st.markdown(
        f"""
<div class="sb-score">
  <div class="sb-ring" style="--p:{score};--num:{score}"></div>
  <div class="sb-score-text">
    <h3>Your match with {escape(company)}</h3>
    <p>{focus_txt}</p>
    {delta_html}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def focus_cards(items: list[dict]) -> None:
    """items: [{'name', 'demand' (0-1), 'url' (optional)}], shown as animated ranked cards."""
    cards = []
    for i, it in enumerate(items, 1):
        pct = round(it["demand"] * 100)
        link = f' · <a href="{escape(it["url"])}" target="_blank">start here</a>' if it.get("url") else ""
        cards.append(
            f'<div class="sb-focus sb-d{min(i, 6)}"><div class="rank">{i}</div><div class="body">'
            f'<div class="top">{escape(it["name"])}<span>asked in {pct}%{link}</span></div>'
            f'<div class="bar"><i style="width:{pct}%"></i></div></div></div>'
        )
    st.markdown("".join(cards), unsafe_allow_html=True)


def chips(labels: list[str], have: bool = False) -> None:
    if not labels:
        return
    cls = "sb-chip have" if have else "sb-chip"
    st.markdown("".join(f'<span class="{cls}">{escape(l)}</span>' for l in labels), unsafe_allow_html=True)


def roadmap_legend() -> None:
    st.markdown(
        '<div class="sb-legend"><span class="k">You know it</span><span class="f">Company wants it</span>'
        '<span class="p">Learn this first</span><span class="d">Learned</span></div>',
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        '<div class="sb-footer"><b>SkillBridge AI</b> · MIT licensed · Open-weight model via Ollama · '
        "No data leaves this device</div>",
        unsafe_allow_html=True,
    )
