"""
Database Tool — SQLite wrapper for long-term product memory.
Stores: past decisions, approved features, PRDs, sprint history, error logs.
"""
from __future__ import annotations
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional

from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./data/product_manager.db")


def get_db_path() -> str:
    path = DB_PATH
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    return path


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database() -> None:
    """Create all database tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                state_json TEXT
            );

            CREATE TABLE IF NOT EXISTS approved_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                feature_name TEXT NOT NULL,
                priority TEXT NOT NULL,
                priority_score REAL,
                reason TEXT,
                approved_at TEXT NOT NULL,
                prd_generated INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS prds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                feature_name TEXT NOT NULL,
                priority TEXT,
                prd_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sprint_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                sprint_name TEXT NOT NULL,
                sprint_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS rejected_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                feature_name TEXT NOT NULL,
                rejection_reason TEXT,
                rejected_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                session_id TEXT,
                error_message TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'failed'
            );

            CREATE TABLE IF NOT EXISTS product_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                decision_type TEXT NOT NULL,
                decision_text TEXT NOT NULL,
                made_by TEXT DEFAULT 'PM',
                created_at TEXT NOT NULL
            );
        """)
    print(f"[DB] Database initialized at: {get_db_path()}")


# ─── Session Operations ───────────────────────────────────────────────────────

def save_session(session_id: str, product_name: str, state_json: str) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO sessions (session_id, product_name, created_at, state_json)
            VALUES (?, ?, ?, ?)
        """, (session_id, product_name, datetime.now().isoformat(), state_json))


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if row:
            return dict(row)
        return None


def list_sessions() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT session_id, product_name, created_at, status FROM sessions ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
        return [dict(r) for r in rows]


# ─── Feature Operations ───────────────────────────────────────────────────────

def save_approved_feature(
    session_id: str,
    feature_name: str,
    priority: str,
    priority_score: float,
    reason: str,
) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO approved_features
                (session_id, feature_name, priority, priority_score, reason, approved_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, feature_name, priority, priority_score, reason, datetime.now().isoformat()))


def save_rejected_feature(session_id: str, feature_name: str, reason: str) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO rejected_features (session_id, feature_name, rejection_reason, rejected_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, feature_name, reason, datetime.now().isoformat()))


def get_past_approved_features(limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM approved_features ORDER BY approved_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ─── PRD Operations ──────────────────────────────────────────────────────────

def save_prd(session_id: str, feature_name: str, priority: str, prd_data: Dict) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO prds (session_id, feature_name, priority, prd_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, feature_name, priority, json.dumps(prd_data), datetime.now().isoformat()))
        conn.execute("""
            UPDATE approved_features SET prd_generated = 1
            WHERE session_id = ? AND feature_name = ?
        """, (session_id, feature_name))


def list_prds(limit: int = 20) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, session_id, feature_name, priority, created_at FROM prds ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ─── Sprint Operations ────────────────────────────────────────────────────────

def save_sprint_plan(session_id: str, sprint_name: str, sprint_data: Dict) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO sprint_plans (session_id, sprint_name, sprint_json, created_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, sprint_name, json.dumps(sprint_data), datetime.now().isoformat()))


# ─── Error Log Operations ─────────────────────────────────────────────────────

def save_error_log(
    agent_name: str,
    session_id: str,
    error_message: str,
    retry_count: int = 0,
    status: str = "failed",
) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO error_logs (timestamp, agent_name, session_id, error_message, retry_count, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), agent_name, session_id, str(error_message)[:2000], retry_count, status))


def get_error_logs(session_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        if session_id:
            rows = conn.execute(
                "SELECT * FROM error_logs WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM error_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


# ─── Decision Log ─────────────────────────────────────────────────────────────

def save_decision(session_id: str, decision_type: str, decision_text: str, made_by: str = "PM") -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO product_decisions (session_id, decision_type, decision_text, made_by, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, decision_type, decision_text, made_by, datetime.now().isoformat()))
