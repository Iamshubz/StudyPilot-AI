"""agent/llm_client.py - Groq API Client Wrapper for StudyPilot AI.

Handles client initialization, environment variable resolution, model fallback,
conversational context trimming, and comprehensive error categorization without
leaking sensitive credentials.
"""

import os
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

# Default Groq Models
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
SUPPORTED_MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
]
FALLBACK_MODEL = "openai/gpt-oss-20b"

# Max conversation messages to keep in sliding window to protect context limits
MAX_CONTEXT_MESSAGES = 10


def get_effective_api_key(explicit_key: Optional[str] = None) -> Optional[str]:
    """Resolves the Groq API key in order of precedence:

    1. Explicit key provided in backend config
    2. OS Environment variable GROQ_API_KEY
    3. Streamlit secrets (if running in Streamlit cloud)
    """
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()

    env_key = os.getenv("GROQ_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            sec_key = st.secrets["GROQ_API_KEY"]
            if sec_key and sec_key.strip():
                return sec_key.strip()
    except Exception:
        pass

    return None


def mask_api_key(key: Optional[str]) -> str:
    """Safely masks an API key for UI display (e.g., gsk_...a1b2)."""
    if not key:
        return "Not Configured"
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


class GroqClientManager:
    """Manages connections to Groq API with error handling and fallback."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = get_effective_api_key(api_key)
        self.model = model or os.getenv("GROQ_MODEL", DEFAULT_MODEL)
        self._client = None

    def is_configured(self) -> bool:
        """Checks if a valid API key string is present."""
        return bool(self.api_key and len(self.api_key) > 5)

    def _get_client(self):
        """Lazy-initializes official Groq client."""
        if not self.is_configured():
            raise ValueError(
                "Groq API Key is missing. Please set GROQ_API_KEY in your server backend .env file "
                "or Streamlit secrets."
            )
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key, timeout=30.0)
            except ImportError:
                raise ImportError(
                    "The official 'groq' package is not installed. Run 'pip install groq'."
                )
        return self._client

    def verify_connection(self) -> Tuple[bool, str]:
        """Tests API key validity by querying available models or a tiny prompt."""
        if not self.is_configured():
            return False, "No API key configured."
        try:
            client = self._get_client()
            # Perform a lightweight call to check credentials
            models_response = client.models.list()
            return True, f"Connected to Groq API successfully. Available models: {len(models_response.data)}"
        except Exception as e:
            err_msg = self._format_error(e)
            return False, err_msg

    def _format_error(self, exc: Exception) -> str:
        """Translates technical API exceptions into student-friendly explanations."""
        err_type = type(exc).__name__
        err_str = str(exc).lower()

        if "authenticationerror" in err_type.lower() or "invalid api key" in err_str or "401" in err_str:
            return (
                "Authentication Error: The backend Groq API key is invalid or expired. "
                "Please verify your key at https://console.groq.com/keys and update the server configuration."
            )
        if "ratelimiterror" in err_type.lower() or "429" in err_str:
            return (
                "Rate Limit Exceeded: Groq API request rate or token quota reached. "
                "Please wait 30-60 seconds before retrying or use the Safe Calculator tool."
            )
        if "notfounderror" in err_type.lower() or "model_not_found" in err_str or "404" in err_str:
            return (
                f"Model Error: The model '{self.model}' is currently unavailable on Groq. "
                f"Configuring GROQ_MODEL='{FALLBACK_MODEL}' in .env is recommended."
            )
        if "timeout" in err_str or "apiconnectionerror" in err_type.lower():
            return (
                "Network Timeout: Could not reach Groq servers. "
                "Please check your internet connection and verify that outbound HTTPS requests are permitted."
            )
        return f"Groq API Error ({err_type}): {str(exc)}"

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        max_tokens: int = 2048,
        model_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sends a conversation history to Groq and returns the text response."""
        client = self._get_client()
        active_model = model_override or self.model

        # Ensure sliding window limit on messages to avoid token blowup
        # Always retain system prompt at index 0 if present
        trimmed_messages = self._trim_messages(messages, MAX_CONTEXT_MESSAGES)

        try:
            response = client.chat.completions.create(
                model=active_model,
                messages=trimmed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as first_error:
            first_error_text = str(first_error).lower()
            is_model_error = (
                "model_not_found" in first_error_text
                or "model does not exist" in first_error_text
                or "404" in first_error_text
            )
            if not is_model_error or active_model == FALLBACK_MODEL:
                return {
                    "success": False,
                    "content": None,
                    "model": active_model,
                    "usage": None,
                    "error": self._format_error(first_error),
                }

            active_model = FALLBACK_MODEL
            try:
                response = client.chat.completions.create(
                    model=active_model,
                    messages=trimmed_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception as fallback_error:
                return {
                    "success": False,
                    "content": None,
                    "model": active_model,
                    "usage": None,
                    "error": self._format_error(fallback_error),
                }

        try:
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                "total_tokens": getattr(response.usage, "total_tokens", 0),
            }
            return {
                "success": True,
                "content": content,
                "model": active_model,
                "usage": usage,
                "error": None,
            }
        except Exception as e:
            return {
                "success": False,
                "content": None,
                "model": active_model,
                "usage": None,
                "error": self._format_error(e),
            }

    @staticmethod
    def _trim_messages(messages: List[Dict[str, str]], max_history: int) -> List[Dict[str, str]]:
        """Ensures system prompt is kept while sliding window limits older messages."""
        if len(messages) <= max_history:
            return messages

        system_msgs = [m for m in messages if m.get("role") == "system"]
        chat_msgs = [m for m in messages if m.get("role") != "system"]

        # Keep the most recent messages
        recent_chat = chat_msgs[-max_history:]
        return system_msgs + recent_chat
