"""
AI SQL Data Analyst — Streamlit Frontend
------------------------------------------------
A modern, animated frontend for the natural-language-to-SQL backend.
Handles string, DataFrame, and raw tuple/list results gracefully.
"""

import time
from datetime import datetime

import pandas as pd
import streamlit as st

from main import get_data_from_database  # your backend function


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI SQL Data Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# SESSION STATE
# =========================================================
if "history" not in st.session_state:
    st.session_state.history = []          # list of dicts: {query, result, time, timestamp}
if "active_query" not in st.session_state:
    st.session_state.active_query = ""

EXAMPLE_QUERIES = [
    "Total products sold in 2025",
    "Top 5 customers by spending",
    "List all orders from last month",
    "Which product category sells the most?",
]


# =========================================================
# STYLES
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* ---------- App background ---------- */
    .stApp {
        background: radial-gradient(circle at 15% 0%, #1a1035 0%, #0b0b16 45%, #08080f 100%);
        color: #e8e6f5;
    }

    /* ---------- Hide default chrome ---------- */
    #MainMenu, header, footer {visibility: hidden;}

    /* ---------- Animations ---------- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(124, 92, 255, 0.45); }
        50%      { box-shadow: 0 0 0 10px rgba(124, 92, 255, 0); }
    }
    @keyframes dotBlink {
        0%, 80%, 100% { opacity: 0.25; }
        40% { opacity: 1; }
    }

    .fade-in { animation: fadeInUp 0.55s ease both; }

    /* ---------- Hero header ---------- */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #7c5cff, #22d3ee, #7c5cff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 6s ease infinite;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        text-align: center;
        color: #9c98b8;
        font-size: 1.02rem;
        margin-bottom: 2rem;
    }

    /* ---------- Card ---------- */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border-radius: 18px;
        padding: 1.6rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    }

    /* ---------- Text area ---------- */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        color: #f0eefc !important;
        font-size: 16px !important;
        padding: 14px !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .stTextArea textarea:focus {
        border-color: #7c5cff !important;
        box-shadow: 0 0 0 3px rgba(124, 92, 255, 0.25) !important;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        background: linear-gradient(90deg, #7c5cff, #5b8dff);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.65rem 1.4rem;
        transition: transform 0.15s ease, box-shadow 0.25s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        animation: pulseGlow 1.4s infinite;
    }

    /* ---------- Example chips ---------- */
    .chip-btn button {
        background: rgba(124, 92, 255, 0.12) !important;
        border: 1px solid rgba(124, 92, 255, 0.35) !important;
        color: #cfc9ff !important;
        font-weight: 500 !important;
        border-radius: 999px !important;
        padding: 0.35rem 0.9rem !important;
        font-size: 0.85rem !important;
    }
    .chip-btn button:hover {
        background: rgba(124, 92, 255, 0.25) !important;
        transform: translateY(-1px);
    }

    /* ---------- Metric mini-cards ---------- */
    .mini-metric {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 0.9rem 1rem;
        text-align: center;
    }
    .mini-metric .val { font-size: 1.4rem; font-weight: 700; color: #22d3ee; }
    .mini-metric .lbl { font-size: 0.78rem; color: #9c98b8; text-transform: uppercase; letter-spacing: 0.04em; }

    /* ---------- History items ---------- */
    .hist-item {
        background: rgba(255,255,255,0.04);
        border-left: 3px solid #7c5cff;
        border-radius: 8px;
        padding: 0.5rem 0.7rem;
        margin-bottom: 0.5rem;
        font-size: 0.82rem;
        color: #d6d3ec;
    }
    .hist-time { font-size: 0.7rem; color: #7c789a; }

    /* ---------- Answer text ---------- */
    .answer-box {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #f0eefc;
    }

    code, .stCodeBlock, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# RESULT RENDERING HELPERS
# =========================================================
def to_dataframe(result):
    """Best-effort conversion of arbitrary backend output into a DataFrame, or None."""
    if isinstance(result, pd.DataFrame):
        return result
    if isinstance(result, (list, tuple)) and len(result) > 0 and isinstance(result[0], (list, tuple)):
        return pd.DataFrame(result)
    return None


def render_result(query: str, result, elapsed: float):
    df = to_dataframe(result)

    st.markdown('<div class="glass-card fade-in">', unsafe_allow_html=True)

    # --- top metrics row ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="mini-metric"><div class="val">{elapsed:.2f}s</div>'
            f'<div class="lbl">Query Time</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        row_count = len(df) if df is not None else "—"
        st.markdown(
            f'<div class="mini-metric"><div class="val">{row_count}</div>'
            f'<div class="lbl">Rows Returned</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="mini-metric"><div class="val">✅</div>'
            '<div class="lbl">Status</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- main content ---
    if df is not None:
        st.dataframe(df, use_container_width=True, height=min(400, 60 + 35 * len(df)))
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            data=csv,
            file_name="query_result.csv",
            mime="text/csv",
            use_container_width=False,
        )
    else:
        st.markdown(
            f'<div class="answer-box">🔍 {result}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🤖 AI SQL Analyst")
    st.caption("Natural language → SQL → Answers")
    st.markdown("---")

    st.markdown("### 💡 Try asking")
    for q in EXAMPLE_QUERIES:
        st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
        if st.button(q, key=f"ex_{q}", use_container_width=True):
            st.session_state.active_query = q
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🕘 Query History")
    if not st.session_state.history:
        st.caption("No queries yet — ask something!")
    else:
        for item in reversed(st.session_state.history[-8:]):
            st.markdown(
                f'<div class="hist-item">{item["query"]}'
                f'<div class="hist-time">{item["timestamp"]} · {item["time"]:.2f}s</div></div>',
                unsafe_allow_html=True,
            )
        if st.button("🗑️ Clear history", use_container_width=True):
            st.session_state.history = []
            st.rerun()


# =========================================================
# HERO HEADER
# =========================================================
st.markdown('<div class="hero-title fade-in">🤖 AI SQL Data Analyst</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle fade-in">Ask questions about your data in plain English — get instant, accurate answers.</div>',
    unsafe_allow_html=True,
)

# =========================================================
# INPUT CARD
# =========================================================
st.markdown('<div class="glass-card fade-in">', unsafe_allow_html=True)

user_query = st.text_area(
    "💬 Enter your question",
    value=st.session_state.active_query,
    placeholder="e.g., Total products sold in 2025",
    height=100,
    label_visibility="collapsed",
)

col_a, col_b = st.columns([5, 1])
with col_b:
    analyze_clicked = st.button("🚀 Analyze", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# PROCESS QUERY
# =========================================================
if analyze_clicked:
    if user_query.strip() == "":
        st.warning("⚠️ Please enter a question to analyze.")
    else:
        placeholder = st.empty()
        thinking_frames = ["Thinking", "Thinking.", "Thinking..", "Thinking..."]
        start = time.time()

        # light animated "thinking" cue before the (blocking) backend call
        for frame in thinking_frames:
            placeholder.markdown(
                f'<div class="glass-card fade-in" style="text-align:center; color:#9c98b8;">'
                f'🧠 {frame}</div>',
                unsafe_allow_html=True,
            )
            time.sleep(0.12)

        try:
            result = get_data_from_database(user_query)
        except Exception as e:
            placeholder.empty()
            st.error(f"❌ Something went wrong while processing your query:\n\n`{e}`")
        else:
            elapsed = time.time() - start
            placeholder.empty()

            st.session_state.history.append(
                {
                    "query": user_query,
                    "result": result,
                    "time": elapsed,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                }
            )

            render_result(user_query, result, elapsed)