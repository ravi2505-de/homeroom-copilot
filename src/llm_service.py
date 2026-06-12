"""Local LLM service for generating text with llama.cpp.

The Qwen GGUF model is loaded lazily and cached globally so repeated calls
reuse the same llama.cpp instance instead of reloading model weights.
"""

from __future__ import annotations

import logging
import os
import time
import traceback
from typing import Any

import psutil
from llama_cpp import Llama


MODEL_REPO_ID = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
MODEL_FILENAME = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
TEMPERATURE = 0.2
MAX_TOKENS = 1024
N_CTX = 4096
N_GPU_LAYERS = -1
TOP_P = 0.9
TOP_K = 40
REPEAT_PENALTY = 1.12

_LLM: Any | None = None
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _memory_usage_mb() -> float:
    """Return current process resident memory in megabytes."""
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)


def get_llm() -> Any:
    """Return the singleton llama.cpp model, loading it if needed."""
    global _LLM

    if _LLM is None:
        try:
            logger.info("Model loading start: %s / %s", MODEL_REPO_ID, MODEL_FILENAME)
            memory_before = _memory_usage_mb()
            logger.info("Memory before model load: %.1f MB", memory_before)

            load_start = time.perf_counter()
            _LLM = Llama.from_pretrained(
                repo_id=MODEL_REPO_ID,
                filename=MODEL_FILENAME,
                n_gpu_layers=N_GPU_LAYERS,
                n_ctx=N_CTX,
                chat_format="chatml",
                verbose=True,
            )
            load_time = time.perf_counter() - load_start

            memory_after = _memory_usage_mb()
            logger.info("Model loading complete in %.2f seconds", load_time)
            logger.info("Memory after model load: %.1f MB", memory_after)
            logger.info("Model load memory delta: %.1f MB", memory_after - memory_before)
        except Exception as error:
            traceback.print_exc()
            raise RuntimeError(f"Failed to load LLM model: {error}") from error

    return _LLM


def generate_text(prompt: str) -> str:
    """Generate text from a prompt using the singleton Qwen GGUF model."""
    try:
        llm = get_llm()
        logger.info("Generation start")
        logger.info("Prompt length: %s characters", len(prompt))

        memory_before = _memory_usage_mb()
        generation_start = time.perf_counter()
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            repeat_penalty=REPEAT_PENALTY,
            max_tokens=MAX_TOKENS,
        )
        generation_time = time.perf_counter() - generation_start
        memory_after = _memory_usage_mb()

        logger.info("Generation complete in %.2f seconds", generation_time)
        logger.info("Memory before generation: %.1f MB", memory_before)
        logger.info("Memory after generation: %.1f MB", memory_after)
        logger.info("Generation memory delta: %.1f MB", memory_after - memory_before)

        choices = response.get("choices", [])
        if not choices:
            return ""

        message = choices[0].get("message", {})
        return str(message.get("content", "")).strip()

    except Exception as error:
        traceback.print_exc()
        raise RuntimeError(f"Failed to generate text: {error}") from error
