"""Local LLM service for generating text with llama-cpp-python.

The model is loaded lazily and cached globally so repeated calls reuse the same
Llama instance instead of reloading the GGUF file.
"""

from __future__ import annotations

import logging
import time
import traceback
from collections.abc import Iterator
from typing import Any

from llama_cpp import Llama


MODEL_PATH = "models/qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf"
N_CTX = 4096
TEMPERATURE = 0.2
MAX_TOKENS = 400

_LLM: Llama | None = None
logger = logging.getLogger(__name__)


def get_llm() -> Llama:
    """Return the singleton Llama model instance, loading it if needed."""
    global _LLM

    if _LLM is None:
        try:
            _LLM = Llama(
                model_path=MODEL_PATH,
                n_ctx=N_CTX,
            )
        except Exception as error:
            traceback.print_exc()
            raise RuntimeError(f"Failed to load LLM model: {error}") from error

    return _LLM


def _stream_chat_completion(llm: Llama, prompt: str) -> Iterator[dict[str, Any]]:
    """Yield chat completion chunks.

    This helper keeps the generation path ready for future UI streaming while
    generate_text still returns one complete string.
    """
    response = llm.create_chat_completion(
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        stream=True,
    )
    yield from response


def _chunk_text(chunk: dict[str, Any]) -> str:
    """Extract generated text from a llama-cpp streaming chat chunk."""
    choices = chunk.get("choices") or []
    if not choices:
        return ""

    choice = choices[0]
    delta = choice.get("delta") or {}
    message = choice.get("message") or {}
    return str(delta.get("content") or message.get("content") or "")


def generate_text(prompt: str) -> str:
    """Generate text from a prompt using the local singleton LLM."""
    try:
        llm = get_llm()
        logger.info("Prompt length: %s characters", len(prompt))

        generation_start = time.perf_counter()
        first_token_time: float | None = None
        generated_parts: list[str] = []

        for chunk in _stream_chat_completion(llm, prompt):
            text = _chunk_text(chunk)
            if text and first_token_time is None:
                first_token_time = time.perf_counter() - generation_start
                logger.info(
                    "First token generation time: %.2f seconds",
                    first_token_time,
                )
            if text:
                generated_parts.append(text)

        total_generation_time = time.perf_counter() - generation_start
        if first_token_time is None:
            logger.info("First token generation time: no token generated")
        logger.info("Total generation time: %.2f seconds", total_generation_time)

        return "".join(generated_parts).strip()

    except Exception as error:
        traceback.print_exc()
        raise RuntimeError(f"Failed to generate text: {error}") from error
