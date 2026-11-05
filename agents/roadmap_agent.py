"""
Roadmap Agent — Generates a quarterly product roadmap from prioritized features.
Organizes features into Now / Next / Later themes with business impact estimates.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List

from models.schemas import AgentResult
from tools.openai_tool import chat_json
from tools.error_handler import log_error


SYSTEM_PROMPT = """You are a Senior Product Strategist specializing in product roadmap planning.
Given a prioritized feature list, you organize features into a Now / Next / Later roadmap.

You must return a valid JSON object with this exact structure:
{
  "product_name": "<product name>",
  "roadmap_period": "<e.g., Q1-Q2 2025>",
  "roadmap_summary": "<2-3 sentence executive summary>",
  "now": {
    "theme": "<single unifying theme for Now>",
    "objective": "<what this quarter achieves>",
    "features": ["feature1", "feature2"],
    "expected_impact": "<business impact>",
    "kpis": ["KPI 1", "KPI 2"]
  },
  "next": {
    "theme": "<unifying theme for Next>",
    "objective": "<what next quarter achieves>",
    "features": ["feature3", "feature4"],
    "expected_impact": "<business impact>",
    "kpis": ["KPI 1", "KPI 2"]
  },
  "later": {
    "theme": "<future theme>",
    "objective": "<longer-term goals>",
    "features": ["feature5", "feature6"],
    "expected_impact": "<strategic impact>",
    "kpis": ["KPI 1"]
  },
  "risks": ["risk1", "risk2"],
  "dependencies": ["dep1", "dep2"]
}

Rules:
- Now = P0 and high-impact P1 features (current sprint/quarter)
- Next = remaining P1 and P2 features (next quarter)
- Later = P2 and P3 features (future planning)
- Each theme should have a memorable, motivating name (e.g., "Reliability First", "Growth Engine")
- KPIs must be measurable
"""


def run(
    prioritization_result: Dict[str, Any],
    product_name: str = "our product",
    business_goals: List[str] = None,
    session_id: str = "unknown",
) -> AgentResult:
    """
    Generate a quarterly roadmap from prioritized features.

    Args:
        prioritization_result: Output from the PrioritizationAgent
        product_name: Name of the product
        business_goals: List of business objectives
        session_id: Session ID for error logging

    Returns:
        AgentResult with roadmap dict
    """
    start_time = time.time()
    agent_name = "roadmap_agent"

    try:
        features = prioritization_result.get("features", [])
        if not features:
            raise ValueError("No prioritized features provided for roadmap generation.")

        goals_text = "\n".join(f"  {i+1}. {g}" for i, g in enumerate(business_goals or []))
        features_text = "\n".join(
            f"  - [{f.get('priority', 'P2')} | Score: {f.get('priority_score', 0):.1f}] "
            f"{f.get('feature', '')} — {f.get('reason', '')[:100]}"
            for f in features
        )

        user_prompt = f"""Create a Now / Next / Later product roadmap for {product_name}.

Business Goals:
{goals_text or '  - Improve product quality and user satisfaction'}

Prioritized Features:
{features_text}

Prioritization Summary: {prioritization_result.get('recommendation_summary', '')}

Please generate a strategic quarterly roadmap that organizes these features into Now / Next / Later buckets.
Return the complete roadmap as JSON."""

        result_json = chat_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=3000,
        )

        result_json["product_name"] = product_name

        elapsed = int((time.time() - start_time) * 1000)
        return AgentResult(
            agent=agent_name,
            status="success",
            data=result_json,
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
