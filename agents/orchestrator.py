"""
Orchestrator Agent — Controls the complete multi-agent workflow.
Runs feedback/competitor/analytics agents in parallel, then sequences
the remaining pipeline with human approval checkpoint.
"""
from __future__ import annotations
import concurrent.futures
import time
import uuid
from datetime import datetime
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional

from models.schemas import OrchestratorState, AgentStatus
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory

import agents.feedback_agent as feedback_agent
import agents.competitor_agent as competitor_agent
import agents.analytics_agent as analytics_agent
import agents.prioritization_agent as prioritization_agent
import agents.prd_agent as prd_agent
import agents.sprint_agent as sprint_agent
from rag.retriever import get_retriever
from tools.error_handler import log_error
from tools.simulation_fallback import (
    simulate_feedback_analysis,
    simulate_competitor_analysis,
    simulate_product_analytics,
    simulate_prioritization,
    simulate_prd_writer,
    simulate_sprint_planner,
)
from models.schemas import AgentResult


class Orchestrator:
    """
    Master controller for the AI Product Manager pipeline.
    
    Workflow:
    1. Parallel: Feedback + Competitor + Analytics agents
    2. Sequential: Prioritization agent (combines all above)
    3. *** HUMAN APPROVAL CHECKPOINT ***
    4. Sequential: PRD agent (for each approved feature)
    5. Sequential: Sprint planner agent
    """

    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.memory = ShortTermMemory(self.session_id)
        self.ltm = LongTermMemory()
        self.state = OrchestratorState(
            session_id=self.session_id,
            product_name="Product",
        )
        self._status_callback: Optional[Callable] = None
        self._retriever = None

    def set_status_callback(self, callback: Callable[[str, str, str], None]) -> None:
        """
        Register a callback for agent status updates.
        Called with (agent_name, status, message).
        """
        self._status_callback = callback

    def _emit(self, agent: str, status: str, message: str = "") -> None:
        """Emit a status update via the callback."""
        self.state.agent_statuses[agent] = AgentStatus(
            agent_name=agent,
            status=status,
            started_at=datetime.now().isoformat() if status == "running" else None,
            completed_at=datetime.now().isoformat() if status in ("success", "error") else None,
        )
        if self._status_callback:
            self._status_callback(agent, status, message)

    def configure(
        self,
        product_name: str,
        product_domain: str,
        business_goals: List[str],
        engineering_capacity: int = 40,
        team_size: int = 5,
        sprint_number: int = 1,
        competitors: Optional[List[str]] = None,
    ) -> None:
        """Configure the orchestrator for a new session."""
        self.state.product_name = product_name
        self.state.business_goals = business_goals
        self.state.engineering_capacity = engineering_capacity
        self.state.team_size = team_size
        self.state.sprint_number = sprint_number
        self.memory.set("product_domain", product_domain)
        self.memory.set("competitors", competitors or [])
        self._emit("orchestrator", "pending", "Configured")

    # ─── Phase 1: Parallel Analysis ──────────────────────────────────────────

    def run_feedback_analysis(self, feedback_list: List[str]) -> bool:
        """Run the feedback analysis agent. Falls back to simulation on any error."""
        self._emit("feedback_agent", "running", f"Analyzing {len(feedback_list)} feedback items...")
        self.state.raw_feedback = feedback_list

        try:
            result = feedback_agent.run(
                feedback_list=feedback_list,
                product_name=self.state.product_name,
                session_id=self.session_id,
            )
        except Exception as real_error:
            log_error("feedback_agent", self.session_id, f"Using simulation mode. LLM error: {str(real_error)[:120]}")
            result = SimpleNamespace(status="error", error=str(real_error), data=None, source=None)

        # Trigger simulation fallback both for exceptions AND non-success AgentResults
        # (agents catch their own exceptions and return status="error" internally)
        if result.status != "success":
            err = getattr(result, "error", "") or str(result)
            log_error("feedback_agent", self.session_id, f"Using simulation mode. Agent error: {err[:120]}")
            simulated = simulate_feedback_analysis(feedback_list)
            result = SimpleNamespace(status="success", data=simulated, error=None, source="simulation")

        data = result.data
        self.state.feedback_analysis = data
        self.memory.set_feedback_analysis(data)
        n_issues = len(data.get("issues", []))
        n_feat = len(data.get("feature_requests", []))
        suffix = " (demo data)" if getattr(result, "source", "") == "simulation" else ""
        self._emit("feedback_agent", "success",
                   f"Found {n_issues} issues, {n_feat} feature requests{suffix}")
        return True

    def run_competitor_research(self) -> bool:
        """Run the competitor research agent. Falls back to simulation on any error."""
        product_domain = self.memory.get("product_domain", self.state.product_name)
        competitors = self.memory.get("competitors", [])
        self._emit("competitor_agent", "running", f"Researching {product_domain} competitors...")

        try:
            result = competitor_agent.run(
                product_name=self.state.product_name,
                product_domain=product_domain,
                competitors=competitors,
                session_id=self.session_id,
            )
        except Exception as real_error:
            log_error("competitor_agent", self.session_id, f"Using simulation mode. LLM error: {str(real_error)[:120]}")
            result = SimpleNamespace(status="error", error=str(real_error), data=None, source=None)

        if result.status != "success":
            err = getattr(result, "error", "") or str(result)
            log_error("competitor_agent", self.session_id, f"Using simulation mode. Agent error: {err[:120]}")
            simulated = simulate_competitor_analysis(product_domain, competitors)
            result = SimpleNamespace(status="success", data=simulated, error=None, source="simulation")

        data = result.data
        self.state.competitor_analysis = data
        self.memory.set_competitor_analysis(data)
        comp_count = len(data.get("competitors", []))
        gap_count = len(data.get("market_gaps", []))
        suffix = " (demo data)" if getattr(result, "source", "") == "simulation" else ""
        self._emit("competitor_agent", "success",
                   f"Found {comp_count} competitors, {gap_count} market gaps{suffix}")
        return True

    def run_analytics_analysis(self, analytics_data: Dict[str, Any]) -> bool:
        """Run the product analytics agent. Falls back to simulation on any error."""
        self._emit("analytics_agent", "running", "Analyzing product metrics...")
        self.state.raw_analytics = analytics_data

        try:
            result = analytics_agent.run(
                analytics_data=analytics_data,
                product_name=self.state.product_name,
                session_id=self.session_id,
            )
        except Exception as real_error:
            log_error("analytics_agent", self.session_id, f"Using simulation mode. LLM error: {str(real_error)[:120]}")
            result = SimpleNamespace(status="error", error=str(real_error), data=None, source=None)

        if result.status != "success":
            err = getattr(result, "error", "") or str(result)
            log_error("analytics_agent", self.session_id, f"Using simulation mode. Agent error: {err[:120]}")
            fb = self.memory.get_feedback_analysis() or {}
            topics = [i.get("issue", "") for i in fb.get("issues", [])]
            simulated = simulate_product_analytics(analytics_data, topics)
            # Normalize: simulation puts metrics under "features" -> rename for schema compatibility
            if "features" in simulated and "feature_metrics" not in simulated:
                simulated["feature_metrics"] = simulated["features"]
            result = SimpleNamespace(status="success", data=simulated, error=None, source="simulation")

        data = result.data
        # Normalize key name
        if "feature_metrics" not in data and "features" in data:
            data["feature_metrics"] = data["features"]
        self.state.product_analytics = data
        self.memory.set_product_analytics(data)
        metrics_count = len(data.get("feature_metrics", []))
        suffix = " (demo data)" if getattr(result, "source", "") == "simulation" else ""
        self._emit("analytics_agent", "success", f"Analyzed {metrics_count} feature metrics{suffix}")
        return True

    def run_parallel_analysis(
        self,
        feedback_list: List[str],
        analytics_data: Dict[str, Any],
    ) -> Dict[str, bool]:
        """
        Run feedback, competitor, and analytics agents in parallel.
        Returns dict of {agent_name: success}.
        """
        results = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.run_feedback_analysis, feedback_list): "feedback",
                executor.submit(self.run_competitor_research): "competitor",
                executor.submit(self.run_analytics_analysis, analytics_data): "analytics",
            }

            for future in concurrent.futures.as_completed(futures):
                agent_name = futures[future]
                try:
                    results[agent_name] = future.result()
                except Exception as e:
                    results[agent_name] = False
                    self._emit(f"{agent_name}_agent", "error", str(e))

        return results

    # ─── Phase 2: Prioritization ─────────────────────────────────────────────

    def run_prioritization(self) -> bool:
        """Run the feature prioritization agent. Falls back to simulation on any error."""
        self._emit("prioritization_agent", "running", "Scoring and ranking features...")

        past_context = self.ltm.get_past_features_summary()

        # Prefer data directly from state over ShortTermMemory — avoids any serialization
        # round-trip issues that can make data appear empty when running fallbacks.
        fb_data = self.state.feedback_analysis or self.memory.get_feedback_analysis() or {}
        comp_data = self.state.competitor_analysis or self.memory.get_competitor_analysis() or {}
        ana_data = self.state.product_analytics or self.memory.get_product_analytics() or {}

        try:
            result = prioritization_agent.run(
                feedback_analysis=fb_data,
                competitor_analysis=comp_data,
                product_analytics=ana_data,
                business_goals=self.state.business_goals,
                engineering_capacity=self.state.engineering_capacity,
                past_features_context=past_context,
                session_id=self.session_id,
            )
        except Exception as real_error:
            log_error("prioritization_agent", self.session_id, f"Using simulation mode. LLM error: {str(real_error)[:120]}")
            result = SimpleNamespace(status="error", error=str(real_error), data=None, source=None)

        if result.status != "success":
            err = getattr(result, "error", "") or str(result)
            log_error("prioritization_agent", self.session_id, f"Using simulation mode. Agent error: {err[:120]}")
            simulated = simulate_prioritization(
                feedback=fb_data,
                competitors=comp_data,
                analytics=ana_data,
                business_goals=self.state.business_goals,
            )
            result = SimpleNamespace(status="success", data=simulated, error=None, source="simulation")

        # Extra safety: if LLM succeeded but returned 0 features, still use simulation
        data = result.data
        if not data.get("features", []):
            log_error("prioritization_agent", self.session_id, "Using simulation mode. LLM returned empty feature list.")
            simulated = simulate_prioritization(
                feedback=fb_data,
                competitors=comp_data,
                analytics=ana_data,
                business_goals=self.state.business_goals,
            )
            result = SimpleNamespace(status="success", data=simulated, error=None, source="simulation")
            data = result.data

        self.state.prioritization_result = data
        self.memory.set_prioritization(data)
        features = data.get("features", [])
        p0 = sum(1 for f in features if f.get("priority") == "P0")
        suffix = " (demo data)" if getattr(result, "source", "") == "simulation" else ""
        self._emit("prioritization_agent", "success",
                   f"Ranked {len(features)} features, {p0} are P0 (Critical){suffix}")
        return True

    # ─── Phase 3: Human Approval (handled by UI) ─────────────────────────────

    def set_approved_features(self, approved_features: List[Dict]) -> None:
        """
        Called by the UI after PM reviews and approves features.
        Saves approved features to memory and long-term storage.
        """
        self.state.approved_features = approved_features
        self.state.human_approved = True
        self.memory.set_approved_features(approved_features)

        for feat in approved_features:
            try:
                self.ltm.remember_approved_feature(
                    session_id=self.session_id,
                    feature_name=feat.get("feature", ""),
                    priority=feat.get("priority", "P1"),
                    priority_score=feat.get("priority_score", 0.0),
                    reason=feat.get("reason", ""),
                )
            except Exception:
                pass
            try:
                self.ltm.log_decision(
                    self.session_id,
                    "feature_approved",
                    f"Approved: {feat.get('feature')} ({feat.get('priority')})",
                )
            except Exception:
                pass

        self._emit("human_approval", "success",
                   f"PM approved {len(approved_features)} features")

    # ─── Phase 4: PRD Generation ──────────────────────────────────────────────

    def run_prd_generation(self) -> bool:
        """Generate PRDs for all approved features. Falls back to simulation on error."""
        approved = self.state.approved_features
        if not approved:
            self._emit("prd_agent", "error", "No approved features to generate PRDs for")
            return False

        self._emit("prd_agent", "running", f"Writing PRDs for {len(approved)} features...")

        # Initialize RAG retriever
        try:
            retriever = get_retriever()
        except Exception:
            retriever = None

        prds = []
        product_domain = self.memory.get("product_domain", self.state.product_name)
        prioritization = self.memory.get_prioritization() or {}
        used_demo = False

        for feat in approved[:4]:  # Max 4 PRDs per session
            try:
                rag_context = ""
                if retriever:
                    try:
                        rag_context = retriever.get_similar_prds(feat.get("feature", "") or feat.get("name", ""))
                    except Exception:
                        rag_context = ""

                result = prd_agent.run(
                    feature=feat,
                    product_name=self.state.product_name,
                    rag_context=rag_context,
                    session_id=self.session_id,
                )

                if result.status != "success":
                    raise RuntimeError(result.error or "PRD agent returned non-success")

            except Exception as real_error:
                log_error("prd_agent", self.session_id, f"Using simulation mode. LLM error: {str(real_error)[:120]}")
                fname = feat.get("feature") or feat.get("name") or "Unknown feature"
                simulated = simulate_prd_writer(
                    feature_name=fname,
                    product_name=self.state.product_name,
                    product_domain=product_domain,
                    prioritization=prioritization,
                )
                used_demo = True
                result = SimpleNamespace(status="success", data=simulated, error=None, source="simulation")

            if result.status == "success":
                prds.append(result.data)
                try:
                    self.ltm.save_prd(
                        self.session_id,
                        feat.get("feature", "") or feat.get("name", ""),
                        feat.get("priority", "P1"),
                        result.data,
                    )
                except Exception:
                    pass
                # Add to RAG for future reference
                try:
                    if retriever:
                        prd_text = "PRD: " + str(result.data)
                        retriever.add_prd(feat.get("feature", "") or feat.get("name", ""), prd_text)
                except Exception:
                    pass

        self.state.prds = prds
        self.memory.set_prds(prds)

        if prds:
            suffix = " (demo data)" if used_demo else ""
            self._emit("prd_agent", "success", f"Generated {len(prds)} PRD(s){suffix}")
            return True
        else:
            self._emit("prd_agent", "error", "Failed to generate any PRDs")
            return False

    # ─── Phase 5: Sprint Planning ─────────────────────────────────────────────

    def run_sprint_planning(self) -> bool:
        """Create sprint plan from approved features and PRDs. Falls back to simulation on error."""
        self._emit("sprint_agent", "running", "Creating sprint plan...")

        used_demo = False
        try:
            result = sprint_agent.run(
                approved_features=self.state.approved_features,
                prds=self.state.prds,
                engineering_capacity=self.state.engineering_capacity,
                sprint_number=self.state.sprint_number,
                team_size=self.state.team_size,
                session_id=self.session_id,
            )
            if result.status != "success":
                raise RuntimeError(result.error or "Sprint agent returned non-success")
        except Exception as real_error:
            log_error("sprint_agent", self.session_id, f"Using simulation mode. LLM error: {str(real_error)[:120]}")
            simulated = simulate_sprint_planner(
                approved_features=self.state.approved_features or [],
                prds=self.state.prds or [],
                capacity=self.state.engineering_capacity,
                team_size=self.state.team_size,
                sprint_number=self.state.sprint_number,
            )
            # Normalize simulation output keys to match expected schema
            sim_out = dict(simulated)
            sim_out["sprint_name"] = sim_out.get("sprint", f"Sprint {self.state.sprint_number}")
            sim_out["used_capacity"] = sim_out.get("committed_story_points", 0)
            sim_out["total_tasks"] = len(sim_out.get("tasks", []) or [])
            used_demo = True
            result = SimpleNamespace(status="success", data=sim_out, error=None, source="simulation")

        if result.status == "success":
            data = result.data
            self.state.sprint_plan = data
            self.memory.set_sprint_plan(data)
            try:
                self.ltm.save_sprint(
                    self.session_id,
                    data.get("sprint_name", data.get("sprint", "Sprint")),
                    data,
                )
            except Exception:
                pass
            tasks = data.get("tasks", [])
            used_sp = data.get("used_capacity", data.get("committed_story_points", 0))
            suffix = " (demo data)" if used_demo else ""
            self._emit("sprint_agent", "success",
                       f"Created {len(tasks)} tasks using {used_sp}/{self.state.engineering_capacity} story points{suffix}")
            return True
        else:
            try:
                self.ltm.log_error("sprint_agent", self.session_id, result.error or "Sprint planning failed")
            except Exception:
                pass
            self._emit("sprint_agent", "error", result.error or "Sprint planning failed")
            return False

    # ─── Save Session ─────────────────────────────────────────────────────────

    def save_session(self) -> None:
        """Persist the session state to long-term memory."""
        try:
            self.ltm.save_session(
                self.session_id,
                self.state.product_name,
                self.state,
            )
        except Exception as e:
            print(f"[Orchestrator] Failed to save session: {e}")

    def get_state(self) -> OrchestratorState:
        return self.state

    def get_error_logs(self) -> List[Dict]:
        return self.ltm.get_errors(self.session_id)
