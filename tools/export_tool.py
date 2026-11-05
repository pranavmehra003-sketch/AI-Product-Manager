"""
Export Tool — Converts agent outputs to Markdown, CSV, and JSON formats
for download and sharing.
"""
from __future__ import annotations
import csv
import io
import json
from typing import Any, Dict, List, Optional


# ─── PRD Markdown Export ──────────────────────────────────────────────────────

def prd_to_markdown(prd: Dict[str, Any]) -> str:
    """Convert a PRDDocument dict to a Markdown string."""
    lines = []
    feature_name = prd.get("feature_name", "Feature")
    priority = prd.get("priority", "P1")
    version = prd.get("version", "1.0")
    author = prd.get("author", "AI Product Manager")
    created_at = prd.get("created_at", "")[:10]

    lines.append(f"# PRD: {feature_name}")
    lines.append(f"")
    lines.append(f"| Field | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| **Version** | {version} |")
    lines.append(f"| **Priority** | {priority} |")
    lines.append(f"| **Author** | {author} |")
    lines.append(f"| **Created** | {created_at} |")
    lines.append(f"| **Timeline** | {prd.get('timeline_estimate', 'TBD')} |")
    lines.append("")

    lines.append("## Problem Statement")
    lines.append(prd.get("problem_statement", "N/A"))
    lines.append("")

    lines.append("## Background")
    lines.append(prd.get("background", "N/A"))
    lines.append("")

    if prd.get("user_personas"):
        lines.append("## User Personas")
        for p in prd["user_personas"]:
            lines.append(f"- {p}")
        lines.append("")

    if prd.get("goals"):
        lines.append("## Goals")
        for g in prd["goals"]:
            lines.append(f"- ✅ {g}")
        lines.append("")

    if prd.get("non_goals"):
        lines.append("## Non-Goals")
        for ng in prd["non_goals"]:
            lines.append(f"- 🚫 {ng}")
        lines.append("")

    if prd.get("user_stories"):
        lines.append("## User Stories")
        for i, story in enumerate(prd["user_stories"], 1):
            lines.append(f"### Story {i}: As a {story.get('persona', '')}")
            lines.append(f"**I want to** {story.get('action', '')}")
            lines.append(f"**So that** {story.get('benefit', '')}")
            lines.append("")
            if story.get("acceptance_criteria"):
                lines.append("**Acceptance Criteria:**")
                for ac in story["acceptance_criteria"]:
                    lines.append(f"- {ac}")
            lines.append("")

    if prd.get("functional_requirements"):
        lines.append("## Functional Requirements")
        for req in prd["functional_requirements"]:
            lines.append(f"- {req}")
        lines.append("")

    if prd.get("non_functional_requirements"):
        lines.append("## Non-Functional Requirements")
        for req in prd["non_functional_requirements"]:
            lines.append(f"- {req}")
        lines.append("")

    if prd.get("success_metrics"):
        lines.append("## Success Metrics")
        for m in prd["success_metrics"]:
            lines.append(f"- 📈 {m}")
        lines.append("")

    if prd.get("technical_considerations"):
        lines.append("## Technical Considerations")
        lines.append(prd["technical_considerations"])
        lines.append("")

    if prd.get("dependencies"):
        lines.append("## Dependencies")
        for dep in prd["dependencies"]:
            lines.append(f"- 🔗 {dep}")
        lines.append("")

    if prd.get("risks"):
        lines.append("## Risks & Mitigations")
        for risk in prd["risks"]:
            lines.append(f"- ⚠️ {risk}")
        lines.append("")

    if prd.get("acceptance_criteria"):
        lines.append("## Acceptance Criteria")
        for ac in prd["acceptance_criteria"]:
            lines.append(f"- ✓ {ac}")
        lines.append("")

    return "\n".join(lines)


# ─── Sprint Plan Markdown Export ──────────────────────────────────────────────

def sprint_to_markdown(sprint: Dict[str, Any]) -> str:
    """Convert a SprintPlan dict to a Markdown string."""
    lines = []
    sprint_name = sprint.get("sprint_name", "Sprint")
    used = sprint.get("used_capacity", 0)
    total = sprint.get("total_capacity", 40)
    pct = int(used / total * 100) if total else 0

    lines.append(f"# {sprint_name}")
    lines.append("")
    lines.append(f"**Sprint Goal:** {sprint.get('sprint_goal', 'N/A')}")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Duration | {sprint.get('duration_weeks', 2)} weeks |")
    lines.append(f"| Capacity | {used} / {total} SP ({pct}%) |")
    lines.append(f"| Total Tasks | {len(sprint.get('tasks', []))} |")
    lines.append(f"| Features Covered | {', '.join(sprint.get('features_covered', []))} |")
    lines.append("")

    if sprint.get("tasks"):
        lines.append("## Task Breakdown")
        lines.append("")
        lines.append("| # | Task | Team | SP | Priority | Assignee |")
        lines.append("|---|---|---|---|---|---|")
        for i, task in enumerate(sprint["tasks"], 1):
            lines.append(
                f"| {i} | {task.get('task', '')} | {task.get('team', '')} | "
                f"{task.get('story_points', 0)} | {task.get('priority', '')} | "
                f"{task.get('assignee', '')} |"
            )
        lines.append("")

    if sprint.get("definition_of_done"):
        lines.append("## Definition of Done")
        for dod in sprint["definition_of_done"]:
            lines.append(f"- ✓ {dod}")
        lines.append("")

    if sprint.get("risks"):
        lines.append("## Sprint Risks")
        for risk in sprint["risks"]:
            lines.append(f"- ⚠️ {risk}")
        lines.append("")

    return "\n".join(lines)


# ─── Feature Priority CSV Export ──────────────────────────────────────────────

def features_to_csv(features: List[Dict[str, Any]]) -> str:
    """Convert a list of FeaturePriority dicts to a CSV string."""
    output = io.StringIO()
    fieldnames = [
        "feature", "priority", "priority_score",
        "customer_impact", "business_value", "strategic_alignment",
        "urgency", "feasibility", "estimated_effort", "reason", "source",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for feat in features:
        writer.writerow(feat)
    return output.getvalue()


# ─── Competitor Analysis Markdown Export ──────────────────────────────────────

def competitor_to_markdown(analysis: Dict[str, Any]) -> str:
    """Convert a CompetitorAnalysis dict to a Markdown string."""
    lines = []
    lines.append(f"# Competitive Analysis: {analysis.get('product_name', 'Product')}")
    lines.append("")
    lines.append(f"## Executive Summary")
    lines.append(analysis.get("analysis_summary", "N/A"))
    lines.append("")

    if analysis.get("competitors"):
        lines.append("## Competitors")
        for comp in analysis["competitors"]:
            lines.append(f"### {comp.get('name', 'Unknown')}")
            lines.append(f"**Pricing:** {comp.get('pricing', 'Unknown')}")
            lines.append("")
            if comp.get("strengths"):
                lines.append("**Strengths:**")
                for s in comp["strengths"]:
                    lines.append(f"- ✅ {s}")
            if comp.get("weaknesses"):
                lines.append("**Weaknesses:**")
                for w in comp["weaknesses"]:
                    lines.append(f"- ❌ {w}")
            if comp.get("recent_launches"):
                lines.append("**Recent Launches:**")
                for r in comp["recent_launches"]:
                    lines.append(f"- 🚀 {r}")
            lines.append("")

    if analysis.get("market_gaps"):
        lines.append("## Market Gaps")
        for gap in analysis["market_gaps"]:
            lines.append(f"- 🎯 {gap}")
        lines.append("")

    if analysis.get("opportunities"):
        lines.append("## Opportunities")
        for opp in analysis["opportunities"]:
            lines.append(f"- 💡 {opp}")
        lines.append("")

    if analysis.get("threats"):
        lines.append("## Threats")
        for threat in analysis["threats"]:
            lines.append(f"- ⚠️ {threat}")
        lines.append("")

    return "\n".join(lines)
