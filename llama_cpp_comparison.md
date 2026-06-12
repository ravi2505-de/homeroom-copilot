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

## Output Quality Investigation

After the first llama.cpp deployment, generated plans were fast but weaker than
the Transformers version. Observed issues included repeated monitoring
sentences, generic week-by-week plans, and weak use of retrieved evidence.

### Findings

| Area Checked | Finding |
|---|---|
| Prompt fidelity | The llama.cpp branch initially used the same `build_action_plan_prompt()` template as `transformers-zerogpu`. The prompt was not missing from the pipeline. |
| Intervention evidence | The prompt formatter was only passing intervention rank, name, and category. It discarded summaries and expected benefits that were already available from retrieval. |
| Source selection | Cleanup always fell back to all retrieved sources, which made `Sources Used` look like every intervention was used even when the model should select fewer. |
| Chat formatting | llama.cpp was relying on automatic chat formatting. Qwen GGUF should use ChatML-style role formatting explicitly. |
| Repetition control | The first llama.cpp generation settings did not include `top_p`, `top_k`, or `repeat_penalty`, which likely contributed to repeated monitoring language. |

### Adjustments Made

- Preserved the same public action-plan pipeline and output format.
- Added intervention `summary` and `expected_benefits` back into the prompt
  context so Qwen has concrete evidence to plan from.
- Added stronger action instructions for specific educator tasks, measurable
  supports, and week-to-week progression.
- Set llama.cpp `chat_format="chatml"` for Qwen GGUF.
- Added `top_p=0.9`, `top_k=40`, and `repeat_penalty=1.12`.
- Updated source cleanup so `Sources Used` reflects selected/generated sources
  when available, while preserving links back to retrieved evidence.

## Second Quality Pass

User comparison against the Transformers baseline showed that llama.cpp was
still producing actions that were too generic, such as:

- "Establish regular communication with parents or guardians."
- "Provide one-to-one mentoring or tutoring support."
- "Continue Monitoring."

These were valid intervention labels but not implementation plans.

Additional corrections:

- Added concrete implementation ideas for each retrieved intervention type.
- Added weak-vs-better examples directly in the prompt.
- Added rules requiring each action to include a concrete routine, goal,
  actor, or progress-check method.
- Added cleanup replacements for the exact weak phrases observed in llama.cpp
  outputs.
- Increased llama.cpp temperature from `0.2` to `0.35`.
- Increased repeat penalty from `1.12` to `1.18`.
