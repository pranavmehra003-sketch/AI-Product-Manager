"""
Competitor Research Agent — Researches competitors using web search
and generates structured competitive analysis.
"""
from __future__ import annotations
import time
from typing import List, Optional

from models.schemas import CompetitorAnalysis, AgentResult
from tools.openai_tool import chat_json
from tools.search_tool import search_web, format_search_results
from tools.error_handler import log_error


SYSTEM_PROMPT = """You are an expert competitive intelligence analyst and Product Strategist.
Your task is to analyze web search results about competitors and produce structured insights.

You must return a valid JSON object with this exact structure:
{
  "product_name": "<product name>",
  "analysis_summary": "<2-3 sentence executive summary of competitive landscape>",
  "market_gaps": ["gap1", "gap2", "gap3"],
  "threats": ["threat1", "threat2"],
  "opportunities": ["opportunity1", "opportunity2"],
  "competitors": [
    {
      "name": "<competitor name>",
      "strengths": ["strength1", "strength2"],
      "weaknesses": ["weakness1", "weakness2"],
      "pricing": "<pricing model or tier>",
      "recent_launches": ["feature1", "feature2"]
    }
  ],
  "competitor_features": [
    {
      "competitor_name": "<name>",
      "feature": "<feature name>",
      "description": "<brief description>",
      "availability": true,
      "quality": "<Excellent | Good | Average | Poor>"
    }
  ]
}

Rules:
- Focus on features relevant to the target product
- Identify market gaps that the target product could exploit
- Be objective and evidence-based
- List up to 5 competitors and up to 15 competitor features
"""


def run(
    product_name: str,
    product_domain: str,
    competitors: Optional[List[str]] = None,
    session_id: str = "unknown",
) -> AgentResult:
    """
    Research competitors for a product and return structured analysis.
    
    Args:
        product_name: Name of our product
        product_domain: Domain/category (e.g., "project management software")
        competitors: Optional list of specific competitor names to research
        session_id: Current session ID for error logging
    
    Returns:
        AgentResult with CompetitorAnalysis data
    """
    start_time = time.time()
    agent_name = "competitor_agent"

    try:
        # Build search queries
        search_context = []

        # General market search
        general_results = search_web(f"best {product_domain} software alternatives 2024 features comparison", max_results=6)
        if general_results:
            search_context.append(f"## Market Overview\n{format_search_results(general_results)}")

        # Specific competitor research
        if competitors:
            for competitor in competitors[:3]:  # Limit to 3 specific competitors
                comp_results = search_web(f"{competitor} {product_domain} features pricing 2024", max_results=4)
                if comp_results:
                    search_context.append(f"## {competitor}\n{format_search_results(comp_results)}")
                time.sleep(0.5)

        # Recent trends
        trend_results = search_web(f"{product_domain} new features trends 2024", max_results=4)
        if trend_results:
            search_context.append(f"## Market Trends\n{format_search_results(trend_results)}")

        search_text = "\n\n".join(search_context) if search_context else "No search results available."

        # Build LLM prompt
        competitor_list_str = ", ".join(competitors) if competitors else "identify the main competitors"
        user_prompt = f"""Product Name: {product_name}
Product Domain: {product_domain}
Competitors to analyze: {competitor_list_str}

--- WEB SEARCH RESULTS ---
{search_text[:6000]}
--- END SEARCH RESULTS ---

Based on the search results above, generate a comprehensive competitive analysis. 
If the search results are limited, use your knowledge of the {product_domain} market 
to supplement with realistic competitive intelligence."""

        result_json = chat_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=3000,
        )

        result_json["product_name"] = product_name
        analysis = CompetitorAnalysis(**result_json)

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
