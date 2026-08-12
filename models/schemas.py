"""
Pydantic schemas for all data structures in the AI Product Manager system.
"""
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# Feedback Agent Models
# ─────────────────────────────────────────────

class FeedbackItem(BaseModel):
    id: int
    text: str
    source: Optional[str] = "unknown"
    date: Optional[str] = None


class FeedbackIssue(BaseModel):
    category: str
    issue: str
    frequency: int
    impact: Literal["Critical", "High", "Medium", "Low"]
    sentiment: Literal["Negative", "Neutral", "Positive"]
    sample_quotes: List[str] = Field(default_factory=list)


class FeatureRequest(BaseModel):
    feature: str
    frequency: int
    impact: Literal["High", "Medium", "Low"]
    customer_segment: Optional[str] = None


class FeedbackAnalysis(BaseModel):
    total_feedback: int
    issues: List[FeedbackIssue] = Field(default_factory=list)
    feature_requests: List[FeatureRequest] = Field(default_factory=list)
    overall_sentiment: str
    top_themes: List[str] = Field(default_factory=list)
    analysis_summary: str


# ─────────────────────────────────────────────
# Competitor Agent Models
# ─────────────────────────────────────────────

class CompetitorFeature(BaseModel):
    competitor_name: str
    feature: str
    description: Optional[str] = None
    availability: bool = True
    quality: Literal["Excellent", "Good", "Average", "Poor"] = "Good"


class Competitor(BaseModel):
    name: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    pricing: Optional[str] = None
    recent_launches: List[str] = Field(default_factory=list)


class CompetitorAnalysis(BaseModel):
    product_name: str
    competitors: List[Competitor] = Field(default_factory=list)
    competitor_features: List[CompetitorFeature] = Field(default_factory=list)
    market_gaps: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    analysis_summary: str


# ─────────────────────────────────────────────
# Analytics Agent Models
# ─────────────────────────────────────────────

class FeatureMetric(BaseModel):
    feature: str
    dau: Optional[int] = None
    mau: Optional[int] = None
    usage_percent: Optional[float] = None
    retention_impact: Literal["High", "Medium", "Low"] = "Medium"
    conversion_rate: Optional[float] = None
    churn_correlation: Optional[float] = None
    error_rate: Optional[float] = None
    avg_session_duration: Optional[float] = None
    trend: Literal["Increasing", "Stable", "Decreasing"] = "Stable"


class ProductAnalytics(BaseModel):
    product_name: str
    period: Optional[str] = None
    overall_dau: Optional[int] = None
    overall_mau: Optional[int] = None
    overall_retention: Optional[float] = None
    feature_metrics: List[FeatureMetric] = Field(default_factory=list)
    high_impact_areas: List[str] = Field(default_factory=list)
    risk_areas: List[str] = Field(default_factory=list)
    analytics_summary: str


# ─────────────────────────────────────────────
# Prioritization Agent Models
# ─────────────────────────────────────────────

class FeaturePriority(BaseModel):
    feature: str
    description: str
    customer_impact: float = Field(ge=0, le=10)
    business_value: float = Field(ge=0, le=10)
    strategic_alignment: float = Field(ge=0, le=10)
    urgency: float = Field(ge=0, le=10)
    feasibility: float = Field(ge=0, le=10)
    priority_score: float = Field(ge=0, le=10)
    priority: Literal["P0", "P1", "P2", "P3"]
    reason: str
    estimated_effort: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    source: str = "analysis"  # feedback / analytics / competitor / manual


class PrioritizationResult(BaseModel):
    features: List[FeaturePriority] = Field(default_factory=list)
    p0_count: int = 0
    p1_count: int = 0
    p2_count: int = 0
    p3_count: int = 0
    methodology: str
    recommendation_summary: str


# ─────────────────────────────────────────────
# PRD Agent Models
# ─────────────────────────────────────────────

class UserStory(BaseModel):
    persona: str
    action: str
    benefit: str
    acceptance_criteria: List[str] = Field(default_factory=list)


class PRDDocument(BaseModel):
    feature_name: str
    version: str = "1.0"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    author: str = "AI Product Manager"
    priority: str
    problem_statement: str
    background: str
    user_personas: List[str] = Field(default_factory=list)
    user_stories: List[UserStory] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    non_goals: List[str] = Field(default_factory=list)
    functional_requirements: List[str] = Field(default_factory=list)
    non_functional_requirements: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    technical_considerations: str
    timeline_estimate: Optional[str] = None


# ─────────────────────────────────────────────
# Sprint Planner Agent Models
# ─────────────────────────────────────────────

class SprintTask(BaseModel):
    task: str
    description: str
    story_points: int
    assignee: str
    team: Literal["Backend", "Frontend", "Design", "QA", "DevOps", "Full-Stack"]
    priority: Literal["Must Have", "Should Have", "Nice to Have"]
    dependencies: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)


class SprintPlan(BaseModel):
    sprint_name: str
    sprint_number: int
    duration_weeks: int = 2
    total_capacity: int
    used_capacity: int
    features_covered: List[str] = Field(default_factory=list)
    tasks: List[SprintTask] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    definition_of_done: List[str] = Field(default_factory=list)
    sprint_goal: str


# ─────────────────────────────────────────────
# Orchestrator / System Models
# ─────────────────────────────────────────────

class AgentStatus(BaseModel):
    agent_name: str
    status: Literal["pending", "running", "success", "error", "skipped"]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0


class OrchestratorState(BaseModel):
    session_id: str
    product_name: str
    business_goals: List[str] = Field(default_factory=list)
    engineering_capacity: int = 40
    team_size: int = 5
    sprint_number: int = 1
    agent_statuses: Dict[str, AgentStatus] = Field(default_factory=dict)
    feedback_analysis: Optional[FeedbackAnalysis] = None
    competitor_analysis: Optional[CompetitorAnalysis] = None
    product_analytics: Optional[ProductAnalytics] = None
    prioritization_result: Optional[PrioritizationResult] = None
    approved_features: List[FeaturePriority] = Field(default_factory=list)
    prds: List[PRDDocument] = Field(default_factory=list)
    sprint_plan: Optional[SprintPlan] = None
    human_approved: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    raw_feedback: List[str] = Field(default_factory=list)
    raw_analytics: Dict[str, Any] = Field(default_factory=dict)


class ErrorLog(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    agent_name: str
    session_id: str
    error_message: str
    retry_count: int = 0
    status: Literal["retrying", "failed", "resolved"] = "failed"


class AgentResult(BaseModel):
    agent: str
    status: Literal["success", "error"]
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
