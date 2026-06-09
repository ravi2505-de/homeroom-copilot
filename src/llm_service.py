"""Local LLM service for generating text with Hugging Face Transformers.

The model and tokenizer are loaded lazily and cached globally so repeated calls
reuse the same Qwen instance instead of reloading model weights.
"""

from __future__ import annotations

import logging
import time
import traceback
from typing import Any

import spaces
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
TEMPERATURE = 0.2
MAX_NEW_TOKENS = 1024

_TOKENIZER: Any | None = None
_MODEL: Any | None = None
logger = logging.getLogger(__name__)


def get_llm() -> tuple[Any, Any]:
    """Return the singleton tokenizer and model, loading them if needed."""
    global _TOKENIZER, _MODEL

    if _TOKENIZER is None or _MODEL is None:
        try:
            logger.info("Model loading start: %s", MODEL_NAME)
            load_start = time.perf_counter()

            _TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)
            _MODEL = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                torch_dtype="auto",
                device_map="auto",
            )

            load_time = time.perf_counter() - load_start
            logger.info("Model loading complete in %.2f seconds", load_time)
        except Exception as error:
            traceback.print_exc()
            raise RuntimeError(f"Failed to load LLM model: {error}") from error

    return _TOKENIZER, _MODEL


@spaces.GPU
def generate_text(prompt: str) -> str:
    """Generate text from a prompt using the singleton Qwen model."""
    try:
        tokenizer, model = get_llm()
        logger.info("Generation start")
        logger.info("Prompt length: %s characters", len(prompt))

        generation_start = time.perf_counter()
        messages = [{"role": "user", "content": prompt}]
        model_prompt = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
        )
        inputs = tokenizer(model_prompt, return_tensors="pt").to(model.device)

        generated_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            do_sample=False,
        )

        input_token_count = inputs["input_ids"].shape[-1]
        new_token_ids = generated_ids[0][input_token_count:]
        generated_text = tokenizer.decode(
            new_token_ids,
            skip_special_tokens=True,
        )

        total_generation_time = time.perf_counter() - generation_start
        logger.info("Generation complete in %.2f seconds", total_generation_time)
        return generated_text.strip()

    except Exception as error:
        traceback.print_exc()
        raise RuntimeError(f"Failed to generate text: {error}") from error
