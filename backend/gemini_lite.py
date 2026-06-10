"""
gemini_lite.py

Lightweight Gemini API client using REST API directly.
Replaces the heavy google-generativeai SDK (~150MB with grpcio/protobuf)
for Vercel serverless deployment where bundle size is limited to 250MB.
"""

import json
import logging
import base64
from typing import Any, Dict, List, Optional

import asyncio
import requests  # type: ignore  # type: ignore

logger = logging.getLogger(__name__)

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiLiteModel:
    """Lightweight wrapper for Google Gemini REST API."""

    def __init__(self, api_key: str, model_name: str = "gemini-flash-latest",
                 system_instruction: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name
        self.system_instruction = system_instruction

    def generate_content(
        self,
        content_parts: List[Any],
        generation_config: Optional[Dict[str, Any]] = None,
    ) -> "GeminiLiteResponse":
        """Generate content using Gemini REST API."""
        url = (
            f"{GEMINI_API_BASE}/models/{self.model_name}:generateContent"
            f"?key={self.api_key}"
        )

        # Build parts
        parts: List[Dict[str, Any]] = []
        for part in content_parts:
            if isinstance(part, str):
                parts.append({"text": part})
            elif isinstance(part, dict):
                # Inline data (PDF, image, etc.)
                mime_type = part.get("mime_type", "application/octet-stream")
                data = part.get("data", b"")
                if isinstance(data, bytes):
                    data = base64.standard_b64encode(data).decode("utf-8")
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": data,
                    }
                })

        payload: Dict[str, Any] = {
            "contents": [{"parts": parts}],
        }

        if self.system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": self.system_instruction}]
            }

        # Use local variable to satisfy strict type checker
        gen_config: Dict[str, Any] = generation_config if generation_config is not None else {}  # type: ignore

        if gen_config:
            gc: Dict[str, Any] = {}
            if gen_config.get("temperature") is not None:
                gc["temperature"] = gen_config["temperature"]
            if gen_config.get("max_output_tokens") is not None:
                gc["maxOutputTokens"] = gen_config["max_output_tokens"]
            if gen_config.get("response_mime_type") is not None:
                gc["responseMimeType"] = gen_config["response_mime_type"]
            if gen_config.get("thinking_budget") is not None:
                # Los modelos 2.5 reservan parte de maxOutputTokens para "thinking".
                # Para extracción/formato JSON estructurado no lo necesitamos: si no
                # se desactiva, el JSON puede truncarse (MAX_TOKENS) antes de cerrarse.
                gc["thinkingConfig"] = {"thinkingBudget": gen_config["thinking_budget"]}
            if gc:
                payload["generationConfig"] = gc

        logger.info("Calling Gemini REST API: model=%s", self.model_name)
        resp = requests.post(url, json=payload, timeout=120)

        if resp.status_code != 200:
            error_msg = resp.text[:500]
            logger.error("Gemini API error %d: %s", resp.status_code, error_msg)
            raise Exception(f"Gemini API error {resp.status_code}: {error_msg}")

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise Exception("Gemini returned no candidates")

        text = ""
        first_candidate = candidates[0]
        content = first_candidate.get("content", {})
        for p in content.get("parts", []):
            text += p.get("text", "")

        if not text.strip():
            finish_reason = first_candidate.get("finishReason", "UNKNOWN")
            raise Exception(
                f"Gemini devolvió respuesta vacía (finishReason={finish_reason})"
            )

        return GeminiLiteResponse(text=text)

    async def generate_content_async(
        self,
        content_parts: List[Any],
        generation_config: Optional[Dict[str, Any]] = None,
    ) -> "GeminiLiteResponse":
        """Async wrapper for generate_content."""
        return await asyncio.to_thread(
            self.generate_content, content_parts, generation_config  # type: ignore
        )


class GeminiLiteResponse:
    """Simple response wrapper compatible with google-generativeai interface."""

    def __init__(self, text: str):
        self._text = text

    @property
    def text(self) -> str:
        return self._text


class GeminiLiteConfig:
    """Replaces genai.types.GenerationConfig."""

    def __init__(self, temperature: float = 0.1, max_output_tokens: int = 8000,
                 response_mime_type: str = "application/json",
                 thinking_budget: Optional[int] = None):
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.response_mime_type = response_mime_type
        self.thinking_budget = thinking_budget

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "response_mime_type": self.response_mime_type,
            "thinking_budget": self.thinking_budget,
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Allow dict-like access."""
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
             raise KeyError(key)


# Module-level API mimicking google.generativeai interface
_api_key: Optional[str] = None


def configure(api_key: str) -> None:
    global _api_key
    _api_key = api_key


def GenerativeModel(model_name: str, system_instruction: Optional[str] = None) -> GeminiLiteModel:
    if not _api_key:
        raise ValueError("Gemini API key not configured. Call gemini_lite.configure(api_key=...) first.")
    return GeminiLiteModel(
        api_key=_api_key,
        model_name=model_name,
        system_instruction=system_instruction,
    )


class types:
    """Namespace for compatibility with genai.types."""
    GenerationConfig = GeminiLiteConfig
