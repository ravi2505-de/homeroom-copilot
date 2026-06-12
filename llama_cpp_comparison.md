# Homeroom Copilot LLM Runtime Comparison

Branch: `homeroom-llama.cpp`

Deployment target: `ravi2505/llama-experiment`

This report compares the existing Transformers-based Qwen runtime with the
llama.cpp GGUF runtime used by this experiment branch. The application workflow,
prompt templates, retrieval logic, risk scoring, root-cause analysis, evaluation
artifacts, and UI are intentionally unchanged.

## Runtime Configurations

| Runtime | Model | Backend | GPU Strategy |
|---|---|---|---|
| Transformers baseline | `Qwen/Qwen2.5-1.5B-Instruct` | `transformers` + `torch` | `device_map="auto"` |
| llama.cpp experiment | `Qwen/Qwen2.5-1.5B-Instruct-GGUF` / `qwen2.5-1.5b-instruct-q4_k_m.gguf` | `llama-cpp-python==0.3.28` | `n_gpu_layers=-1` |

## Side-by-Side Metrics

| Metric | Transformers Version | llama.cpp Version |
|---|---:|---:|
| Model load time | Pending baseline log capture | Pending HF Space log capture |
| Generation latency | Pending baseline log capture | Pending HF Space log capture |
| Memory before load | Pending baseline log capture | Logged as `Memory before model load` |
| Memory after load | Pending baseline log capture | Logged as `Memory after model load` |
| Memory delta | Pending baseline log capture | Logged as `Model load memory delta` |

## llama.cpp Logging Added

The experiment runtime logs:

- Model loading start
- Model load time
- Memory usage before model load
- Memory usage after model load
- Model load memory delta
- Generation start
- Prompt length
- Generation latency
- Memory usage before generation
- Memory usage after generation
- Generation memory delta

## Deployment Notes

The expected successful llama.cpp GPU indicators in Hugging Face logs are:

- CUDA-enabled `llama-cpp-python` wheel installs from the `cu124` index.
- llama.cpp reports CUDA buffers.
- llama.cpp reports model layers offloaded to GPU.
- KV cache layers are assigned to `CUDA0`.

## Status

This report should be updated after the `ravi2505/llama-experiment` Space
finishes building and a representative action plan generation is tested.
