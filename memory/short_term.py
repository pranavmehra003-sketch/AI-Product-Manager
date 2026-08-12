"""
Short-term memory — in-session context store for agent-to-agent communication.
Stores the current orchestration state as a Python dict in memory.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime


class ShortTermMemory:
    """
    Session-scoped memory store.
    Holds all agent outputs for the current analysis session.
    Thread-safe for single-session Streamlit use.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self._store: Dict[str, Any] = {}
        self._history: List[Dict[str, Any]] = []
        self.created_at = datetime.now().isoformat()

    # ─── Core Operations ──────────────────────────────────────────────────────

    def set(self, key: str, value: Any) -> None:
        """Store a value and record the change in history."""
        self._store[key] = value
        self._history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "set",
            "key": key,
            "type": type(value).__name__,
        })

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the store."""
        return self._store.get(key, default)

    def update(self, data: Dict[str, Any]) -> None:
        """Update multiple keys at once."""
        for k, v in data.items():
            self.set(k, v)

    def delete(self, key: str) -> None:
        """Remove a key from the store."""
        if key in self._store:
            del self._store[key]

    def clear(self) -> None:
        """Clear all stored values."""
        self._store.clear()
        self._history.clear()

    def has(self, key: str) -> bool:
        """Check if a key exists."""
        return key in self._store

    def keys(self) -> List[str]:
        """Return all stored keys."""
        return list(self._store.keys())

    def snapshot(self) -> Dict[str, Any]:
        """Return a copy of the full memory store."""
        return dict(self._store)

    def history(self) -> List[Dict[str, Any]]:
        """Return the full change history."""
        return list(self._history)

    # ─── Agent Context Keys (convenience methods) ─────────────────────────────

    def set_feedback_analysis(self, data: Any) -> None:
        self.set("feedback_analysis", data)

    def get_feedback_analysis(self) -> Optional[Any]:
        return self.get("feedback_analysis")

    def set_competitor_analysis(self, data: Any) -> None:
        self.set("competitor_analysis", data)

    def get_competitor_analysis(self) -> Optional[Any]:
        return self.get("competitor_analysis")

    def set_product_analytics(self, data: Any) -> None:
        self.set("product_analytics", data)

    def get_product_analytics(self) -> Optional[Any]:
        return self.get("product_analytics")

    def set_prioritization(self, data: Any) -> None:
        self.set("prioritization_result", data)

    def get_prioritization(self) -> Optional[Any]:
        return self.get("prioritization_result")

    def set_approved_features(self, features: List[Any]) -> None:
        self.set("approved_features", features)

    def get_approved_features(self) -> List[Any]:
        return self.get("approved_features", [])

    def set_prds(self, prds: List[Any]) -> None:
        self.set("prds", prds)

    def get_prds(self) -> List[Any]:
        return self.get("prds", [])

    def set_sprint_plan(self, plan: Any) -> None:
        self.set("sprint_plan", plan)

    def get_sprint_plan(self) -> Optional[Any]:
        return self.get("sprint_plan")

    def __repr__(self) -> str:
        return f"<ShortTermMemory session={self.session_id} keys={self.keys()}>"
