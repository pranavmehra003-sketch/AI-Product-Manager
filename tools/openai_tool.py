"""
LLM Tool — Multi-provider wrapper supporting Google Gemini (preferred) and OpenAI.
Provides chat completion with structured JSON output and retry logic.

Auto-selects provider based on configured API keys:
  1. If GOOGLE_API_KEY / GEMINI_API_KEY is set → use Gemini
  2. If OPENAI_API_KEY is set → use OpenAI
  3. Otherwise → error with setup instructions
"""
from __future__ import annotations
import json
import os
import re
import time
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

_openai_client = None
_gemini_model = None
_active_provider: Optional[str] = None


# ─── Provider Detection ──────────────────────────────────────────────────────

def _detect_provider() -> str:
    """Auto-detect which LLM provider to use based on configured API keys."""
    global _active_provider
    if _active_provider:
        return _active_provider

    # Respect explicit override from env
    explicit = os.getenv("LLM_PROVIDER", "").lower().strip()
    if explicit in ("gemini", "openai"):
        _active_provider = explicit
        return _active_provider

    # Prefer Gemini if key present
    gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key not in ("", "your_gemini_api_key_here"):
        _active_provider = "gemini"
        return _active_provider

    # Fall back to OpenAI
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key and openai_key != "your_openai_api_key_here":
        _active_provider = "openai"
        return _active_provider

    return "none"


def get_active_provider() -> str:
    """Return the currently active LLM provider name."""
    return _detect_provider()


# ─── Gemini Setup ─────────────────────────────────────────────────────────────

def _get_gemini_model():
    """Get or create the Gemini generative model (singleton)."""
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GOOGLE_API_KEY / GEMINI_API_KEY is not set. "
            "Please add it to your .env file or sidebar input."
        )

    import google.generativeai as genai
    genai.configure(api_key=api_key)

    model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    generation_config = {
        "temperature": 0.2,
        "top_p": 0.95,
        "top_k": 40,
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    _gemini_model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    return _gemini_model


def get_gemini_model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


# ─── OpenAI Setup ─────────────────────────────────────────────────────────────

def _get_openai_client():
    """Get or create the OpenAI client (singleton)."""
    global _openai_client
    if _openai_client is not None:
        return _openai_client

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError(
            "OPENAI_API_KEY is not set. Please add it to your .env file."
        )
    from openai import OpenAI
    _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# ─── JSON Extraction Helper ───────────────────────────────────────────────────

def _extract_json(text: str) -> Dict[str, Any]:
    """
    Robustly extract a JSON object from model output.
    Handles markdown code blocks, trailing text, and partial responses.
    """
    if not text:
        raise ValueError("Empty response from LLM, cannot parse JSON.")

    text_stripped = text.strip()

    # Try direct parse first
    try:
        return json.loads(text_stripped)
    except json.JSONDecodeError:
        pass

    # Try extracting ```json ... ``` block
    json_block_match = re.search(
        r"```(?:json)?\s*(\{[\s\S]*?\})\s*```",
        text_stripped,
        re.IGNORECASE,
    )
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try extracting first { ... } block
    brace_start = text_stripped.find("{")
    brace_end = text_stripped.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        candidate = text_stripped[brace_start : brace_end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"LLM returned invalid JSON. Extract error: {e}. "
                f"Raw snippet: {text[:400]}"
            )

    raise ValueError(
        f"Could not find JSON object in LLM response. Raw: {text[:500]}"
    )


# ─── Core: Chat Completion (Provider Agnostic) ───────────────────────────────

def chat_completion(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 4000,
    response_format: Optional[Dict] = None,
    max_retries: int = 3,
) -> str:
    """
    Call the active LLM provider and return the response text.
    Automatically retries on transient errors.
    """
    provider = _detect_provider()
    last_error: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            if provider == "gemini":
                return _gemini_chat(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    force_json=bool(response_format and response_format.get("type") == "json_object"),
                )
            elif provider == "openai":
                return _openai_chat(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                )
            else:
                raise ValueError(
                    "No LLM provider configured. Please set GOOGLE_API_KEY or OPENAI_API_KEY "
                    "in your .env file or enter it in the sidebar."
                )
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"[LLM:{provider}] Attempt {attempt} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)

    raise RuntimeError(
        f"LLM call ({provider}) failed after {max_retries} attempts. "
        f"Last error: {last_error}"
    )


def _gemini_chat(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    force_json: bool,
) -> str:
    """Call Google Gemini and return text response."""
    model = _get_gemini_model()

    # Build the generation config override for this call
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": max_tokens,
        "response_mime_type": "application/json" if force_json else "text/plain",
    }

    full_prompt = f"""SYSTEM INSTRUCTIONS:
{system_prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USER REQUEST:
{user_prompt}
"""
    if force_json:
        full_prompt += (
            "\n\nIMPORTANT: Return ONLY a valid JSON object. "
            "No markdown, no prose, no commentary. "
            "Start with { and end with }."
        )

    response = model.generate_content(
        full_prompt,
        generation_config=generation_config,
    )

    # Handle candidates / safety blocks
    if not response.candidates:
        raise RuntimeError("Gemini returned no candidates (possibly blocked by safety filters).")

    candidate = response.candidates[0]
    if hasattr(candidate, "finish_reason") and str(candidate.finish_reason) not in ("FinishReason.STOP", "1", "Stop"):
        finish = candidate.finish_reason
        text = (response.text or "") if hasattr(response, "text") else ""
        if finish not in ("FinishReason.STOP", "1", "Stop", "0") and len(text) < 50:
            raise RuntimeError(f"Gemini finished abnormally: reason={finish}, text={text[:200]}")

    text = response.text
    if not text or len(text.strip()) == 0:
        raise RuntimeError("Gemini returned empty text response.")
    return text


def _openai_chat(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    response_format: Optional[Dict],
) -> str:
    """Call OpenAI and return text response."""
    client = _get_openai_client()
    model = get_openai_model()

    kwargs: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format:
        kwargs["response_format"] = response_format

    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content or ""
    if not content:
        raise RuntimeError("OpenAI returned empty response content.")
    return content


# ─── Convenience: JSON Output ─────────────────────────────────────────────────

def chat_json(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 4000,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """
    Call the active LLM provider and parse the response as JSON.
    Forces JSON output via provider-native modes + robust fallback extraction.
    """
    provider = _detect_provider()
    response_format = {"type": "json_object"} if provider == "openai" else {"type": "json_object"}

    raw = chat_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_format,
        max_retries=max_retries,
    )

    return _extract_json(raw)


# ─── Status Checks ────────────────────────────────────────────────────────────

def is_any_api_key_configured() -> bool:
    """Return True if either Gemini or OpenAI API key is set."""
    gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    return (
        bool(gemini_key and gemini_key not in ("", "your_gemini_api_key_here"))
        or bool(openai_key and openai_key != "your_openai_api_key_here")
    )


def is_gemini_configured() -> bool:
    """Check if Gemini API key is properly configured."""
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
    return bool(key and key not in ("", "your_gemini_api_key_here"))


def is_openai_configured() -> bool:
    """Check if OpenAI API key is properly configured."""
    key = os.getenv("OPENAI_API_KEY", "")
    return bool(key and key != "your_openai_api_key_here")


def is_api_key_configured() -> bool:
    """Backwards-compatible alias for is_any_api_key_configured()."""
    return is_any_api_key_configured()


def get_active_model_display() -> str:
    """Human-readable string showing active provider + model."""
    provider = _detect_provider()
    if provider == "gemini":
        return f"Gemini ({get_gemini_model_name()})"
    elif provider == "openai":
        return f"OpenAI ({get_openai_model()})"
    return "Not configured"
