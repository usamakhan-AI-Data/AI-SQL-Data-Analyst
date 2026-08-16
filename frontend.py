"""
AI SQL Data Analyst — Streamlit Frontend
========================================
Neo Data AI edition — dark, gold/red brand theme.

Backend:
    from main import get_data_from_database
"""

import time
import uuid
import textwrap
from datetime import datetime

import pandas as pd
import streamlit as st

from main import get_data_from_database


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI SQL Data Analyst — Neo Data AI",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "history": [],
    "pending_query": "",
    "query_counter": 0,
    "input_key": 0,      # bumped to force the text_area to accept a new default value
    "selected_id": None, # which history item is currently shown in the main panel
    "confirm_clear": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


EXAMPLE_QUERIES = [
    "Total products sold in 2025",
    "Top 5 customers by spending",
    "Orders placed last month",
    "Which category sells the most?",
]


def html(content: str) -> str:
    """Dedent HTML so Streamlit doesn't render it as a Markdown code block."""
    return textwrap.dedent(content).strip()


# =========================================================
# CUSTOM CSS — Neo Data AI dark / gold / red theme
# =========================================================

st.markdown(
    html(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {
            --bg: #08070a;
            --panel-top: rgba(24, 20, 14, 0.96);
            --panel-bottom: rgba(12, 10, 8, 0.97);
            --border: rgba(212, 175, 55, 0.16);
            --border-hover: rgba(212, 175, 55, 0.4);
            --gold: #d4af37;
            --gold-soft: rgba(212, 175, 55, 0.12);
            --red: #b3261e;
            --red-soft: rgba(179, 38, 30, 0.14);
            --text: #f2ede1;
            --text-muted: #8f8877;
            --text-dim: #6b6558;
        }

        html, body, [class*="css"] { font-family: "Inter", sans-serif; }
        code, pre, .stCodeBlock { font-family: "JetBrains Mono", monospace !important; }

        .stApp {
            background:
                radial-gradient(circle at 8% 0%, rgba(212, 175, 55, 0.07), transparent 30%),
                radial-gradient(circle at 92% 8%, rgba(179, 38, 30, 0.06), transparent 28%),
                var(--bg);
            color: var(--text);
        }

        #MainMenu, footer { visibility: hidden; }
        header { background: transparent !important; }
        .block-container { max-width: 1400px; padding-top: 1.3rem; padding-bottom: 3rem; }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b0a08 0%, #07060a 100%);
            border-right: 1px solid var(--border);
        }
        section[data-testid="stSidebar"] .block-container { padding-top: 1.4rem; }
        .sidebar-brand { color: var(--text); font-size: 1.28rem; font-weight: 800; letter-spacing: -0.3px; }
        .sidebar-tag { color: var(--gold); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.10em; margin-top: 2px; }
        .sidebar-subtitle { color: var(--text-dim); font-size: 0.74rem; margin-top: 6px; margin-bottom: 14px; }

        .status-badge {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 6px 12px; border-radius: 999px;
            background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.22);
            color: #86efac; font-size: 0.71rem; font-weight: 600;
        }
        .status-dot {
            width: 7px; height: 7px; border-radius: 50%; background: #4ade80;
            box-shadow: 0 0 6px rgba(74, 222, 128, 0.8);
            animation: statusPulse 2.4s ease-in-out infinite;
        }
        .status-badge.error { background: var(--red-soft); border-color: rgba(179,38,30,0.35); color: #ff9992; }
        .status-badge.error .status-dot { background: #dc2626; box-shadow: 0 0 6px rgba(220,38,38,0.8); }
        @keyframes statusPulse { 0%,100% { opacity: 0.55; transform: scale(0.9);} 50% { opacity: 1; transform: scale(1.1);} }

        .query-label { color: var(--text-dim); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.09em; margin-bottom: 8px; }

        /* HISTORY ITEMS */
        .history-item {
            padding: 8px 10px; border-radius: 9px; margin-bottom: 5px;
            border: 1px solid transparent; cursor: default;
        }
        .history-item.active { background: var(--gold-soft); border-color: var(--border-hover); }
        .history-meta { color: var(--text-dim); font-size: 0.68rem; margin-top: 2px; }

        /* HERO */
        .hero { position: relative; padding: 0.8rem 0 1.6rem 0; overflow: hidden; }
        .hero::before {
            content: ""; position: absolute; width: 360px; height: 160px; top: -90px; left: -20px;
            background: rgba(212, 175, 55, 0.10); filter: blur(80px); border-radius: 50%; pointer-events: none;
        }
        .hero::after {
            content: ""; position: absolute; width: 320px; height: 150px; top: -60px; right: 5%;
            background: rgba(179, 38, 30, 0.08); filter: blur(80px); border-radius: 50%; pointer-events: none;
        }

        .ai-badge {
            position: relative; z-index: 2; display: inline-flex; align-items: center; gap: 8px;
            padding: 6px 12px; margin-bottom: 12px; border-radius: 999px;
            background: var(--gold-soft); border: 1px solid var(--border-hover);
            color: var(--gold); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em;
        }
        .ai-badge-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--gold); box-shadow: 0 0 6px var(--gold); }

        .hero-title {
            position: relative; z-index: 2; font-size: 2.5rem; font-weight: 800; letter-spacing: -1.3px; line-height: 1.15;
            background: linear-gradient(100deg, var(--gold), #f3d878, var(--red), var(--gold));
            background-size: 280% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            animation: gradientFlow 12s ease-in-out infinite; margin: 0;
        }
        @keyframes gradientFlow { 0%,100% { background-position: 0% center; } 50% { background-position: 100% center; } }

        .hero-subtitle { position: relative; z-index: 2; color: var(--text-muted); font-size: 0.94rem; line-height: 1.6; margin-top: 8px; max-width: 700px; }
        .brand-credit { color: var(--text-dim); font-size: 0.72rem; margin-top: 10px; letter-spacing: 0.03em; }
        .brand-credit b { color: var(--gold); font-weight: 700; }

        /* PANELS */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(150deg, var(--panel-top), var(--panel-bottom)) !important;
            border: 1px solid var(--border) !important; border-radius: 16px !important;
            box-shadow: 0 16px 46px rgba(0,0,0,0.30) !important; padding: 1rem !important;
        }

        /* TEXT AREA */
        .stTextArea textarea {
            background: #100d09 !important; border: 1px solid #2a2318 !important; border-radius: 12px !important;
            color: var(--text) !important; font-size: 15px !important; line-height: 1.6 !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        }
        .stTextArea textarea:hover { border-color: #423a24 !important; }
        .stTextArea textarea:focus {
            border-color: var(--gold) !important;
            box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.14) !important;
        }

        /* BUTTONS */
        .stButton > button {
            border-radius: 10px !important; min-height: 42px;
            border: 1px solid rgba(212, 175, 55, 0.3) !important;
            background: linear-gradient(120deg, var(--gold), #b8862b, var(--red)) !important;
            color: #0c0a08 !important; font-weight: 700 !important;
            transition: transform 0.15s ease, filter 0.15s ease, box-shadow 0.15s ease;
        }
        .stButton > button:hover {
            filter: brightness(1.08); transform: translateY(-1px);
            box-shadow: 0 8px 22px rgba(212, 175, 55, 0.20);
        }

        section[data-testid="stSidebar"] .stButton > button {
            background: #100d09 !important; border: 1px solid #241f16 !important;
            color: #d8d0bd !important; text-align: left; font-weight: 500 !important; min-height: 38px;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #17130d !important; border-color: var(--border-hover) !important; color: var(--gold) !important;
        }
        .clear-btn button { border: 1px solid rgba(179,38,30,0.35) !important; background: rgba(179,38,30,0.08) !important; color: #ff9992 !important; }
        .clear-btn button:hover { background: rgba(179,38,30,0.16) !important; }

        /* METRICS */
        [data-testid="stMetric"] {
            background: linear-gradient(150deg, var(--panel-top), var(--panel-bottom));
            border: 1px solid var(--border); border-radius: 13px; padding: 0.85rem 1rem;
        }
        [data-testid="stMetricLabel"] { color: var(--text-dim) !important; font-size: 0.76rem !important; }
        [data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 700 !important; }

        /* TABS */
        .stTabs [data-baseweb="tab-list"] { gap: 6px; background: transparent; }
        .stTabs [data-baseweb="tab"] { color: var(--text-dim); font-weight: 600; padding: 9px 15px; }
        .stTabs [aria-selected="true"] { color: var(--gold) !important; }
        .stTabs [data-baseweb="tab-highlight"] { background: linear-gradient(90deg, var(--gold), var(--red)); }

        [data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 11px; overflow: hidden; }
        .streamlit-expanderHeader { background: #100d09 !important; border-radius: 10px !important; color: #d8d0bd !important; font-weight: 500 !important; }
        .stAlert { border-radius: 11px !important; }

        .section-title { display: flex; align-items: center; gap: 8px; color: var(--text); font-size: 1.15rem; font-weight: 700; margin: 0.7rem 0 1rem 0; }

        .empty-state {
            margin-top: 2rem; padding: 46px 25px; text-align: center;
            background: linear-gradient(150deg, var(--panel-top), var(--panel-bottom));
            border: 1px solid var(--border); border-radius: 16px;
        }
        .empty-icon { font-size: 2.5rem; margin-bottom: 10px; }
        .empty-title { font-size: 1.2rem; font-weight: 700; color: var(--text); margin-bottom: 8px; }
        .empty-description { color: var(--text-dim); font-size: 0.9rem; max-width: 580px; margin: auto; line-height: 1.6; }

        .stDownloadButton > button {
            border-radius: 9px !important; background: #100d09 !important; border: 1px solid #2a2318 !important;
            color: var(--gold) !important; font-weight: 600 !important;
        }
        .stDownloadButton > button:hover { border-color: var(--gold) !important; color: #f3d878 !important; }

        @media (max-width: 768px) {
            .hero-title { font-size: 1.9rem; }
            .hero-subtitle { font-size: 0.86rem; }
            .block-container { padding-left: 1rem; padding-right: 1rem; }
        }
        </style>
        """
    ),
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================

def create_result_id() -> str:
    st.session_state.query_counter += 1
    return f"query_{st.session_state.query_counter}_{uuid.uuid4().hex[:8]}"


def parse_backend_result(raw):
    """Normalize backend response into (sql, data)."""
    sql, data = None, raw
    if (
        isinstance(raw, tuple)
        and len(raw) == 2
        and isinstance(raw[0], str)
        and "select" in raw[0].lower()
    ):
        sql, data = raw
    return sql, data


def to_dataframe(data):
    if isinstance(data, pd.DataFrame):
        return data
    if isinstance(data, (list, tuple)) and data:
        if isinstance(data[0], (list, tuple, dict)):
            return pd.DataFrame(data)
    return None


def run_query(question: str):
    with st.status("Running your question through the AI SQL Analyst...", expanded=True) as status:
        st.write("Interpreting the question")
        start = time.time()
        try:
            raw = get_data_from_database(question)
        except Exception as e:
            status.update(label="Query failed", state="error", expanded=True)
            st.error(f"Database / AI error: {e}")
            return None
        elapsed = time.time() - start
        st.write("SQL generated")
        st.write("Query executed against the database")
        status.update(label=f"Done · {elapsed:.2f}s", state="complete", expanded=False)

    sql, data = parse_backend_result(raw)
    return {
        "id": create_result_id(),
        "query": question,
        "sql": sql,
        "data": data,
        "elapsed": elapsed,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }


def render_result(item: dict, widget_prefix: str):
    df = to_dataframe(item["data"])

    m1, m2, m3 = st.columns(3)
    m1.metric("Query Time", f"{item['elapsed']:.2f}s")
    m2.metric("Rows Returned", len(df) if df is not None else "—")
    m3.metric("Columns", df.shape[1] if df is not None else "—")

    st.write("")

    # numeric column available -> offer a chart tab
    numeric_cols = list(df.select_dtypes(include="number").columns) if df is not None else []
    show_chart = df is not None and not df.empty and len(numeric_cols) >= 1 and len(df.columns) >= 2

    tab_labels = ["Results"]
    if show_chart:
        tab_labels.append("Chart")
    if item["sql"]:
        tab_labels.append("SQL")

    tabs = st.tabs(tab_labels)
    tab_index = 0

    # --- Results tab ---
    with tabs[tab_index]:
        if df is not None:
            if df.empty:
                st.info("The query ran successfully, but returned no rows.")
            else:
                height = min(480, max(170, 60 + 35 * len(df)))
                st.dataframe(df, use_container_width=True, height=height, hide_index=True)
                st.write("")
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"query_result_{item['id']}.csv",
                    mime="text/csv",
                    key=f"{widget_prefix}_download_csv",
                )
        elif item["data"] is not None and not isinstance(item["data"], (list, tuple)):
            # single scalar result (e.g. a COUNT(*) style answer)
            st.metric("Result", str(item["data"]))
        else:
            st.info(str(item["data"]))
    tab_index += 1

    # --- Chart tab ---
    if show_chart:
        with tabs[tab_index]:
            label_col = next((c for c in df.columns if c not in numeric_cols), df.columns[0])
            value_col = numeric_cols[0]
            st.bar_chart(df.set_index(label_col)[value_col])
        tab_index += 1

    # --- SQL tab ---
    if item["sql"]:
        with tabs[tab_index]:
            st.caption("Generated SQL")
            st.code(item["sql"], language="sql")


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        html(
            """
            <div class="sidebar-brand">AI SQL Analyst</div>
            <div class="sidebar-tag">NEO DATA AI</div>
            <div class="sidebar-subtitle">Natural Language → SQL → Data</div>
            """
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        html(
            """
            <span class="status-badge">
                <span class="status-dot"></span>
                Database connected
            </span>
            """
        ),
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown('<div class="query-label">QUICK QUERIES</div>', unsafe_allow_html=True)

    for index, question in enumerate(EXAMPLE_QUERIES):
        if st.button(question, key=f"example_query_{index}", use_container_width=True):
            st.session_state.pending_query = question
            st.session_state.input_key += 1  # forces the text_area to accept the new value
            st.session_state.selected_id = None
            st.rerun()

    st.divider()
    st.markdown('<div class="query-label">QUERY HISTORY</div>', unsafe_allow_html=True)
    st.write("")

    if not st.session_state.history:
        st.caption("Your previous queries will appear here.")
    else:
        recent = list(reversed(st.session_state.history[-10:]))
        for index, item in enumerate(recent):
            label = item["query"]
            if len(label) > 40:
                label = label[:40] + "…"
            is_active = st.session_state.selected_id == item["id"]

            cols = st.columns([1])
            with cols[0]:
                if st.button(
                    ("▸ " if is_active else "") + label,
                    key=f"history_btn_{item['id']}_{index}",
                    use_container_width=True,
                ):
                    st.session_state.selected_id = item["id"]
                    st.rerun()
            st.markdown(
                f'<div class="history-meta">{item["timestamp"]} · {item["elapsed"]:.2f}s</div>',
                unsafe_allow_html=True,
            )

        st.write("")
        clear_col = st.container()
        with clear_col:
            st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
            clear_label = "Confirm clear history?" if st.session_state.confirm_clear else "Clear History"
            if st.button(clear_label, key="clear_history", use_container_width=True):
                if st.session_state.confirm_clear:
                    st.session_state.history = []
                    st.session_state.selected_id = None
                    st.session_state.confirm_clear = False
                else:
                    st.session_state.confirm_clear = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# HERO
# =========================================================

st.markdown(
    html(
        """
        <div class="hero">
            <div class="ai-badge">
                <span class="ai-badge-dot"></span>
                AI POWERED SQL ANALYTICS
            </div>
            <div class="hero-title">AI SQL Data Analyst</div>
            <div class="hero-subtitle">
                Ask your database questions in plain English.
                Generate SQL, execute queries, and explore your data instantly.
            </div>
            <div class="brand-credit">Built by <b>Neo Data AI</b></div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)


# =========================================================
# QUERY INPUT
# =========================================================

with st.container(border=True):
    st.markdown('<div class="query-label">ASK YOUR DATABASE</div>', unsafe_allow_html=True)

    text_key = f"user_query_{st.session_state.input_key}"
    user_query = st.text_area(
        "Your question",
        value=st.session_state.pending_query,
        placeholder="Example: Show me the top 10 customers by total spending in 2025...",
        height=100,
        label_visibility="collapsed",
        key=text_key,
    )

    st.write("")
    col_space, col_button = st.columns([5, 1])
    with col_button:
        analyze_clicked = st.button("Analyze", use_container_width=True, key="analyze_button")


# =========================================================
# MAIN RESULT AREA
# =========================================================

if analyze_clicked:
    query = user_query.strip()

    if not query:
        st.warning("Please enter a question first.")
    else:
        result_item = run_query(query)
        if result_item:
            st.session_state.history.append(result_item)
            st.session_state.selected_id = result_item["id"]
            st.session_state.confirm_clear = False

            st.markdown('<div class="section-title">Analysis Result</div>', unsafe_allow_html=True)
            render_result(result_item, widget_prefix=f"main_{result_item['id']}")

elif st.session_state.selected_id:
    selected = next(
        (i for i in st.session_state.history if i["id"] == st.session_state.selected_id),
        None,
    )
    if selected:
        st.markdown('<div class="section-title">Analysis Result</div>', unsafe_allow_html=True)
        render_result(selected, widget_prefix=f"selected_{selected['id']}")
    elif st.session_state.history:
        latest = st.session_state.history[-1]
        st.markdown('<div class="section-title">Latest Analysis</div>', unsafe_allow_html=True)
        render_result(latest, widget_prefix=f"latest_{latest['id']}")

elif st.session_state.history:
    latest = st.session_state.history[-1]
    st.markdown('<div class="section-title">Latest Analysis</div>', unsafe_allow_html=True)
    render_result(latest, widget_prefix=f"latest_{latest['id']}")

else:
    st.markdown(
        html(
            """
            <div class="empty-state">
                <div class="empty-icon">🗄️</div>
                <div class="empty-title">Ready to analyze your data</div>
                <div class="empty-description">
                    Ask your database a question in plain English. The AI will generate
                    SQL, execute the query, and show you the results.
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
