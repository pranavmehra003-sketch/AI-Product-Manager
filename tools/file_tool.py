"""
File parsing tool — CSV and JSON input handling for customer feedback and analytics.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional, Union
import io
import pandas as pd


def parse_feedback_csv(file_content: Union[str, bytes, io.BytesIO]) -> List[str]:
    """
    Parse a CSV file containing customer feedback.
    
    Expected columns (flexible): 'feedback', 'text', 'review', 'comment', 'message'
    Returns a list of feedback strings.
    """
    try:
        if isinstance(file_content, bytes):
            df = pd.read_csv(io.BytesIO(file_content))
        elif isinstance(file_content, str):
            df = pd.read_csv(io.StringIO(file_content))
        else:
            df = pd.read_csv(file_content)

        # Try common column names
        text_columns = ["feedback", "text", "review", "comment", "message",
                        "Feedback", "Text", "Review", "Comment", "Message",
                        "FEEDBACK", "TEXT", "REVIEW", "COMMENT"]

        for col in text_columns:
            if col in df.columns:
                return [str(v).strip() for v in df[col].dropna().tolist() if str(v).strip()]

        # Fallback: use first text-like column
        for col in df.columns:
            if df[col].dtype == object:
                return [str(v).strip() for v in df[col].dropna().tolist() if str(v).strip()]

        return []
    except Exception as e:
        raise ValueError(f"Failed to parse feedback CSV: {e}")


def parse_analytics_json(file_content: Union[str, bytes, io.BytesIO]) -> Dict[str, Any]:
    """
    Parse a JSON file containing product analytics data.
    Returns raw analytics dict.
    """
    try:
        if isinstance(file_content, bytes):
            return json.loads(file_content.decode("utf-8"))
        elif isinstance(file_content, str):
            return json.loads(file_content)
        else:
            content = file_content.read()
            return json.loads(content)
    except Exception as e:
        raise ValueError(f"Failed to parse analytics JSON: {e}")


def parse_features_csv(file_content: Union[str, bytes, io.BytesIO]) -> List[Dict[str, Any]]:
    """
    Parse a CSV file containing feature backlog items.
    Returns a list of feature dicts.
    """
    try:
        if isinstance(file_content, bytes):
            df = pd.read_csv(io.BytesIO(file_content))
        elif isinstance(file_content, str):
            df = pd.read_csv(io.StringIO(file_content))
        else:
            df = pd.read_csv(file_content)

        return df.to_dict(orient="records")
    except Exception as e:
        raise ValueError(f"Failed to parse features CSV: {e}")


def format_feedback_for_llm(feedback_list: List[str], max_items: int = 200) -> str:
    """Format feedback list as numbered text for LLM consumption."""
    items = feedback_list[:max_items]
    return "\n".join(f"{i+1}. {fb}" for i, fb in enumerate(items))


def format_analytics_for_llm(analytics: Dict[str, Any]) -> str:
    """Format analytics dict as readable text for LLM consumption."""
    return json.dumps(analytics, indent=2)


def validate_feedback_list(feedback: List[str]) -> tuple[List[str], List[str]]:
    """Validate feedback items; return (valid, errors)."""
    valid = []
    errors = []
    for item in feedback:
        if not isinstance(item, str):
            errors.append(f"Non-string item: {item}")
        elif len(item.strip()) < 5:
            errors.append(f"Too short: {item}")
        elif len(item) > 5000:
            valid.append(item[:5000])  # Truncate very long items
        else:
            valid.append(item.strip())
    return valid, errors
