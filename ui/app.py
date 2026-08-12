"""
AI Product Manager — Main Streamlit Application
Multi-Agent Product Intelligence System
"""
from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Product Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Load CSS ─────────────────────────────────────────────────────────────────
def load_css():
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ─── Extra Inline Styles ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
.stApp { background: #0a0e1a; font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background: #111827 !important; border-right: 1px solid #1e293b; }
[data-testid="stSidebar"] * { color: #f1f5f9 !important; }
.stTabs [data-baseweb="tab-list"] { background: #111827; border-radius: 10px; gap: 4px; }
.stTabs [data-baseweb="tab"] { color: #94a3b8; border-radius: 8px; }
.stTabs [aria-selected="true"] { background: #1e293b; color: #f1f5f9 !important; }
.stButton > button { border-radius: 10px; font-weight: 600; transition: all 0.2s ease; }
.stFileUploader { border-radius: 12px; }
div[data-testid="stMetric"] { background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 16px; }
div[data-testid="stMetric"] label { color: #94a3b8 !important; font-size: 0.8rem !important; }
div[data-testid="stMetric"] div { color: #f1f5f9 !important; }
.stExpander { border: 1px solid #1e293b !important; border-radius: 10px !important; }
.stAlert { border-radius: 10px !important; }
textarea, input, select { background: #111827 !important; color: #f1f5f9 !important; border: 1px solid #1e293b !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Imports after path setup ─────────────────────────────────────────────────
from agents.orchestrator import Orchestrator
from tools.openai_tool import (
    is_api_key_configured, is_gemini_configured, is_openai_configured,
    get_active_provider, get_active_model_display,
)
from tools.file_tool import parse_feedback_csv, parse_analytics_json, validate_feedback_list
from ui.components import (
    render_header, render_workflow_steps, render_all_agent_statuses,
    render_priority_table, render_feature_approval, render_prd,
    render_sprint_board, render_priority_chart, render_feedback_issues,
    render_analytics_chart, render_spider_chart, render_success_banner,
    render_error_banner,
)

# ─── Session State Initialization ────────────────────────────────────────────
def init_session():
    defaults = {
        "orchestrator": None,
        "step": 0,  # 0=config, 1=analyze, 2=prioritize, 3=approve, 4=prd, 5=sprint, 6=done
        "agent_statuses": {},
        "feedback_list": [],
        "analytics_data": {},
        "approved_features": [],
        "log_messages": [],
        "analysis_done": False,
        "prioritization_done": False,
        "approval_done": False,
        "prd_done": False,
        "sprint_done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


def get_orchestrator() -> Orchestrator:
    orch = st.session_state.get("orchestrator")
    if orch is None:
        orch = Orchestrator()
        st.session_state["orchestrator"] = orch
    return orch


def status_callback(agent: str, status: str, message: str):
    """Callback to update session state from orchestrator."""
    agent_statuses = st.session_state.setdefault("agent_statuses", {})
    agent_statuses[agent] = {
        "status": status,
        "message": message,
        "error_message": message if status == "error" else "",
    }
    if message:
        st.session_state.setdefault("log_messages", []).append(f"[{agent}] {message}")


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <div style="font-size:2.5rem;">🤖</div>
        <h2 style="color:#f1f5f9; font-size:1.1rem; font-weight:700; margin:8px 0 4px 0;">AI Product Manager</h2>
        <p style="color:#64748b; font-size:0.75rem; margin:0;">Multi-Agent System</p>
    </div>
    <hr style="border-color:#1e293b; margin:12px 0;">
    """, unsafe_allow_html=True)

    # API Key status — prefer Gemini, fall back to OpenAI
    gemini_ok = is_gemini_configured()
    openai_ok = is_openai_configured()
    active = get_active_provider()

    if gemini_ok:
        st.markdown(f"✅ **Gemini API:** Connected")
        st.markdown(f"<div style='font-size:0.75rem; color:#4ade80; margin-top:-6px;'>Model: {get_active_model_display()}</div>", unsafe_allow_html=True)
    elif openai_ok:
        st.markdown(f"✅ **OpenAI API:** Connected")
        st.markdown(f"<div style='font-size:0.75rem; color:#60a5fa; margin-top:-6px;'>Model: {get_active_model_display()}</div>", unsafe_allow_html=True)
    else:
        st.markdown("⚠️ **AI API:** Not configured")
        st.markdown("<div style='font-size:0.78rem; color:#fbbf24; margin-top:-4px;'>Set either key below (Gemini recommended)</div>", unsafe_allow_html=True)

        with st.expander("🔑 Enter API Keys", expanded=True):
            gemini_key_input = st.text_input(
                "Google Gemini API Key (Recommended)",
                type="password",
                key="gemini_key_input",
                placeholder="Paste from https://aistudio.google.com/apikey",
                help="Gemini is cheaper and faster for structured JSON output",
            )
            if gemini_key_input:
                os.environ["GOOGLE_API_KEY"] = gemini_key_input
                st.success("✅ Gemini API key set! Reload to apply.")

            st.markdown("---")
            openai_key_input = st.text_input(
                "OpenAI API Key (Alternative)",
                type="password",
                key="openai_key_input",
                placeholder="Paste from https://platform.openai.com/api-keys",
            )
            if openai_key_input:
                os.environ["OPENAI_API_KEY"] = openai_key_input
                st.success("✅ OpenAI API key set! Reload to apply.")

    st.markdown("---")

    # Navigation
    st.markdown("**🗂️ Navigation**")
    nav_options = [
        "🚀 New Analysis",
        "📊 View Results",
        "📝 PRD Library",
        "🗄️ Session History",
        "⚙️ Error Logs",
    ]
    nav = st.radio("Navigation", nav_options, label_visibility="collapsed", key="nav_radio")

    st.markdown("---")

    # Agent status in sidebar
    if "agent_statuses" in st.session_state and st.session_state.agent_statuses:
        st.markdown("**🤖 Agent Status**")
        render_all_agent_statuses(st.session_state.agent_statuses)

    st.markdown("---")
    footer_model = get_active_model_display() if is_api_key_configured() else "Configure API key →"
    footer_provider = "Gemini or OpenAI"
    st.markdown(f"""
    <div style="color:#64748b; font-size:0.72rem; text-align:center;">
        6 AI Agents • RAG • Long-Term Memory<br>
        Powered by <span style="color:#94a3b8;">{footer_model}</span>
    </div>
    """, unsafe_allow_html=True)


# ─── Main Content ─────────────────────────────────────────────────────────────

render_header()
st.markdown("<hr style='border-color:#1e293b; margin:1rem 0;'>", unsafe_allow_html=True)

# ─── NEW ANALYSIS TAB ─────────────────────────────────────────────────────────
if "New Analysis" in nav:

    render_workflow_steps(st.session_state.step)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── STEP 0: CONFIGURATION ─────────────────────────────────────────────────
    if st.session_state.step == 0:
        st.markdown("## ⚙️ Step 1: Configure Your Product")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 📦 Product Details")
            product_name = st.text_input(
                "Product Name",
                value="DataPulse Analytics",
                placeholder="e.g., Acme Analytics Platform",
                key="product_name_input",
            )
            product_domain = st.text_input(
                "Product Domain / Category",
                value="business analytics software",
                placeholder="e.g., project management software",
                key="product_domain_input",
            )
            competitors_input = st.text_input(
                "Known Competitors (comma-separated, optional)",
                value="Tableau, Power BI, Looker",
                placeholder="e.g., Competitor A, Competitor B",
                key="competitors_input",
            )
            st.markdown("### 🎯 Business Goals")
            goals_input = st.text_area(
                "Business Goals (one per line)",
                value="Improve user retention by 15%\nReduce churn rate below 5%\nExpand to enterprise market\nAchieve 50K MAU by Q4",
                height=110,
                key="goals_input",
            )

        with col2:
            st.markdown("### 🔧 Engineering Settings")
            capacity = st.slider("Sprint Story Points Capacity", 20, 100, 40, 5, key="capacity_slider")
            team_size = st.slider("Engineering Team Size", 1, 20, 5, 1, key="team_slider")
            sprint_num = st.number_input("Sprint Number", 1, 100, 24, 1, key="sprint_num_input")

            st.markdown("### 📁 Upload Data")
            feedback_file = st.file_uploader(
                "Customer Feedback (CSV)",
                type=["csv"],
                help="CSV with a 'feedback' or 'text' column",
                key="feedback_uploader",
            )
            analytics_file = st.file_uploader(
                "Product Analytics (JSON)",
                type=["json"],
                help="JSON file with product metrics",
                key="analytics_uploader",
            )

            use_sample = st.checkbox(
                "📦 Use built-in sample data (for demo)",
                value=True if not feedback_file else False,
                key="use_sample_check",
            )

        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            start_btn = st.button("🚀 Start AI Analysis", type="primary", use_container_width=True, key="start_btn")

        if start_btn:
            if not is_api_key_configured():
                render_error_banner("Please configure your Google Gemini (or OpenAI) API key in the sidebar first.")
            else:
                # Load feedback
                if feedback_file:
                    try:
                        raw_feedback = parse_feedback_csv(feedback_file.getvalue())
                        valid_feedback, _ = validate_feedback_list(raw_feedback)
                        st.session_state.feedback_list = valid_feedback
                    except Exception as e:
                        render_error_banner(f"Feedback file error: {e}")
                        st.stop()
                elif use_sample:
                    sample_path = ROOT / "data" / "sample_feedback.csv"
                    if sample_path.exists():
                        with open(sample_path, "rb") as f:
                            raw = parse_feedback_csv(f.read())
                            valid, _ = validate_feedback_list(raw)
                            st.session_state.feedback_list = valid
                    else:
                        st.session_state.feedback_list = get_sample_feedback()
                else:
                    render_error_banner("Please upload a feedback CSV or enable sample data.")
                    st.stop()

                # Load analytics
                if analytics_file:
                    try:
                        st.session_state.analytics_data = parse_analytics_json(analytics_file.getvalue())
                    except Exception as e:
                        render_error_banner(f"Analytics file error: {e}")
                        st.stop()
                elif use_sample:
                    sample_path = ROOT / "data" / "sample_analytics.json"
                    if sample_path.exists():
                        with open(sample_path) as f:
                            st.session_state.analytics_data = json.load(f)
                    else:
                        st.session_state.analytics_data = get_sample_analytics()

                # Configure orchestrator
                orch = get_orchestrator()
                orch.set_status_callback(status_callback)
                orch.configure(
                    product_name=product_name,
                    product_domain=product_domain,
                    business_goals=[g.strip() for g in goals_input.split("\n") if g.strip()],
                    engineering_capacity=capacity,
                    team_size=team_size,
                    sprint_number=sprint_num,
                    competitors=[c.strip() for c in competitors_input.split(",") if c.strip()],
                )
                st.session_state.step = 1
                st.rerun()

    # ── STEP 1: ANALYSIS ──────────────────────────────────────────────────────
    elif st.session_state.step == 1:
        st.markdown("## 🔬 Step 2: AI Analysis in Progress")

        orch = get_orchestrator()
        feedback_list = st.session_state.feedback_list
        analytics_data = st.session_state.analytics_data

        col1, col2 = st.columns([2, 1])

        with col2:
            st.markdown("### 🤖 Agent Status")
            status_placeholder = st.empty()
            with status_placeholder.container():
                render_all_agent_statuses(st.session_state.agent_statuses)

        with col1:
            if not st.session_state.analysis_done:
                with st.spinner(""):
                    progress_bar = st.progress(0, "Starting analysis...")

                    # Run parallel analysis
                    progress_bar.progress(10, "🚀 Launching agents in parallel...")
                    results = orch.run_parallel_analysis(feedback_list, analytics_data)

                    progress_bar.progress(70, "✅ Parallel analysis complete...")
                    with status_placeholder.container():
                        render_all_agent_statuses(st.session_state.agent_statuses)

                    # Prioritization
                    progress_bar.progress(80, "⚡ Running prioritization agent...")
                    orch.run_prioritization()
                    with status_placeholder.container():
                        render_all_agent_statuses(st.session_state.agent_statuses)

                    progress_bar.progress(100, "✅ Analysis complete!")
                    st.session_state.analysis_done = True
                    st.session_state.prioritization_done = True

            state = orch.get_state()

            # Show feedback summary
            if state.feedback_analysis:
                fb = state.feedback_analysis
                st.markdown("### 💬 Feedback Analysis")
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric("Total Feedback", fb.get("total_feedback", 0))
                with col_m2:
                    st.metric("Issues Found", len(fb.get("issues", [])))
                with col_m3:
                    st.metric("Feature Requests", len(fb.get("feature_requests", [])))

                st.info(f"📊 **Sentiment:** {fb.get('overall_sentiment', 'N/A')} | **Summary:** {fb.get('analysis_summary', '')}")

                col_fb1, col_fb2 = st.columns(2)
                with col_fb1:
                    st.markdown("**Top Issues**")
                    render_feedback_issues(fb.get("issues", []))
                with col_fb2:
                    st.markdown("**Feature Requests**")
                    for req in fb.get("feature_requests", [])[:6]:
                        st.markdown(f"""
                        <div style="background:rgba(26,34,53,0.8); border:1px solid #1e293b;
                                    border-radius:8px; padding:10px 14px; margin:4px 0;">
                            <span style="color:#f1f5f9; font-weight:500;">{req.get('feature','')}</span>
                            <span style="float:right; color:#3b82f6; font-size:0.8rem;">
                                {req.get('frequency',0)} requests
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

        # Proceed button
        if st.session_state.analysis_done:
            render_success_banner("All 3 analysis agents completed successfully!")
            if st.button("➡️ View Priority Recommendations", type="primary", key="goto_priority_btn"):
                st.session_state.step = 2
                st.rerun()

    # ── STEP 2: PRIORITIZATION ────────────────────────────────────────────────
    elif st.session_state.step == 2:
        orch = get_orchestrator()
        state = orch.get_state()
        pr = state.prioritization_result

        st.markdown("## ⚡ Step 3: Feature Priority Recommendations")

        if pr:
            # Summary metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("P0 Critical", pr.get("p0_count", 0))
            with col2:
                st.metric("P1 High", pr.get("p1_count", 0))
            with col3:
                st.metric("P2 Medium", pr.get("p2_count", 0))
            with col4:
                st.metric("P3 Low", pr.get("p3_count", 0))
            with col5:
                st.metric("Total Features", len(pr.get("features", [])))

            st.info(f"💡 **Recommendation:** {pr.get('recommendation_summary', '')}")

            col_left, col_right = st.columns([3, 2])
            with col_left:
                render_priority_table(pr.get("features", []))
            with col_right:
                st.markdown("**Priority Score Chart**")
                render_priority_chart(pr.get("features", []))

            # Feature detail cards
            st.markdown("---")
            st.markdown("### 🔍 Feature Details")
            features = pr.get("features", [])
            if features:
                sel_feature = st.selectbox(
                    "Select feature to inspect",
                    [f.get("feature", "") for f in features],
                    key="feature_inspect_select",
                )
                selected = next((f for f in features if f.get("feature") == sel_feature), None)
                if selected:
                    col_d1, col_d2 = st.columns([1, 1])
                    with col_d1:
                        render_spider_chart(selected)
                    with col_d2:
                        st.markdown(f"**Feature:** {selected.get('feature')}")
                        st.markdown(f"**Priority:** {selected.get('priority')} | **Score:** {selected.get('priority_score', 0):.2f}/10")
                        st.markdown(f"**Description:** {selected.get('description', '')}")
                        st.markdown(f"**Reason:** {selected.get('reason', '')}")
                        st.markdown(f"**Effort:** {selected.get('estimated_effort', 'TBD')}")
                        if selected.get("dependencies"):
                            st.markdown(f"**Dependencies:** {', '.join(selected['dependencies'])}")

        if st.button("👥 Proceed to Human Approval", type="primary", key="goto_approval_btn"):
            st.session_state.step = 3
            st.rerun()

    # ── STEP 3: HUMAN APPROVAL ────────────────────────────────────────────────
    elif st.session_state.step == 3:
        orch = get_orchestrator()
        state = orch.get_state()
        pr = state.prioritization_result

        st.markdown("## 👥 Step 4: Product Manager Review & Approval")
        st.markdown("""
        <div style="background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.2);
                    border-radius:12px; padding:16px 20px; margin-bottom:20px;">
            <strong style="color:#3b82f6;">🧑‍💼 Human-in-the-Loop Checkpoint</strong><br>
            <span style="color:#94a3b8; font-size:0.9rem;">
                Review the AI-recommended features below. Check the features you approve.
                You can override priorities, remove features, or approve all.
                Only approved features will proceed to PRD generation and sprint planning.
            </span>
        </div>
        """, unsafe_allow_html=True)

        features = pr.get("features", []) if pr else []

        if not features:
            render_error_banner(
                "No features were generated by the prioritization agent. "
                "This typically happens if the analysis step didn't complete successfully "
                "or the AI API encountered an issue. Please go back to Step 1, re-run the analysis, "
                "or start a new session with valid sample data."
            )
            col_back1, col_back2, col_back3 = st.columns([1, 1, 2])
            with col_back1:
                if st.button("← Back to Priorities", use_container_width=True, key="back_empty_feat_btn"):
                    st.session_state.step = 2
                    st.rerun()
            with col_back2:
                if st.button("🔄 Start New Analysis", use_container_width=True, key="restart_empty_feat_btn"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    init_session()
                    st.rerun()
            st.stop()

        approved = render_feature_approval(features)

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            if st.button("✅ Approve Selected Features", type="primary", use_container_width=True, key="approve_btn"):
                if not approved:
                    render_error_banner(
                        f"Please select at least one feature to approve. "
                        f"There are {len(features)} features available — "
                        f"use the '📋 Select All' button above or check individual 'Approve' boxes."
                    )
                else:
                    orch.set_approved_features(approved)
                    st.session_state.approved_features = approved
                    st.session_state.approval_done = True
                    render_success_banner(f"Approved {len(approved)} feature(s) for PRD generation!")
                    time.sleep(1)
                    st.session_state.step = 4
                    st.rerun()
        with col_btn2:
            if st.button("← Back to Priorities", use_container_width=True, key="back_priority_btn"):
                st.session_state.step = 2
                st.rerun()

    # ── STEP 4: PRD GENERATION ────────────────────────────────────────────────
    elif st.session_state.step == 4:
        orch = get_orchestrator()
        state = orch.get_state()

        st.markdown("## 📝 Step 5: PRD Generation")
        approved = st.session_state.approved_features

        st.info(f"📋 Generating PRDs for {len(approved)} approved feature(s)...")

        if not st.session_state.prd_done:
            with st.spinner("AI is writing comprehensive PRDs... This may take 30-60 seconds."):
                col_status, _ = st.columns([1, 2])
                with col_status:
                    render_all_agent_statuses(st.session_state.agent_statuses)
                success = orch.run_prd_generation()
                st.session_state.prd_done = success
                with col_status:
                    render_all_agent_statuses(st.session_state.agent_statuses)

        state = orch.get_state()
        prds = state.prds or []

        if prds:
            render_success_banner(f"Generated {len(prds)} PRD(s) successfully!")
            st.markdown("---")
            for prd in prds:
                render_prd(prd)
                st.markdown("---")
                # Download button
                st.download_button(
                    f"⬇️ Download PRD: {prd.get('feature_name','Feature')}",
                    data=json.dumps(prd, indent=2),
                    file_name=f"prd_{prd.get('feature_name','feature').lower().replace(' ', '_')}.json",
                    mime="application/json",
                    key=f"download_prd_{prd.get('feature_name','').replace(' ','_')}",
                )

        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            if st.button("🏃 Create Sprint Plan", type="primary", key="goto_sprint_btn"):
                st.session_state.step = 5
                st.rerun()

    # ── STEP 5: SPRINT PLANNING ───────────────────────────────────────────────
    elif st.session_state.step == 5:
        orch = get_orchestrator()
        state = orch.get_state()

        st.markdown("## 🏃 Step 6: Sprint Planning")

        if not st.session_state.sprint_done:
            with st.spinner("Creating sprint plan..."):
                success = orch.run_sprint_planning()
                st.session_state.sprint_done = success
                orch.save_session()

        state = orch.get_state()
        sprint = state.sprint_plan

        if sprint:
            render_success_banner(f"{sprint.get('sprint_name','Sprint')} plan created!")
            st.markdown("---")
            render_sprint_board(sprint)

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Definition of Done**")
                for dod in sprint.get("definition_of_done", []):
                    st.markdown(f"✓ {dod}")
            with col2:
                st.markdown("**Sprint Risks**")
                for risk in sprint.get("risks", []):
                    st.markdown(f"⚠️ {risk}")

            # Download
            st.download_button(
                "⬇️ Download Sprint Plan (JSON)",
                data=json.dumps(sprint, indent=2),
                file_name=f"sprint_{sprint.get('sprint_number', 1)}_plan.json",
                mime="application/json",
                key="download_sprint_btn",
            )

        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            if st.button("🎉 Complete & View Summary", type="primary", key="goto_done_btn"):
                st.session_state.step = 6
                st.rerun()

    # ── STEP 6: DONE ──────────────────────────────────────────────────────────
    elif st.session_state.step == 6:
        orch = get_orchestrator()
        state = orch.get_state()

        st.markdown("""
        <div style="text-align:center; padding:2rem 0;">
            <div style="font-size:4rem;">🎉</div>
            <h2 style="background:linear-gradient(135deg,#10b981,#3b82f6);
                       -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                       font-size:2rem; font-weight:800;">Analysis Complete!</h2>
            <p style="color:#94a3b8;">Your AI Product Manager has finished the full lifecycle analysis.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            fb = state.feedback_analysis or {}
            st.metric("Feedback Analyzed", fb.get("total_feedback", 0))
        with col2:
            pr = state.prioritization_result or {}
            st.metric("Features Ranked", len(pr.get("features", [])))
        with col3:
            st.metric("PRDs Generated", len(state.prds or []))
        with col4:
            sprint = state.sprint_plan or {}
            st.metric("Sprint Tasks", len(sprint.get("tasks", [])))

        st.markdown("---")
        st.markdown("### 🤖 Agent Pipeline Summary")
        render_all_agent_statuses(st.session_state.agent_statuses)

        st.markdown("---")
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("🔄 Start New Analysis", use_container_width=True, key="new_analysis_btn"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                init_session()
                st.rerun()


# ─── VIEW RESULTS TAB ─────────────────────────────────────────────────────────
elif "View Results" in nav:
    st.markdown("## 📊 Current Session Results")
    orch = st.session_state.orchestrator
    if not orch:
        st.info("No active session. Start a new analysis first.")
    else:
        state = orch.get_state()
        tabs = st.tabs(["💬 Feedback", "🔍 Competitors", "📈 Analytics", "⚡ Priorities"])

        with tabs[0]:
            fb = state.feedback_analysis
            if fb:
                st.markdown(f"**Total Feedback:** {fb.get('total_feedback')} | **Sentiment:** {fb.get('overall_sentiment')}")
                st.info(fb.get('analysis_summary', ''))
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Issues**")
                    render_feedback_issues(fb.get("issues", []))
                with col2:
                    st.markdown("**Feature Requests**")
                    for req in fb.get("feature_requests", []):
                        st.markdown(f"- **{req.get('feature')}** — {req.get('frequency')} requests ({req.get('impact')} impact)")
            else:
                st.info("No feedback analysis available yet.")

        with tabs[1]:
            ca = state.competitor_analysis
            if ca:
                st.info(ca.get("analysis_summary", ""))
                for comp in ca.get("competitors", []):
                    with st.expander(f"🏢 {comp.get('name', '')}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**Strengths**")
                            for s in comp.get("strengths", []):
                                st.markdown(f"✅ {s}")
                        with c2:
                            st.markdown("**Weaknesses**")
                            for w in comp.get("weaknesses", []):
                                st.markdown(f"❌ {w}")
                st.markdown("**Market Gaps**")
                for gap in ca.get("market_gaps", []):
                    st.markdown(f"🎯 {gap}")
            else:
                st.info("No competitor analysis available yet.")

        with tabs[2]:
            pa = state.product_analytics
            if pa:
                st.info(pa.get("analytics_summary", ""))
                render_analytics_chart(pa.get("feature_metrics", []))
                for m in pa.get("feature_metrics", []):
                    st.markdown(f"- **{m.get('feature')}**: {m.get('usage_percent', 'N/A')}% usage | "
                                f"{m.get('error_rate', 'N/A')}% errors | trend={m.get('trend')}")
            else:
                st.info("No analytics available yet.")

        with tabs[3]:
            pr = state.prioritization_result
            if pr:
                render_priority_chart(pr.get("features", []))
                render_priority_table(pr.get("features", []))
            else:
                st.info("No prioritization available yet.")


# ─── PRD LIBRARY TAB ──────────────────────────────────────────────────────────
elif "PRD Library" in nav:
    st.markdown("## 📝 PRD Library")

    orch = st.session_state.orchestrator
    current_prds = []
    if orch:
        state = orch.get_state()
        current_prds = state.prds or []

    if current_prds:
        st.markdown(f"**{len(current_prds)} PRD(s) from current session:**")
        selected_prd_name = st.selectbox(
            "Select PRD",
            [p.get("feature_name", "Feature") for p in current_prds],
            key="prd_library_select",
        )
        selected_prd = next((p for p in current_prds if p.get("feature_name") == selected_prd_name), None)
        if selected_prd:
            render_prd(selected_prd)
            st.download_button(
                "⬇️ Download PRD",
                data=json.dumps(selected_prd, indent=2),
                file_name=f"prd_{selected_prd_name.lower().replace(' ', '_')}.json",
                mime="application/json",
                key="prd_library_download",
            )
    else:
        st.info("No PRDs generated yet. Complete an analysis first.")


# ─── SESSION HISTORY TAB ──────────────────────────────────────────────────────
elif "Session History" in nav:
    st.markdown("## 🗄️ Session History")
    try:
        from memory.long_term import LongTermMemory
        ltm = LongTermMemory()
        sessions = ltm.list_sessions()
        if sessions:
            for s in sessions:
                st.markdown(f"""
                <div style="background:#111827; border:1px solid #1e293b; border-radius:10px;
                            padding:12px 16px; margin:6px 0;">
                    <strong style="color:#f1f5f9;">{s.get('product_name','')}</strong>
                    <span style="color:#64748b; font-size:0.8rem; float:right;">
                        {s.get('created_at','')[:19]}
                    </span><br>
                    <span style="color:#94a3b8; font-size:0.8rem;">ID: {s.get('session_id','')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No session history found.")
    except Exception as e:
        st.warning(f"Could not load session history: {e}")


# ─── ERROR LOGS TAB ───────────────────────────────────────────────────────────
elif "Error Logs" in nav:
    st.markdown("## ⚙️ Error Logs")
    try:
        from memory.long_term import LongTermMemory
        ltm = LongTermMemory()
        errors = ltm.get_errors()
        if errors:
            for err in errors:
                st.markdown(f"""
                <div style="background:rgba(239,68,68,0.05); border:1px solid rgba(239,68,68,0.2);
                            border-radius:10px; padding:12px 16px; margin:6px 0;">
                    <strong style="color:#ef4444;">{err.get('agent_name','')}</strong>
                    <span style="color:#64748b; font-size:0.8rem; float:right;">{err.get('timestamp','')[:19]}</span><br>
                    <span style="color:#94a3b8; font-size:0.85rem;">{err.get('error_message','')[:200]}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No errors logged.")
    except Exception as e:
        st.warning(f"Could not load error logs: {e}")


# ─── Sample Data Helpers ──────────────────────────────────────────────────────
def get_sample_feedback() -> list:
    """Return inline sample feedback if sample file not found."""
    return [
        "The app crashes whenever I try to upload a CSV file larger than 10MB",
        "Reports take forever to load, sometimes more than 2 minutes",
        "Please add dark mode, my eyes hurt after long sessions",
        "The mobile app is unusable on iPhone, nothing loads properly",
        "I love the dashboard but wish I could customize the widgets",
        "Export to PDF is broken, it only exports the first page",
        "The search function doesn't find results that clearly exist",
        "Can you add more chart types? I need a waterfall chart",
        "Notifications are not working, I'm missing important alerts",
        "The onboarding is confusing, took me 3 days to figure out basic features",
        "Please add API access so I can integrate with our internal tools",
        "The filter options on the reports page reset every time I navigate away",
        "Collaboration features would be amazing, we need to share dashboards with the team",
        "Your customer support is incredibly slow, waited 4 days for a response",
        "The pricing is too high for small teams, please add a startup plan",
    ] * 33  # 495 items


def get_sample_analytics() -> dict:
    """Return inline sample analytics data."""
    return {
        "product": "DataPulse Analytics",
        "period": "Q3 2024",
        "overall_dau": 12400,
        "overall_mau": 48200,
        "overall_retention_30d": 61.2,
        "features": [
            {"name": "Reports", "usage_percent": 78, "error_rate": 4.2, "retention_impact": "High", "trend": "Increasing", "avg_session_duration": 420},
            {"name": "Dashboard", "usage_percent": 91, "error_rate": 1.1, "retention_impact": "High", "trend": "Stable", "avg_session_duration": 680},
            {"name": "Mobile App", "usage_percent": 34, "error_rate": 8.7, "retention_impact": "Medium", "trend": "Decreasing", "avg_session_duration": 180},
            {"name": "CSV Export", "usage_percent": 55, "error_rate": 12.3, "retention_impact": "High", "trend": "Stable", "avg_session_duration": 90},
            {"name": "Alerts", "usage_percent": 22, "error_rate": 15.1, "retention_impact": "Medium", "trend": "Decreasing", "avg_session_duration": 45},
            {"name": "Collaboration", "usage_percent": 8, "error_rate": 2.1, "retention_impact": "Low", "trend": "Increasing", "avg_session_duration": 300},
            {"name": "Search", "usage_percent": 67, "error_rate": 6.8, "retention_impact": "High", "trend": "Stable", "avg_session_duration": 120},
            {"name": "API Access", "usage_percent": 18, "error_rate": 3.2, "retention_impact": "Medium", "trend": "Increasing", "avg_session_duration": 250},
        ]
    }
