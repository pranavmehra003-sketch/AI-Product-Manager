"""
Feedback Analysis Agent — Analyzes customer feedback to identify issues,
feature requests, sentiment, and themes.
"""
from __future__ import annotations
import json
import time
from typing import List, Optional

from models.schemas import FeedbackAnalysis, FeedbackIssue, FeatureRequest, AgentResult
from tools.openai_tool import chat_json
from tools.error_handler import log_error


SYSTEM_PROMPT = """You are an expert Product Manager and UX Researcher specializing in 
customer feedback analysis. Your task is to analyze raw customer feedback and extract 
structured insights.

You must return a valid JSON object with this exact structure:
{
  "total_feedback": <number>,
  "overall_sentiment": "<Mostly Negative | Mixed | Mostly Positive>",
  "top_themes": ["theme1", "theme2", "theme3"],
  "analysis_summary": "<2-3 sentence executive summary>",
  "issues": [
    {
      "category": "<Performance | UI/UX | Reliability | Features | Support | Billing | Other>",
      "issue": "<concise issue title>",
      "frequency": <estimated number of mentions>,
      "impact": "<Critical | High | Medium | Low>",
      "sentiment": "<Negative | Neutral | Positive>",
      "sample_quotes": ["quote1", "quote2"]
    }
  ],
  "feature_requests": [
    {
      "feature": "<feature name>",
      "frequency": <estimated mentions>,
      "impact": "<High | Medium | Low>",
      "customer_segment": "<power users | new users | enterprise | all>"
    }
  ]
}

Rules:
- Cluster similar issues together (don't list duplicates)
- Rank issues by frequency (highest first)
- Extract up to 10 issues and 8 feature requests
- Be specific and actionable in issue descriptions
- Frequency should be your best estimate based on the patterns in feedback
"""


def run(
    feedback_list: List[str],
    product_name: str = "our product",
    session_id: str = "unknown",
) -> AgentResult:
    """
    Analyze customer feedback and return structured insights.
    
    Args:
        feedback_list: List of raw feedback strings
        product_name: Name of the product being analyzed
        session_id: Current session ID for error logging
    
    Returns:
        AgentResult with FeedbackAnalysis data
    """
    start_time = time.time()
    agent_name = "feedback_agent"

    try:
        if not feedback_list:
            raise ValueError("No feedback provided for analysis.")

        # Limit to 200 items to avoid token limits; summarize the rest
        sample = feedback_list[:200]
        total = len(feedback_list)

        user_prompt = f"""Product: {product_name}
Total feedback items received: {total}
Analyzing a sample of {len(sample)} items:

--- CUSTOMER FEEDBACK ---
{chr(10).join(f'{i+1}. {fb}' for i, fb in enumerate(sample))}
--- END FEEDBACK ---

Please analyze this feedback and return the structured JSON response.
Extrapolate frequency estimates to the full {total} item dataset."""

        result_json = chat_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=3000,
        )

        # Ensure total_feedback reflects the actual count
        result_json["total_feedback"] = total

        # Parse into Pydantic model for validation
        analysis = FeedbackAnalysis(**result_json)

        elapsed = int((time.time() - start_time) * 1000)
        return AgentResult(
            agent=agent_name,
            status="success",
            data=analysis.model_dump(),
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
