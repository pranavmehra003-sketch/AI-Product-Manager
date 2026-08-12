"""
PRD Writer Agent — Generates comprehensive Product Requirements Documents
using RAG to retrieve relevant past PRDs and product guidelines.
"""
from __future__ import annotations
import json
import time
from typing import Any, Dict, List, Optional

from models.schemas import PRDDocument, UserStory, AgentResult
from tools.openai_tool import chat_json
from tools.error_handler import log_error


SYSTEM_PROMPT = """You are an expert Senior Product Manager specializing in writing clear, 
comprehensive Product Requirements Documents (PRDs). You write PRDs that engineers, 
designers, and stakeholders can all understand and act on.

You must return a valid JSON object with this exact structure:
{
  "feature_name": "<exact feature name>",
  "version": "1.0",
  "author": "AI Product Manager",
  "priority": "<P0 | P1 | P2>",
  "problem_statement": "<clear 2-3 sentence problem statement>",
  "background": "<3-4 sentences of background and context>",
  "user_personas": ["Persona 1: description", "Persona 2: description"],
  "user_stories": [
    {
      "persona": "<type of user>",
      "action": "<what they want to do>",
      "benefit": "<why they want it>",
      "acceptance_criteria": [
        "Given <context>, When <action>, Then <expected result>",
        "Given <context>, When <action>, Then <expected result>"
      ]
    }
  ],
  "goals": ["measurable goal 1", "measurable goal 2"],
  "non_goals": ["explicitly out of scope 1", "explicitly out of scope 2"],
  "functional_requirements": [
    "FR-1: System shall...",
    "FR-2: System shall..."
  ],
  "non_functional_requirements": [
    "NFR-1: Performance - ...",
    "NFR-2: Security - ..."
  ],
  "success_metrics": [
    "Reduce X by Y%",
    "Increase Z metric to target"
  ],
  "dependencies": ["dependency 1", "dependency 2"],
  "risks": ["Risk: description — Mitigation: description"],
  "acceptance_criteria": [
    "Given <context>, When <action>, Then <result>"
  ],
  "technical_considerations": "<paragraph on technical approach, architecture considerations>",
  "timeline_estimate": "<e.g., 2 sprints / 4 weeks>"
}

Rules:
- Write at least 3 user stories with 2-3 acceptance criteria each
- Write at least 5 functional requirements (FR-1, FR-2, ...)
- Write at least 3 non-functional requirements (performance, security, reliability)
- Success metrics must be measurable (include specific numbers or percentages)
- Acceptance criteria must follow Given/When/Then format
- Be specific and actionable — avoid vague requirements
"""


def run(
    feature: Dict[str, Any],
    product_name: str = "our product",
    product_context: str = "",
    rag_context: str = "",
    session_id: str = "unknown",
) -> AgentResult:
    """
    Generate a comprehensive PRD for an approved feature.
    
    Args:
        feature: FeaturePriority dict with name, scores, reason
        product_name: Name of the product
        product_context: Additional product/company context
        rag_context: Retrieved context from past PRDs (RAG)
        session_id: Current session ID for error logging
    
    Returns:
        AgentResult with PRDDocument data
    """
    start_time = time.time()
    agent_name = "prd_agent"

    try:
        feature_name = feature.get("feature", "Unknown Feature")
        description = feature.get("description", "")
        priority = feature.get("priority", "P1")
        reason = feature.get("reason", "")
        score = feature.get("priority_score", 0)

        rag_section = ""
        if rag_context and "No relevant context" not in rag_context and "No similar PRDs" not in rag_context:
            rag_section = f"""
## Relevant Context from Knowledge Base
{rag_context[:2000]}
"""

        user_prompt = f"""Generate a comprehensive PRD for the following approved feature.

Product: {product_name}
Feature: {feature_name}
Description: {description}
Priority: {priority} (Score: {score}/10)
Prioritization Reason: {reason}

Scoring Breakdown:
- Customer Impact: {feature.get('customer_impact', 'N/A')}/10
- Business Value: {feature.get('business_value', 'N/A')}/10
- Strategic Alignment: {feature.get('strategic_alignment', 'N/A')}/10
- Urgency: {feature.get('urgency', 'N/A')}/10
- Feasibility: {feature.get('feasibility', 'N/A')}/10

Estimated Effort: {feature.get('estimated_effort', 'TBD')}
Dependencies: {', '.join(feature.get('dependencies', [])) or 'None'}

{product_context}
{rag_section}

Please generate a complete, detailed PRD in JSON format. Be specific and actionable."""

        result_json = chat_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=4000,
        )

        # Ensure required fields
        result_json["feature_name"] = feature_name
        result_json["priority"] = priority
        result_json["author"] = "AI Product Manager"
        result_json["version"] = "1.0"

        prd = PRDDocument(**result_json)

        elapsed = int((time.time() - start_time) * 1000)
        return AgentResult(
            agent=agent_name,
            status="success",
            data=prd.model_dump(),
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
