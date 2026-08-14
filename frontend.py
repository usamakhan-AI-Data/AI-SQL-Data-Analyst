"""
AI SQL Data Analyst — Streamlit Frontend (v2)
------------------------------------------------
Dark, professional dashboard layout. Leans on native Streamlit components
(st.status, st.tabs, st.metric, st.code) for reliability and familiar UX,
with light CSS polish rather than heavy custom animation.
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
    st.session_state.history = []            # list of dicts: query, sql, data, elapsed, timestamp
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""

EXAMPLE_QUERIES = [
    "Total products sold in 2025",
    "Top 5 customers by spending",
    "Orders placed last month",
    "Which category sells the most?",
]


# =========================================================
# STYLES (minimal, purposeful — not distracting)
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    code, pre, .stCodeBlock { font-family: 'JetBrains Mono', monospace !important; }

    .stApp { background: #0e0e17; color: #e6e4f0; }
    #MainMenu, footer { visibility: hidden; }

    .app-title {
        font-size: 2.1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #8b5cf6, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .app-subtitle { color: #9491ac; font-size: 0.95rem; margin-bottom: 1.4rem; }

    .status-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.35);
        color: #4ade80;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: #4ade80; }

    .stTextArea textarea {
        background: #15151f !important;
        border: 1px solid #2c2c42 !important;
        border-radius: 10px !important;
        color: #f0eefc !important;
        font-size: 15.5px !important;
    }
    .stTextArea textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.25) !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #7c3aed, #38bdf8);
        color: white; border: none; border-radius: 10px;
        font-weight: 600; padding: 0.55rem 1.2rem;
        transition: filter 0.15s ease, transform 0.1s ease;
    }
    .stButton > button:hover { filter: brightness(1.1); transform: translateY(-1px); }

    section[data-testid="stSidebar"] .stButton > button {
        background: #1c1c2b;
        border: 1px solid #2c2c42;
        color: #cfc9ff;
        font-weight: 500;
        text-align: left;
        width: 100%;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #23233a;
        border-color: #7c3aed;
    }

    .stTabs [data-baseweb="tab"] { color: #9491ac; font-weight: 500; }
    .stTabs [aria-selected="true"] { color: #a78bfa !important; }

    section[data-testid="stSidebar"] { background: #0c0c14; border-right: 1px solid #1f1f2e; }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================
def parse_backend_result(raw):
    """
    Normalizes whatever get_data_from_database returns into (sql, data).
    Supports: (sql, result) tuples, plain rows/DataFrame, or plain strings.
    """
    sql = None
    data = raw
    if isinstance(raw, tuple) and len(raw) == 2 and isinstance(raw[0], str) and "select" in raw[0].lower():
        sql, data = raw
    return sql, data


def to_dataframe(data):
    if isinstance(data, pd.DataFrame):
        return data
    if isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], (list, tuple)):
        return pd.DataFrame(data)
    return None


def run_query(question: str):
    """Runs the backend call inside a step-by-step status panel."""
    with st.status("Working on your question…", expanded=True) as status:
        st.write("🧠 Understanding your question")
        time.sleep(0.15)
        st.write("🛠️ Generating SQL query")
        start = time.time()
        try:
            raw = get_data_from_database(question)
        except Exception as e:
            status.update(label="Failed", state="error", expanded=True)
            st.error(f"❌ {e}")
            return None
        elapsed = time.time() - start
        st.write("📡 Executing against database")
        time.sleep(0.1)
        status.update(label=f"Done in {elapsed:.2f}s", state="complete", expanded=False)

    sql, data = parse_backend_result(raw)
    return {
        "query": question,
        "sql": sql,
        "data": data,
        "elapsed": elapsed,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }


def render_result(item: dict):
    df = to_dataframe(item["data"])

    m1, m2, m3 = st.columns(3)
    m1.metric("Query time", f"{item['elapsed']:.2f}s")
    m2.metric("Rows returned", len(df) if df is not None else "—")
    m3.metric("Status", "Success ✅")

    tab_labels = ["📊 Result"] + (["🧾 SQL"] if item["sql"] else [])
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        if df is not None:
            st.dataframe(df, use_container_width=True, height=min(420, 60 + 35 * len(df)))
            st.download_button(
                "⬇️ Download CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="query_result.csv",
                mime="text/csv",
            )
        else:
            st.markdown(f"🔍 {item['data']}")

    if item["sql"]:
        with tabs[1]:
            st.code(item["sql"], language="sql")  # built-in copy button


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🤖 SQL Analyst")
    st.markdown('<span class="status-badge"><span class="status-dot"></span> Database connected</span>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**Try an example**")
    for q in EXAMPLE_QUERIES:
        if st.button(q, key=f"ex_{q}"):
            st.session_state.pending_query = q

    st.markdown("---")
    st.markdown("**History**")
    if not st.session_state.history:
        st.caption("No queries yet.")
    else:
        for item in reversed(st.session_state.history[-10:]):
            label = item["query"][:38] + ("…" if len(item["query"]) > 38 else "")
            with st.expander(label):
                st.caption(f"{item['timestamp']} · {item['elapsed']:.2f}s")
                render_result(item)
        if st.button("🗑️ Clear history"):
            st.session_state.history = []
            st.rerun()


# =========================================================
# MAIN — HEADER
# =========================================================
st.markdown('<div class="app-title">AI SQL Data Analyst</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Ask a question in plain English. Get SQL, data, and answers instantly.</div>', unsafe_allow_html=True)

# =========================================================
# MAIN — INPUT
# =========================================================
with st.container(border=True):
    user_query = st.text_area(
        "Your question",
        value=st.session_state.pending_query,
        placeholder="e.g., Total products sold in 2025",
        height=90,
        label_visibility="collapsed",
    )
    col_l, col_r = st.columns([5, 1])
    with col_r:
        analyze_clicked = st.button("🚀 Analyze", use_container_width=True)

st.write("")

# =========================================================
# MAIN — RESULT
# =========================================================
if analyze_clicked:
    st.session_state.pending_query = ""
    if user_query.strip() == "":
        st.warning("Please enter a question first.")
    else:
        result_item = run_query(user_query)
        if result_item:
            st.session_state.history.append(result_item)
            st.subheader("Result")
            render_result(result_item)
elif st.session_state.history:
    st.subheader("Latest result")
    render_result(st.session_state.history[-1])
else:
    st.info("Ask a question above, or pick an example from the sidebar to get started.")
