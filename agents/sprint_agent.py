"""
Sprint Planner Agent — Creates sprint plans from approved PRDs
based on team capacity and engineering constraints.
"""
from __future__ import annotations
import json
import time
from typing import Any, Dict, List, Optional

from models.schemas import SprintPlan, SprintTask, AgentResult
from tools.openai_tool import chat_json
from tools.error_handler import log_error


SYSTEM_PROMPT = """You are an expert Agile Coach and Engineering Manager specializing in 
sprint planning and task decomposition. You create realistic, achievable sprint plans.

STORY POINT GUIDE:
- 1 SP: Trivial (< 2 hours)
- 2 SP: Simple (half day)
- 3 SP: Small (1 day)
- 5 SP: Medium (2-3 days)
- 8 SP: Large (4-5 days)
- 13 SP: Extra Large (full sprint for one person)

You must return a valid JSON object with this exact structure:
{
  "sprint_name": "<Sprint Name>",
  "sprint_number": <number>,
  "duration_weeks": 2,
  "total_capacity": <total story points>,
  "used_capacity": <sum of all task story points>,
  "sprint_goal": "<clear, single-sentence sprint goal>",
  "features_covered": ["feature1", "feature2"],
  "definition_of_done": [
    "Code reviewed and approved by at least one team member",
    "Unit tests written with >80% coverage",
    "Integration tests passing",
    "Documentation updated",
    "Product Manager demo completed and approved"
  ],
  "risks": ["risk1", "risk2"],
  "tasks": [
    {
      "task": "<task title>",
      "description": "<what specifically needs to be done>",
      "story_points": <1|2|3|5|8|13>,
      "assignee": "<Backend Team | Frontend Team | Design Team | QA Team | Full-Stack Team>",
      "team": "<Backend | Frontend | Design | QA | DevOps | Full-Stack>",
      "priority": "<Must Have | Should Have | Nice to Have>",
      "dependencies": ["task that must be done first"],
      "acceptance_criteria": ["criterion 1", "criterion 2"]
    }
  ]
}

Rules:
- Total used_capacity must not exceed total_capacity
- Break each feature into 3-6 granular engineering tasks
- Include Design, Backend, Frontend, and QA tasks for each feature
- Must Have tasks should never exceed 80% of capacity (leave buffer for bugs/reviews)
- Order tasks logically (design before frontend, backend before integration)
- Keep used_capacity ≤ total_capacity
"""


def run(
    approved_features: List[Dict[str, Any]],
    prds: List[Dict[str, Any]],
    engineering_capacity: int = 40,
    sprint_number: int = 1,
    team_size: int = 5,
    session_id: str = "unknown",
) -> AgentResult:
    """
    Create a sprint plan from approved features and PRDs.
    
    Args:
        approved_features: List of approved FeaturePriority dicts
        prds: List of PRDDocument dicts
        engineering_capacity: Total story points available
        sprint_number: Sprint number
        team_size: Number of engineers
        session_id: Current session ID for error logging
    
    Returns:
        AgentResult with SprintPlan data
    """
    start_time = time.time()
    agent_name = "sprint_agent"

    try:
        if not approved_features:
            raise ValueError("No approved features to plan sprint for.")

        # Build feature context from PRDs
        feature_sections = []
        prd_map = {prd.get("feature_name", ""): prd for prd in prds}

        for feat in approved_features[:4]:  # Max 4 features per sprint
            fname = feat.get("feature", "")
            priority = feat.get("priority", "P1")
            effort = feat.get("estimated_effort", "1 sprint")
            prd = prd_map.get(fname, {})

            section = f"""### {fname} ({priority})
Estimated Effort: {effort}
Description: {feat.get('description', '')}"""

            if prd:
                func_reqs = prd.get("functional_requirements", [])[:5]
                nonfunc_reqs = prd.get("non_functional_requirements", [])[:3]
                if func_reqs:
                    section += f"\nKey Functional Requirements:\n" + "\n".join(f"  - {r}" for r in func_reqs)
                if nonfunc_reqs:
                    section += f"\nNon-Functional Requirements:\n" + "\n".join(f"  - {r}" for r in nonfunc_reqs)
                tech_notes = prd.get("technical_considerations", "")
                if tech_notes:
                    section += f"\nTechnical Notes: {tech_notes[:200]}"

            feature_sections.append(section)

        features_text = "\n\n".join(feature_sections)
        feature_names = [f.get("feature", "") for f in approved_features[:4]]

        user_prompt = f"""Create a sprint plan for Sprint {sprint_number}.

Team Size: {team_size} engineers
Sprint Capacity: {engineering_capacity} story points
Sprint Duration: 2 weeks

Features to plan:
{features_text}

Important:
- Total story points used must not exceed {engineering_capacity}
- Focus on Must Have items first (leave 20% buffer for bugs)
- Include backend, frontend, design, and QA tasks
- Create a realistic plan the team can actually complete

Return the complete sprint plan as JSON."""

        result_json = chat_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=4000,
        )

        # Enforce capacity constraint
        result_json["sprint_number"] = sprint_number
        result_json["total_capacity"] = engineering_capacity
        result_json["features_covered"] = feature_names
        result_json["duration_weeks"] = 2

        # Recalculate used capacity
        tasks = result_json.get("tasks", [])
        used = sum(t.get("story_points", 0) for t in tasks)
        result_json["used_capacity"] = used

        sprint = SprintPlan(**result_json)

        elapsed = int((time.time() - start_time) * 1000)
        return AgentResult(
            agent=agent_name,
            status="success",
            data=sprint.model_dump(),
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
