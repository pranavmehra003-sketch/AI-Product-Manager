"""
Long-term memory — SQLite-backed persistent store for product decisions.
Wraps database_tool.py with a convenient interface.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional

from tools.database_tool import (
    initialize_database,
    save_session,
    load_session,
    list_sessions,
    save_approved_feature,
    save_rejected_feature,
    get_past_approved_features,
    save_prd,
    list_prds,
    save_sprint_plan,
    save_error_log,
    get_error_logs,
    save_decision,
)


class LongTermMemory:
    """
    Persistent memory backed by SQLite.
    Remembers approved/rejected features, PRDs, sprints, and decisions
    across sessions.
    """

    def __init__(self):
        initialize_database()

    # ─── Sessions ──────────────────────────────────────────────────────────────

    def save_session(self, session_id: str, product_name: str, state: Any) -> None:
        """Persist the full session state."""
        try:
            state_json = state.model_dump_json() if hasattr(state, "model_dump_json") else json.dumps(state)
            save_session(session_id, product_name, state_json)
        except Exception as e:
            print(f"[LTM] Failed to save session: {e}")

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return load_session(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        return list_sessions()

    # ─── Features ──────────────────────────────────────────────────────────────

    def remember_approved_feature(
        self,
        session_id: str,
        feature_name: str,
        priority: str,
        priority_score: float,
        reason: str,
    ) -> None:
        try:
            save_approved_feature(session_id, feature_name, priority, priority_score, reason)
        except Exception as e:
            print(f"[LTM] Failed to save approved feature: {e}")

    def remember_rejected_feature(self, session_id: str, feature_name: str, reason: str) -> None:
        try:
            save_rejected_feature(session_id, feature_name, reason)
        except Exception as e:
            print(f"[LTM] Failed to save rejected feature: {e}")

    def get_past_features(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve previously approved features for context."""
        try:
            return get_past_approved_features(limit)
        except Exception:
            return []

    def get_past_features_summary(self) -> str:
        """Return a text summary of past approved features."""
        features = self.get_past_features(20)
        if not features:
            return "No previous features found."
        lines = []
        for f in features:
            lines.append(
                f"- {f['feature_name']} ({f['priority']}, score={f['priority_score']:.1f}) "
                f"approved on {f['approved_at'][:10]}"
            )
        return "\n".join(lines)

    # ─── PRDs ──────────────────────────────────────────────────────────────────

    def save_prd(self, session_id: str, feature_name: str, priority: str, prd_data: Dict) -> None:
        try:
            save_prd(session_id, feature_name, priority, prd_data)
        except Exception as e:
            print(f"[LTM] Failed to save PRD: {e}")

    def list_prds(self) -> List[Dict[str, Any]]:
        try:
            return list_prds()
        except Exception:
            return []

    # ─── Sprint Plans ──────────────────────────────────────────────────────────

    def save_sprint(self, session_id: str, sprint_name: str, sprint_data: Dict) -> None:
        try:
            save_sprint_plan(session_id, sprint_name, sprint_data)
        except Exception as e:
            print(f"[LTM] Failed to save sprint: {e}")

    # ─── Error Logs ────────────────────────────────────────────────────────────

    def log_error(
        self,
        agent_name: str,
        session_id: str,
        error_message: str,
        retry_count: int = 0,
        status: str = "failed",
    ) -> None:
        try:
            save_error_log(agent_name, session_id, error_message, retry_count, status)
        except Exception as e:
            print(f"[LTM] Failed to log error: {e}")

    def get_errors(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            return get_error_logs(session_id)
        except Exception:
            return []

    # ─── Decisions ─────────────────────────────────────────────────────────────

    def log_decision(self, session_id: str, decision_type: str, decision_text: str, made_by: str = "PM") -> None:
        try:
            save_decision(session_id, decision_type=decision_type, decision_text=decision_text, made_by=made_by)
        except Exception as e:
            print(f"[LTM] Failed to log decision: {e}")
