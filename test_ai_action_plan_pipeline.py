"""End-to-end smoke test for the AI action-plan pipeline.

Run this from the Python 3.11 environment that has Gradio, pandas,
llama-cpp-python, and the local Qwen GGUF model available.
"""

from __future__ import annotations

import time
import traceback
from typing import Any


def main() -> None:
    """Run one student through the full AI action-plan pipeline."""
    try:
        import app
        import src.llm_service as llm_service

        student_record = app.STUDENTS.iloc[0]
        student_name = str(student_record["student_name"])

        timings: dict[str, float] = {
            "retrieve_interventions": 0.0,
            "build_prompt": 0.0,
            "generate_with_qwen": 0.0,
        }
        captured: dict[str, Any] = {
            "interventions": [],
            "prompt": "",
            "first_token_latency": None,
            "raw_model_output": "",
        }

        original_load_intervention_library = app.load_intervention_library
        original_recommend_interventions = app.recommend_interventions
        original_build_action_plan_prompt = app.build_action_plan_prompt
        original_generate_text = llm_service.generate_text

        def timed_load_intervention_library(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                return original_load_intervention_library(*args, **kwargs)
            finally:
                timings["retrieve_interventions"] += time.perf_counter() - start

        def timed_recommend_interventions(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                recommendations = original_recommend_interventions(*args, **kwargs)
                captured["interventions"] = recommendations
                return recommendations
            finally:
                timings["retrieve_interventions"] += time.perf_counter() - start

        def timed_build_action_plan_prompt(*args: Any, **kwargs: Any) -> str:
            start = time.perf_counter()
            try:
                prompt = original_build_action_plan_prompt(*args, **kwargs)
                captured["prompt"] = prompt
                return prompt
            finally:
                timings["build_prompt"] += time.perf_counter() - start

        def timed_generate_text(prompt: str) -> str:
            start = time.perf_counter()
            try:
                generated_text = original_generate_text(prompt)
                captured["raw_model_output"] = generated_text
                return generated_text
            finally:
                timings["generate_with_qwen"] += time.perf_counter() - start

        app.load_intervention_library = timed_load_intervention_library
        app.recommend_interventions = timed_recommend_interventions
        app.build_action_plan_prompt = timed_build_action_plan_prompt
        llm_service.generate_text = timed_generate_text

        risk_profile = app.student_risk_profile(student_record)
        root_causes = app.student_root_causes(student_record)

        total_start = time.perf_counter()
        action_plan = app.generate_ai_action_plan(student_record)
        total_pipeline_time = time.perf_counter() - total_start

        print("=" * 72)
        print("AI Action Plan Pipeline Test")
        print("=" * 72)
        print(f"Student name: {student_name}")

        print("\nRisk profile:")
        for key, value in risk_profile.items():
            print(f"- {key}: {value}")

        print("\nRoot causes:")
        for root_cause in root_causes:
            print(f"- {root_cause}")

        print("\nRetrieved interventions:")
        for index, intervention in enumerate(captured["interventions"], start=1):
            print(
                f"{index}. {intervention.intervention_name} "
                f"({intervention.category}) "
                f"- score {intervention.relevance_score}"
            )

        print("\nTiming:")
        print(
            f"- Time to retrieve interventions: "
            f"{timings['retrieve_interventions']:.2f}s"
        )
        print(f"- Time to build prompt: {timings['build_prompt']:.2f}s")
        print(
            f"- Time to generate with Qwen: "
            f"{timings['generate_with_qwen']:.2f}s"
        )
        print(f"- Total pipeline time: {total_pipeline_time:.2f}s")

        prompt = str(captured["prompt"])
        prompt_token_estimate = len(prompt) // 4
        raw_model_output = str(captured["raw_model_output"])
        response_token_estimate = len(raw_model_output) // 4
        first_token_latency = captured["first_token_latency"]

        print("\nDiagnostics:")
        print(f"- Prompt character length: {len(prompt)}")
        print(f"- Approximate prompt token count: {prompt_token_estimate}")
        print(f"- Generated response character length: {len(raw_model_output)}")
        print(
            f"- Generated response token count estimate: "
            f"{response_token_estimate}"
        )
        if first_token_latency is None:
            print("- First token latency: unavailable from generate_text()")
        else:
            print(f"- First token latency: {first_token_latency:.2f}s")
        print(f"- Total generation time: {timings['generate_with_qwen']:.2f}s")

        print("\n" + "=" * 60)
        print("FULL RAW MODEL OUTPUT")
        print("=" * 21)
        print()
        print(raw_model_output)
        print()
        print("=" * 60)
        print("END RAW MODEL OUTPUT")
        print("=" * 20)

        print("\n" + "=" * 60)
        print("FULL CLEANED ACTION PLAN")
        print("=" * 26)
        print()
        print(action_plan)
        print()
        print("=" * 60)
        print("END CLEANED ACTION PLAN")
        print("=" * 23)

    except Exception as error:
        print("AI action-plan pipeline test failed:")
        print(repr(error))
        traceback.print_exc()


if __name__ == "__main__":
    main()
