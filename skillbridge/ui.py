"""Look and feel: deep warm charcoal, soft ivory and a touch of electric teal.

Everything visual lives here so app.py stays readable. Colours are defined once in PALETTE.
If Google Fonts can't load (e.g. Wi-Fi off), the browser falls back to a system font.
"""

import streamlit as st

PALETTE = {
    "ivory": "#1C1B19",
    "ivory_deep": "#282621",
    "line": "#454035",
    "ink": "#F4EFE4",          # warm ivory text
    "ink_soft": "#C0B8A8",
    "teal": "#20A9B7",         # buttons / links (readable)
    "teal_bright": "#16D3E2",  # glows and accents (electric)
    "teal_tint": "#18383B",
}

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
  --ivory: %(ivory)s; --ivory-deep: %(ivory_deep)s; --line: %(line)s;
  --ink: %(ink)s; --ink-soft: %(ink_soft)s;
  --teal: %(teal)s; --teal-bright: %(teal_bright)s; --teal-tint: %(teal_tint)s;
}

/* ---------- typography ---------- */
html, body, [class*="css"], .stMarkdown, .stText, p, li, label, input, textarea, button {
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
h1, h2, h3, h4, [data-testid="stMetricValue"] {
  font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif !important;
  letter-spacing: -0.02em;
  color: var(--ink);
}
a { color: var(--teal) !important; text-decoration: none; border-bottom: 1px solid transparent; transition: border-color .2s; }
a:hover { border-bottom-color: var(--teal-bright); }

/* ---------- animations ---------- */
@keyframes sbFadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes sbShimmer { 0%% { background-position: -200%% 0; } 100%% { background-position: 200%% 0; } }
@keyframes sbGlow { 0%%, 100%% { box-shadow: 0 0 0 0 rgba(22,211,226,0.0); } 50%% { box-shadow: 0 0 0 6px rgba(22,211,226,0.22); } }
@keyframes sbGrow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes sbFloat { 0%%, 100%% { transform: translateY(0); } 50%% { transform: translateY(-4px); } }

.block-container { padding-top: 2.2rem; max-width: 1200px; }
.block-container > div { animation: sbFadeUp .55s ease-out both; }
[data-baseweb="tab-panel"] { animation: sbFadeUp .45s ease-out both; }

/* ---------- hero ---------- */
.sb-hero { margin-bottom: 1.4rem; }
.sb-hero .sb-badge {
  display: inline-flex; align-items: center; gap: .45rem;
  font-size: .78rem; font-weight: 600; letter-spacing: .04em; text-transform: uppercase;
  color: var(--teal); background: var(--teal-tint);
  padding: .3rem .7rem; border-radius: 999px; border: 1px solid rgba(0,137,154,.18);
}
.sb-hero .sb-dot { width: 7px; height: 7px; border-radius: 50%%; background: var(--teal-bright); animation: sbGlow 2.4s ease-in-out infinite; }
.sb-hero h1 { font-size: clamp(2.1rem, 4vw, 3.1rem); margin: .55rem 0 .2rem; line-height: 1.05; }
.sb-hero h1 .sb-accent {
  background: linear-gradient(90deg, var(--teal), var(--teal-bright), var(--teal));
  background-size: 200%% auto; -webkit-background-clip: text; background-clip: text; color: transparent;
  animation: sbShimmer 6s linear infinite;
}
.sb-hero p { color: var(--ink-soft); font-size: 1.02rem; max-width: 720px; margin: 0; }
.sb-hero .sb-rule {
  height: 3px; width: 120px; margin-top: 1rem; border-radius: 3px;
  background: linear-gradient(90deg, var(--teal-bright), var(--teal));
  transform-origin: left; animation: sbGrow .9s .2s cubic-bezier(.2,.8,.2,1) both;
}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background: var(--ivory-deep); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] h2 { font-size: 1.05rem; }

/* ---------- buttons ---------- */
.stButton > button, .stDownloadButton > button {
  border-radius: 12px; font-weight: 600; border: 1px solid var(--line);
  transition: transform .18s ease, box-shadow .18s ease, background .18s ease, border-color .18s ease;
}
.stButton > button:hover { transform: translateY(-2px); border-color: var(--teal); box-shadow: 0 8px 20px -10px rgba(0,137,154,.55); }
.stButton > button:active { transform: translateY(0); }
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, var(--teal), #00A8B9) !important; color: #fff !important; border: none !important;
  animation: sbGlow 2.8s ease-in-out infinite;
}
.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover { filter: brightness(1.07); }

/* ---------- tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: .4rem; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] {
  font-family: 'Space Grotesk', 'Inter', sans-serif; font-weight: 600; font-size: 1rem;
  padding: .55rem 1rem; border-radius: 10px 10px 0 0; color: var(--ink-soft); transition: color .2s, background .2s;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--ink); background: var(--ivory-deep); }
.stTabs [aria-selected="true"] { color: var(--ink) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: linear-gradient(90deg, var(--teal), var(--teal-bright)) !important; height: 3px !important; }

/* ---------- cards: metrics, expanders, charts, tables ---------- */
[data-testid="stMetric"], [data-testid="stExpander"], [data-testid="stGraphVizChart"],
[data-testid="stDataFrame"], [data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] {
  background: #24221D; border: 1px solid var(--line); border-radius: 16px;
  transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}
[data-testid="stMetric"] { padding: 1rem 1.1rem; }
[data-testid="stMetric"]:hover, [data-testid="stExpander"]:hover {
  transform: translateY(-3px); border-color: rgba(0,137,154,.45); box-shadow: 0 14px 28px -18px rgba(28,27,25,.45);
}
[data-testid="stMetricLabel"] { color: var(--ink-soft); font-weight: 500; }
[data-testid="stMetricValue"] { font-size: 2.2rem; }
[data-testid="stMetricDelta"] { color: var(--teal) !important; }
[data-testid="stMetricDelta"] svg { fill: var(--teal) !important; }
[data-testid="stExpander"] summary { font-weight: 600; }
[data-testid="stExpander"] summary:hover { color: var(--teal); }
[data-testid="stGraphVizChart"] { padding: .6rem; animation: sbFadeUp .6s ease-out both; }

/* ---------- match score progress bar ---------- */
.stProgress > div > div > div > div, [data-testid="stProgress"] div[role="progressbar"] > div > div {
  background: linear-gradient(90deg, var(--teal), var(--teal-bright), var(--teal)) !important;
  background-size: 200%% 100%% !important; animation: sbShimmer 2.5s linear infinite;
  transition: width .8s cubic-bezier(.2,.8,.2,1);
}
.stProgress > div > div, [data-testid="stProgress"] div[role="progressbar"] > div { background: var(--ivory-deep) !important; border-radius: 99px; }

/* ---------- alerts, inputs, checkboxes ---------- */
[data-testid="stAlert"] { border-radius: 14px; border: 1px solid var(--line); }
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div { border-radius: 12px !important; }
[data-testid="stFileUploaderDropzone"] { border-radius: 14px; border: 1.5px dashed rgba(32,169,183,.6); background: #24221D; transition: border-color .2s, background .2s; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--teal-bright); background: var(--teal-tint); }
[data-baseweb="tag"] { background: var(--teal-tint) !important; color: var(--teal) !important; border-radius: 8px !important; }

/* ---------- custom chips & legend ---------- */
.sb-chip {
  display: inline-block; padding: .28rem .7rem; margin: .18rem .25rem .18rem 0; border-radius: 999px;
  font-size: .86rem; font-weight: 500; border: 1px solid var(--line); background: #24221D; color: var(--ink);
  transition: transform .18s ease, border-color .18s ease;
}
.sb-chip:hover { transform: translateY(-2px); border-color: var(--teal); }
.sb-chip.have { background: var(--teal-tint); border-color: rgba(32,169,183,.45); color: #A5E8EC; }
.sb-legend { display: flex; flex-wrap: wrap; gap: .9rem; font-size: .84rem; color: var(--ink-soft); margin: .3rem 0 1rem; }
.sb-legend span::before { content: ""; display: inline-block; width: 11px; height: 11px; border-radius: 3px; margin-right: .4rem; vertical-align: -1px; }
.sb-legend .k::before { background: var(--teal-tint); border: 1px solid rgba(0,137,154,.4); }
.sb-legend .f::before { background: var(--ink); }
.sb-legend .p::before { background: var(--ivory-deep); border: 1px solid #716B5E; }
.sb-legend .d::before { background: var(--teal); }

/* ---------- footer ---------- */
.sb-footer { text-align: center; color: var(--ink-soft); font-size: .82rem; padding: 1.2rem 0 .4rem; }
.sb-footer b { color: var(--teal); }

/* Respect users who turn off motion */
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
</style>
"""


def apply_theme() -> None:
    """Inject fonts, colours and animations. Call once, right after st.set_page_config."""
    st.markdown(_CSS % PALETTE, unsafe_allow_html=True)


def hero(title_start: str, title_accent: str, subtitle: str, badge: str) -> None:
    st.markdown(
        f"""
        <div class="sb-hero">
          <span class="sb-badge"><span class="sb-dot"></span>{badge}</span>
          <h1>{title_start} <span class="sb-accent">{title_accent}</span></h1>
          <p>{subtitle}</p>
          <div class="sb-rule"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chips(labels: list[str], have: bool = False) -> None:
    if not labels:
        return
    cls = "sb-chip have" if have else "sb-chip"
    st.markdown("".join(f'<span class="{cls}">{l}</span>' for l in labels), unsafe_allow_html=True)


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
