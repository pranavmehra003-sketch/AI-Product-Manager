"""
Reusable UI components for the AI Product Manager Streamlit app.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# ─── Color Palette ────────────────────────────────────────────────────────────

PRIORITY_COLORS = {
    "P0": "#ef4444",
    "P1": "#f97316",
    "P2": "#eab308",
    "P3": "#6b7280",
}

AGENT_ICONS = {
    "feedback_agent": "💬",
    "competitor_agent": "🔍",
    "analytics_agent": "📊",
    "prioritization_agent": "⚡",
    "prd_agent": "📝",
    "sprint_agent": "🏃",
    "orchestrator": "🧠",
    "human_approval": "✅",
}

STATUS_ICONS = {
    "pending": "⏳",
    "running": "🔄",
    "success": "✅",
    "error": "❌",
    "skipped": "⏭️",
}


# ─── Header Components ────────────────────────────────────────────────────────

def render_header():
    """Render the BhashaSetu-style glassmorphism hero header."""
    st.markdown("""
    <header style="text-align:center; padding: 1.8rem 0 1rem 0;" role="banner">
        <div style="display:flex; justify-content:center; align-items:center; gap:12px; margin-bottom:14px; flex-wrap:wrap;">
            <div class="hero-badge">
                <span style="font-size:1.05rem;">🤖</span>
                <span>Multi-Agent Autonomous Product Intelligence</span>
            </div>
            <div class="status-badge-live">
                <span class="status-dot"></span>
                <span>System Online • Gemini 3.8 Live</span>
            </div>
        </div>
        <h1 class="hero-title">
            AI Product Manager
        </h1>
        <p class="hero-subtitle">
            Autonomous multi-agent product intelligence: from customer feedback ingestion and competitor gap discovery to prioritized roadmap scoring and sprint-ready PRD synthesis.
        </p>
    </header>
    """, unsafe_allow_html=True)


def render_workflow_steps(current_step: int):
    """Render the workflow progress bar with glassmorphic step pills."""
    steps = ["Configure", "Analyze", "Prioritize", "Approve", "PRD", "Sprint", "Done"]
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < current_step:
                bg = "rgba(16, 185, 129, 0.18)"
                border = "rgba(16, 185, 129, 0.45)"
                text_color = "#34d399"
                icon = "✓"
            elif i == current_step:
                bg = "rgba(56, 189, 248, 0.2)"
                border = "rgba(56, 189, 248, 0.6)"
                text_color = "#38bdf8"
                icon = str(i + 1)
            else:
                bg = "rgba(15, 23, 42, 0.6)"
                border = "rgba(255, 255, 255, 0.08)"
                text_color = "#94a3b8"
                icon = str(i + 1)
            st.markdown(f"""
            <div style="text-align:center; background:{bg}; border:1px solid {border};
                        border-radius:12px; padding:10px 4px; backdrop-filter:blur(10px);
                        transition:all 0.3s ease; box-shadow:0 4px 12px rgba(0,0,0,0.3);">
                <div style="font-size:0.95rem; font-weight:800; color:{text_color}; margin-bottom:2px;">
                    {icon}
                </div>
                <div style="font-size:0.75rem; font-weight:600; color:{text_color};">
                    {step}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─── Agent Status Cards ───────────────────────────────────────────────────────

def render_agent_status_card(agent_name: str, status: str, message: str = ""):
    """Render a single agent status card."""
    icon = AGENT_ICONS.get(agent_name, "🤖")
    status_icon = STATUS_ICONS.get(status, "⏳")
    display_name = agent_name.replace("_", " ").title()

    bg_colors = {
        "success": "rgba(16,185,129,0.08)",
        "running": "rgba(59,130,246,0.08)",
        "error": "rgba(239,68,68,0.08)",
        "pending": "rgba(100,116,139,0.05)",
    }
    border_colors = {
        "success": "#10b981",
        "running": "#3b82f6",
        "error": "#ef4444",
        "pending": "#374151",
    }

    bg = bg_colors.get(status, "rgba(100,116,139,0.05)")
    border = border_colors.get(status, "#374151")

    st.markdown(f"""
    <div style="background:{bg}; border:1px solid {border}; border-left:3px solid {border};
                border-radius:10px; padding:12px 16px; margin:6px 0;
                {'animation:pulse 1.5s infinite;' if status == 'running' else ''}">
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:1.3rem;">{icon}</span>
            <div>
                <div style="font-weight:600; color:#f1f5f9; font-size:0.9rem;">
                    {status_icon} {display_name}
                </div>
                {f'<div style="color:#94a3b8; font-size:0.78rem; margin-top:2px;">{message}</div>' if message else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_all_agent_statuses(agent_statuses: Dict[str, Any]):
    """Render status cards for all agents."""
    agent_order = [
        "feedback_agent", "competitor_agent", "analytics_agent",
        "prioritization_agent", "human_approval",
        "prd_agent", "sprint_agent"
    ]
    for agent in agent_order:
        if agent in agent_statuses:
            status_obj = agent_statuses[agent]
            if isinstance(status_obj, dict):
                status = status_obj.get("status", "pending")
                msg = status_obj.get("error_message", "")
            else:
                status = getattr(status_obj, "status", "pending")
                msg = getattr(status_obj, "error_message", "") or ""
            render_agent_status_card(agent, status, msg)
        else:
            render_agent_status_card(agent, "pending")


# ─── Priority Table ───────────────────────────────────────────────────────────

def render_priority_table(features: List[Dict]) -> Optional[List[Dict]]:
    """
    Render the feature priority table with approve/reject controls.
    Returns the list of approved features.
    """
    if not features:
        st.warning("No features to display.")
        return None

    st.markdown("### 📋 Feature Priority Ranking")

    df_data = []
    for f in features:
        df_data.append({
            "Feature": f.get("feature", ""),
            "Priority": f.get("priority", ""),
            "Score": f.get("priority_score", 0),
            "Customer": f.get("customer_impact", 0),
            "Business": f.get("business_value", 0),
            "Strategic": f.get("strategic_alignment", 0),
            "Urgency": f.get("urgency", 0),
            "Feasibility": f.get("feasibility", 0),
            "Effort": f.get("estimated_effort", "TBD"),
            "Reason": f.get("reason", ""),
        })

    df = pd.DataFrame(df_data)

    # Style the priority column
    def color_priority(val):
        colors = {"P0": "color: #ef4444; font-weight: 700",
                  "P1": "color: #f97316; font-weight: 700",
                  "P2": "color: #eab308; font-weight: 700",
                  "P3": "color: #6b7280;"}
        return colors.get(val, "")

    st.dataframe(
        df[["Feature", "Priority", "Score", "Customer", "Business", "Strategic", "Urgency", "Feasibility", "Effort"]],
        use_container_width=True,
        height=min(400, 60 + len(features) * 36),
    )

    return features


def render_feature_approval(features: List[Dict]) -> List[Dict]:
    """
    Render individual feature approval cards with checkboxes.
    Returns list of approved features.
    """
    st.markdown("### ✅ Review & Approve Features")
    st.markdown(
        '<p style="color:#94a3b8; font-size:0.9rem;">Select features to approve for PRD generation and sprint planning. '
        'P0 (Critical), P1 (High), and P2 (Medium) are pre-selected for your convenience.</p>',
        unsafe_allow_html=True
    )

    if not features:
        st.warning("⚠️ **No features available to approve.** The prioritization agent returned an empty list. "
                   "Please go back and re-run the analysis with valid feedback/analytics data.")
        return []

    col_sel1, col_sel2, col_sel3 = st.columns([1, 1, 3])
    with col_sel1:
        if st.button("📋 Select All", use_container_width=True, key="select_all_btn"):
            for feat in features:
                k = f"approve_{feat.get('feature','').replace(' ', '_')}"
                st.session_state[k] = True
            st.rerun()
    with col_sel2:
        if st.button("🧹 Clear All", use_container_width=True, key="clear_all_btn"):
            for feat in features:
                k = f"approve_{feat.get('feature','').replace(' ', '_')}"
                st.session_state[k] = False
            st.rerun()

    approved = []
    for feat in features:
        priority = feat.get("priority", "P2")
        color = PRIORITY_COLORS.get(priority, "#6b7280")
        score = feat.get("priority_score", 0)

        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div style="background:rgba(26,34,53,0.8); border:1px solid #1e293b;
                            border-left:3px solid {color}; border-radius:10px;
                            padding:14px 16px; margin:6px 0;">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                        <span style="background:rgba({','.join(str(int(color.lstrip('#')[i:i+2], 16)) for i in (0,2,4))},0.15);
                                     color:{color}; border:1px solid {color}40;
                                     padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:700;">
                            {priority}
                        </span>
                        <span style="color:#f1f5f9; font-weight:600;">{feat.get('feature','')}</span>
                        <span style="color:#94a3b8; font-size:0.8rem;">Score: {score:.1f}/10</span>
                    </div>
                    <p style="color:#94a3b8; font-size:0.82rem; margin:0;">{feat.get('reason','')[:150]}</p>
                    <p style="color:#64748b; font-size:0.78rem; margin:4px 0 0 0;">
                        Effort: {feat.get('estimated_effort','TBD')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                default = priority in ("P0", "P1", "P2")
                approved_check = st.checkbox(
                    "Approve",
                    value=default,
                    key=f"approve_{feat.get('feature','').replace(' ', '_')}",
                )
                if approved_check:
                    approved.append(feat)

    return approved


# ─── PRD Display ──────────────────────────────────────────────────────────────

def render_prd(prd: Dict):
    """Render a PRD document in a nicely formatted view."""
    feature_name = prd.get("feature_name", "Feature")
    priority = prd.get("priority", "P1")
    color = PRIORITY_COLORS.get(priority, "#6b7280")

    st.markdown(f"""
    <div style="background:rgba(26,34,53,0.9); border:1px solid #1e293b;
                border-radius:14px; padding:24px; margin-bottom:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
            <span style="font-size:1.5rem;">📝</span>
            <h2 style="color:#f1f5f9; margin:0; font-size:1.3rem; font-weight:700;">
                PRD: {feature_name}
            </h2>
            <span style="background:rgba(255,255,255,0.05); color:{color};
                         border:1px solid {color}40; padding:3px 12px;
                         border-radius:20px; font-size:0.8rem; font-weight:700;">
                {priority}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📋 Overview", "👤 Users & Stories", "⚙️ Requirements", "📊 Metrics & Risks"])

    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Problem Statement**")
            st.info(prd.get("problem_statement", "N/A"))
            st.markdown("**Background**")
            st.write(prd.get("background", "N/A"))
        with col2:
            st.markdown("**Goals**")
            for g in prd.get("goals", []):
                st.markdown(f"✅ {g}")
            st.markdown("**Non-Goals**")
            for ng in prd.get("non_goals", []):
                st.markdown(f"🚫 {ng}")

    with tabs[1]:
        st.markdown("**User Personas**")
        for persona in prd.get("user_personas", []):
            st.markdown(f"👤 {persona}")
        st.markdown("---")
        st.markdown("**User Stories**")
        for i, story in enumerate(prd.get("user_stories", []), 1):
            with st.expander(f"Story {i}: As a **{story.get('persona','')}**", expanded=i == 1):
                st.markdown(f"**Action:** {story.get('action','')}")
                st.markdown(f"**Benefit:** {story.get('benefit','')}")
                st.markdown("**Acceptance Criteria:**")
                for ac in story.get("acceptance_criteria", []):
                    st.markdown(f"- {ac}")

    with tabs[2]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Functional Requirements**")
            for req in prd.get("functional_requirements", []):
                st.markdown(f"- {req}")
        with col2:
            st.markdown("**Non-Functional Requirements**")
            for req in prd.get("non_functional_requirements", []):
                st.markdown(f"- {req}")
        st.markdown("---")
        st.markdown("**Technical Considerations**")
        st.write(prd.get("technical_considerations", "N/A"))
        st.markdown("**Dependencies**")
        for dep in prd.get("dependencies", []):
            st.markdown(f"🔗 {dep}")

    with tabs[3]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Success Metrics**")
            for m in prd.get("success_metrics", []):
                st.markdown(f"📈 {m}")
            st.markdown("**Acceptance Criteria**")
            for ac in prd.get("acceptance_criteria", []):
                st.markdown(f"✓ {ac}")
        with col2:
            st.markdown("**Risks**")
            for risk in prd.get("risks", []):
                st.markdown(f"⚠️ {risk}")
            st.markdown(f"**Timeline:** {prd.get('timeline_estimate', 'TBD')}")


# ─── Sprint Board ─────────────────────────────────────────────────────────────

def render_sprint_board(sprint: Dict):
    """Render a visual sprint board."""
    sprint_name = sprint.get("sprint_name", "Sprint")
    used_cap = sprint.get("used_capacity", 0)
    total_cap = sprint.get("total_capacity", 40)
    pct = min(100, int(used_cap / total_cap * 100)) if total_cap else 0

    # Header metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sprint", sprint_name)
    with col2:
        st.metric("Duration", f"{sprint.get('duration_weeks', 2)} weeks")
    with col3:
        st.metric("Story Points", f"{used_cap} / {total_cap}")
    with col4:
        task_count = len(sprint.get("tasks", []))
        st.metric("Tasks", task_count)

    # Capacity bar
    st.markdown(f"""
    <div style="margin: 16px 0;">
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
            <span style="color:#94a3b8; font-size:0.85rem;">Capacity Used</span>
            <span style="color:#f1f5f9; font-size:0.85rem; font-weight:600;">{pct}%</span>
        </div>
        <div style="background:#1e293b; border-radius:8px; height:10px; overflow:hidden;">
            <div style="background:{'#10b981' if pct < 80 else '#f59e0b' if pct < 95 else '#ef4444'};
                        width:{pct}%; height:100%; border-radius:8px;
                        transition:width 1s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sprint goal
    if sprint.get("sprint_goal"):
        st.info(f"**Sprint Goal:** {sprint['sprint_goal']}")

    # Task breakdown by team
    tasks = sprint.get("tasks", [])
    teams = {}
    for task in tasks:
        team = task.get("team", "Full-Stack")
        teams.setdefault(team, []).append(task)

    team_colors = {
        "Backend": "#3b82f6",
        "Frontend": "#8b5cf6",
        "Design": "#ec4899",
        "QA": "#10b981",
        "DevOps": "#f97316",
        "Full-Stack": "#06b6d4",
    }

    priority_icons = {"Must Have": "🔴", "Should Have": "🟡", "Nice to Have": "🟢"}

    st.markdown("### 📋 Task Board")
    team_cols = st.columns(min(len(teams), 3))
    for col_idx, (team_name, team_tasks) in enumerate(teams.items()):
        with team_cols[col_idx % len(team_cols)]:
            color = team_colors.get(team_name, "#64748b")
            total_sp = sum(t.get("story_points", 0) for t in team_tasks)
            st.markdown(f"""
            <div style="border-top:3px solid {color}; background:rgba(26,34,53,0.8);
                        border-radius:10px; padding:12px; margin-bottom:16px;">
                <div style="color:{color}; font-weight:700; margin-bottom:8px;">
                    {team_name} Team ({total_sp} SP)
                </div>
            """, unsafe_allow_html=True)

            for task in team_tasks:
                p_icon = priority_icons.get(task.get("priority", "Should Have"), "🟡")
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.03); border:1px solid #1e293b;
                            border-radius:8px; padding:8px 10px; margin:4px 0;">
                    <div style="color:#f1f5f9; font-size:0.85rem; font-weight:500;">
                        {p_icon} {task.get('task','')}
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top:4px;">
                        <span style="color:#64748b; font-size:0.75rem;">
                            {task.get('description','')[:50]}...
                        </span>
                        <span style="background:rgba(59,130,246,0.1); color:#3b82f6;
                                     padding:1px 8px; border-radius:10px; font-size:0.75rem;
                                     font-weight:600; white-space:nowrap;">
                            {task.get('story_points',0)} SP
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


# ─── Charts ───────────────────────────────────────────────────────────────────

def render_priority_chart(features: List[Dict]):
    """Render a horizontal bar chart of feature priority scores."""
    if not features:
        return

    sorted_features = sorted(features, key=lambda x: x.get("priority_score", 0))
    names = [f.get("feature", "")[:30] for f in sorted_features]
    scores = [f.get("priority_score", 0) for f in sorted_features]
    priorities = [f.get("priority", "P3") for f in sorted_features]
    colors_list = [PRIORITY_COLORS.get(p, "#6b7280") for p in priorities]

    fig = go.Figure(go.Bar(
        x=scores,
        y=names,
        orientation='h',
        marker_color=colors_list,
        text=[f"{s:.1f}" for s in scores],
        textposition='outside',
        textfont=dict(color='white', size=11),
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', family='Inter'),
        xaxis=dict(
            showgrid=True, gridcolor='rgba(255,255,255,0.05)',
            color='#64748b', range=[0, 11],
            title="Priority Score"
        ),
        yaxis=dict(color='#94a3b8'),
        height=max(300, len(features) * 40 + 80),
        margin=dict(l=0, r=60, t=20, b=20),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_sentiment_gauge(sentiment: str, score: float):
    """Render a sentiment gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': sentiment, 'font': {'color': '#94a3b8', 'size': 14}},
        number={'font': {'color': '#f1f5f9', 'size': 24}},
        gauge={
            'axis': {'range': [0, 10], 'tickcolor': '#64748b'},
            'bar': {'color': '#3b82f6'},
            'bgcolor': '#1e293b',
            'steps': [
                {'range': [0, 3.5], 'color': 'rgba(239,68,68,0.2)'},
                {'range': [3.5, 6.5], 'color': 'rgba(234,179,8,0.2)'},
                {'range': [6.5, 10], 'color': 'rgba(16,185,129,0.2)'},
            ],
            'threshold': {'line': {'color': '#3b82f6', 'width': 3}, 'value': score},
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#94a3b8'),
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_spider_chart(feature: Dict):
    """Render a radar/spider chart for feature scores."""
    categories = ['Customer Impact', 'Business Value', 'Strategic Alignment', 'Urgency', 'Feasibility']
    values = [
        feature.get('customer_impact', 0),
        feature.get('business_value', 0),
        feature.get('strategic_alignment', 0),
        feature.get('urgency', 0),
        feature.get('feasibility', 0),
    ]
    values.append(values[0])  # Close the polygon
    categories.append(categories[0])

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(59,130,246,0.15)',
        line=dict(color='#3b82f6', width=2),
        name=feature.get('feature', ''),
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0, 10], color='#64748b',
                            gridcolor='rgba(255,255,255,0.05)'),
            angularaxis=dict(color='#94a3b8', gridcolor='rgba(255,255,255,0.08)'),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', family='Inter', size=11),
        showlegend=False,
        height=280,
        margin=dict(l=40, r=40, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_analytics_chart(feature_metrics: List[Dict]):
    """Render a bubble chart of feature analytics."""
    if not feature_metrics:
        return

    features = [m.get("feature", "") for m in feature_metrics]
    usage = [m.get("usage_percent", 0) or 0 for m in feature_metrics]
    error_rates = [m.get("error_rate", 0) or 0 for m in feature_metrics]
    trend_colors = {
        "Increasing": "#10b981",
        "Stable": "#3b82f6",
        "Decreasing": "#ef4444",
    }
    colors_list = [trend_colors.get(m.get("trend", "Stable"), "#3b82f6") for m in feature_metrics]

    fig = go.Figure()
    for i, (feat, u, e, c) in enumerate(zip(features, usage, error_rates, colors_list)):
        fig.add_trace(go.Scatter(
            x=[u], y=[e],
            mode='markers+text',
            marker=dict(size=20, color=c, opacity=0.8),
            text=[feat[:15]],
            textposition='top center',
            textfont=dict(color='#94a3b8', size=10),
            name=feat,
            showlegend=False,
        ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', family='Inter'),
        xaxis=dict(title="Usage %", gridcolor='rgba(255,255,255,0.05)', color='#64748b'),
        yaxis=dict(title="Error Rate %", gridcolor='rgba(255,255,255,0.05)', color='#64748b'),
        height=320,
        margin=dict(l=40, r=20, t=20, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─── Feedback Summary Cards ───────────────────────────────────────────────────

def render_feedback_issues(issues: List[Dict]):
    """Render feedback issue cards."""
    impact_colors = {
        "Critical": "#ef4444",
        "High": "#f97316",
        "Medium": "#eab308",
        "Low": "#10b981",
    }
    for issue in issues[:8]:
        color = impact_colors.get(issue.get("impact", "Medium"), "#94a3b8")
        st.markdown(f"""
        <div style="background:rgba(26,34,53,0.8); border:1px solid #1e293b;
                    border-left:3px solid {color}; border-radius:10px;
                    padding:12px 16px; margin:6px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#f1f5f9; font-weight:600; font-size:0.9rem;">
                    {issue.get('issue', '')}
                </span>
                <div style="display:flex; gap:8px; align-items:center;">
                    <span style="color:{color}; font-size:0.75rem; font-weight:700;">
                        {issue.get('impact', '')}
                    </span>
                    <span style="background:rgba(255,255,255,0.06); color:#94a3b8;
                                 padding:2px 8px; border-radius:10px; font-size:0.75rem;">
                        {issue.get('frequency', 0)} mentions
                    </span>
                </div>
            </div>
            <div style="color:#64748b; font-size:0.78rem; margin-top:4px;">
                {issue.get('category', '')} • {issue.get('sentiment', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_success_banner(message: str):
    """Render a success notification banner."""
    st.markdown(f"""
    <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3);
                border-radius:12px; padding:16px 20px; margin:16px 0; text-align:center;">
        <span style="font-size:1.5rem;">✅</span>
        <span style="color:#10b981; font-weight:600; font-size:1rem; margin-left:10px;">
            {message}
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_error_banner(message: str):
    """Render an error notification banner."""
    st.markdown(f"""
    <div style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3);
                border-radius:12px; padding:16px 20px; margin:16px 0;">
        <span style="font-size:1.2rem;">❌</span>
        <span style="color:#ef4444; font-weight:500; font-size:0.9rem; margin-left:10px;">
            {message}
        </span>
    </div>
    """, unsafe_allow_html=True)
