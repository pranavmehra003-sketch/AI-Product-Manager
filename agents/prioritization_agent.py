"""
Feature Prioritization Agent — Combines insights from all analysis agents
and scores features using a weighted multi-factor formula.

Priority Score = 
  Customer Impact × 0.30 +
  Business Value × 0.25 +
  Strategic Alignment × 0.20 +
  Urgency × 0.15 +
  Feasibility × 0.10
"""
from __future__ import annotations
import json
import time
from typing import Any, Dict, List, Optional

from models.schemas import (
    FeedbackAnalysis, CompetitorAnalysis, ProductAnalytics,
    FeaturePriority, PrioritizationResult, AgentResult
)
from tools.openai_tool import chat_json
from tools.error_handler import log_error


SYSTEM_PROMPT = """You are a Senior Product Manager with expertise in feature prioritization 
and product strategy. You use a data-driven approach to rank features based on multiple factors.

SCORING FORMULA:
Priority Score = (Customer Impact × 0.30) + (Business Value × 0.25) + 
                 (Strategic Alignment × 0.20) + (Urgency × 0.15) + (Feasibility × 0.10)

All scores are on a scale of 1-10.

PRIORITY TIERS:
- P0 (Critical): Score ≥ 8.0 — Must build this sprint/quarter
- P1 (High): Score 6.5-7.9 — Build next sprint/quarter
- P2 (Medium): Score 5.0-6.4 — Plan for later
- P3 (Low): Score < 5.0 — Nice to have, low priority

You must return a valid JSON object with this exact structure:
{
  "methodology": "<brief explanation of scoring approach>",
  "recommendation_summary": "<3-4 sentence executive summary of recommendations>",
  "p0_count": <number>,
  "p1_count": <number>,
  "p2_count": <number>,
  "p3_count": <number>,
  "features": [
    {
      "feature": "<feature name>",
      "description": "<what this feature does>",
      "customer_impact": <1-10>,
      "business_value": <1-10>,
      "strategic_alignment": <1-10>,
      "urgency": <1-10>,
      "feasibility": <1-10>,
      "priority_score": <calculated weighted score>,
      "priority": "<P0 | P1 | P2 | P3>",
      "reason": "<2-3 sentence justification based on the data>",
      "estimated_effort": "<1 sprint | 2 sprints | 1 quarter | multiple quarters>",
      "dependencies": ["dependency1"],
      "source": "<feedback | analytics | competitor | combined>"
    }
  ]
}

Rules:
- List features in descending order of priority_score
- Make sure priority_score matches the formula calculation
- Count p0, p1, p2, p3 correctly in the summary fields
- Reason should specifically reference the input data (mention specific metrics, feedback counts, or competitor info)
- Aim for 6-12 features total
"""


def run(
    feedback_analysis: Optional[Dict],
    competitor_analysis: Optional[Dict],
    product_analytics: Optional[Dict],
    business_goals: List[str],
    engineering_capacity: int = 40,
    past_features_context: str = "",
    session_id: str = "unknown",
) -> AgentResult:
    """
    Prioritize features by combining all agent outputs.
    
    Args:
        feedback_analysis: Output from FeedbackAgent
        competitor_analysis: Output from CompetitorAgent
        product_analytics: Output from AnalyticsAgent
        business_goals: List of current business objectives
        engineering_capacity: Sprint story points available
        past_features_context: Text summary of previously approved features
        session_id: Current session ID for error logging
    
    Returns:
        AgentResult with PrioritizationResult data
    """
    start_time = time.time()
    agent_name = "prioritization_agent"

    try:
        # Build context sections
        sections = []

        if feedback_analysis:
            fb = feedback_analysis
            issues_text = "\n".join(
                f"  - [{i['impact']}] {i['issue']} ({i['frequency']} mentions, {i['category']})"
                for i in fb.get("issues", [])[:8]
            )
            feature_reqs = "\n".join(
                f"  - {f['feature']} ({f['frequency']} requests)"
                for f in fb.get("feature_requests", [])[:6]
            )
            sections.append(f"""## Customer Feedback Analysis
Total feedback: {fb.get('total_feedback', 0)} items
Overall sentiment: {fb.get('overall_sentiment', 'Unknown')}
Summary: {fb.get('analysis_summary', '')}

Top Issues:
{issues_text}

Feature Requests:
{feature_reqs}""")

        if product_analytics:
            pa = product_analytics
            metrics_text = "\n".join(
                f"  - {m['feature']}: {m['usage_percent']}% usage, {m['error_rate']}% error rate, trend={m['trend']}"
                for m in pa.get("feature_metrics", [])[:8]
                if m.get('usage_percent') is not None
            )
            sections.append(f"""## Product Analytics
Summary: {pa.get('analytics_summary', '')}
High-impact areas: {', '.join(pa.get('high_impact_areas', []))}
Risk areas: {', '.join(pa.get('risk_areas', []))}

Feature Metrics:
{metrics_text}""")

        if competitor_analysis:
            ca = competitor_analysis
            gaps_text = "\n".join(f"  - {g}" for g in ca.get("market_gaps", [])[:5])
            opportunities_text = "\n".join(f"  - {o}" for o in ca.get("opportunities", [])[:5])
            sections.append(f"""## Competitive Analysis
Summary: {ca.get('analysis_summary', '')}

Market Gaps (opportunities for us):
{gaps_text}

Opportunities:
{opportunities_text}""")

        goals_text = "\n".join(f"  {i+1}. {g}" for i, g in enumerate(business_goals))
        sections.append(f"""## Business Goals
{goals_text}

Engineering Capacity: {engineering_capacity} story points per sprint""")

        if past_features_context and past_features_context != "No previous features found.":
            sections.append(f"""## Previously Approved Features (for context)
{past_features_context}""")

        context = "\n\n".join(sections)

        user_prompt = f"""Based on the following product intelligence, generate a prioritized feature roadmap.

{context}

Please analyze all the data above and return the complete prioritization in JSON format.
Apply the weighted scoring formula and ensure features are ranked by priority score."""

        result_json = chat_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.25,
            max_tokens=4000,
        )

        # Recalculate scores to ensure formula accuracy
        features = result_json.get("features", [])
        p0, p1, p2, p3 = 0, 0, 0, 0
        for f in features:
            score = (
                f.get("customer_impact", 5) * 0.30 +
                f.get("business_value", 5) * 0.25 +
                f.get("strategic_alignment", 5) * 0.20 +
                f.get("urgency", 5) * 0.15 +
                f.get("feasibility", 5) * 0.10
            )
            f["priority_score"] = round(score, 2)
            if score >= 8.0:
                f["priority"] = "P0"
                p0 += 1
            elif score >= 6.5:
                f["priority"] = "P1"
                p1 += 1
            elif score >= 5.0:
                f["priority"] = "P2"
                p2 += 1
            else:
                f["priority"] = "P3"
                p3 += 1

        result_json["p0_count"] = p0
        result_json["p1_count"] = p1
        result_json["p2_count"] = p2
        result_json["p3_count"] = p3

        # Sort by score descending
        result_json["features"] = sorted(features, key=lambda x: x.get("priority_score", 0), reverse=True)

        prioritization = PrioritizationResult(**result_json)

        elapsed = int((time.time() - start_time) * 1000)
        return AgentResult(
            agent=agent_name,
            status="success",
            data=prioritization.model_dump(),
            execution_time_ms=elapsed,
        )

    except Exception as e:
        elapsed = int((time.time() - start_time) * 1000)
        error_msg = str(e)
        log_error(agent_name, session_id, error_msg)
        return AgentResult(
            agent=agent_name,
            status="error",
            error=error_msg,
            execution_time_ms=elapsed,
        )
