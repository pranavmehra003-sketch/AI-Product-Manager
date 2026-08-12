"""
Product Analytics Agent — Analyzes product usage metrics to identify
trends, risks, and opportunities.
"""
from __future__ import annotations
import json
import time
from typing import Any, Dict, Optional

from models.schemas import ProductAnalytics, AgentResult
from tools.openai_tool import chat_json
from tools.error_handler import log_error


SYSTEM_PROMPT = """You are an expert Product Analyst specializing in data-driven product decisions.
Your task is to analyze product usage metrics and extract actionable insights.

You must return a valid JSON object with this exact structure:
{
  "product_name": "<product name>",
  "period": "<time period of data>",
  "overall_dau": <number or null>,
  "overall_mau": <number or null>,
  "overall_retention": <percentage or null>,
  "analytics_summary": "<2-3 sentence executive summary>",
  "high_impact_areas": ["area1", "area2"],
  "risk_areas": ["risk1", "risk2"],
  "feature_metrics": [
    {
      "feature": "<feature name>",
      "dau": <number or null>,
      "mau": <number or null>,
      "usage_percent": <percentage or null>,
      "retention_impact": "<High | Medium | Low>",
      "conversion_rate": <percentage or null>,
      "churn_correlation": <0.0-1.0 or null>,
      "error_rate": <percentage or null>,
      "avg_session_duration": <seconds or null>,
      "trend": "<Increasing | Stable | Decreasing>"
    }
  ]
}

Rules:
- Identify features with high usage but also high error rates (reliability risks)
- Flag features with decreasing trends as potential churn risks
- Highlight features with high retention impact as strategic assets
- Use null for metrics not available in the input data
- Focus on actionable business insights, not raw statistics
"""


def run(
    analytics_data: Dict[str, Any],
    product_name: str = "our product",
    session_id: str = "unknown",
) -> AgentResult:
    """
    Analyze product metrics and return structured analytics insights.
    
    Args:
        analytics_data: Raw analytics data dict from uploaded JSON
        product_name: Name of the product
        session_id: Current session ID for error logging
    
    Returns:
        AgentResult with ProductAnalytics data
    """
    start_time = time.time()
    agent_name = "analytics_agent"

    try:
        if not analytics_data:
            raise ValueError("No analytics data provided for analysis.")

        analytics_json_str = json.dumps(analytics_data, indent=2)

        user_prompt = f"""Product: {product_name}

--- PRODUCT ANALYTICS DATA ---
{analytics_json_str[:5000]}
--- END ANALYTICS DATA ---

Analyze this product metrics data and return the structured JSON response.
Identify key trends, risks, and opportunities for the product roadmap."""

        result_json = chat_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=3000,
        )

        result_json["product_name"] = product_name

        # Parse and validate
        analytics = ProductAnalytics(**result_json)

        elapsed = int((time.time() - start_time) * 1000)
        return AgentResult(
            agent=agent_name,
            status="success",
            data=analytics.model_dump(),
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
