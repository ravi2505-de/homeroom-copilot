"""Prompt construction utilities for teacher-facing student action plans.

This module prepares structured context for an external language model such as
Qwen 2.5 7B. It does not load models, call model runtimes, or perform text
generation directly.
"""

from __future__ import annotations

from typing import Any


PROMPT_ROLE = (
    "You are an experienced school intervention specialist and student success "
    "coordinator."
)


def _format_list(value: Any) -> str:
    """Format a scalar or list-like value as prompt-friendly bullet points."""
    if value is None:
        return "- Not provided"

    if isinstance(value, (list, tuple, set)):
        items = [str(item).strip() for item in value if str(item).strip()]
    else:
        text = str(value).strip()
        items = [text] if text else []

    if not items:
        return "- Not provided"

    return "\n".join(f"- {item}" for item in items)


def _format_mapping(mapping: dict[str, Any]) -> str:
    """Format dictionary values as a compact bullet list."""
    if not mapping:
        return "- Not provided"

    lines = []
    for key, value in mapping.items():
        label = key.replace("_", " ").title()
        lines.append(f"- {label}: {value}")
    return "\n".join(lines)


def format_intervention_context(intervention: dict) -> str:
    """Format one retrieved intervention as structured prompt context.

    The formatted context includes only fields supplied by the intervention
    knowledge base and leaves missing values clearly marked as not provided.
    """
    rank = intervention.get("recommendation_rank", "Not provided")

    return f"""Recommendation Rank: {rank}
Intervention Name: {intervention.get("intervention_name", "Not provided")}
Category: {intervention.get("category", "Not provided")}
Summary:
{_format_list(intervention.get("summary"))}
Expected Benefits:
{_format_list(intervention.get("expected_benefits"))}
Recommendation Reason Template:
{intervention.get("recommendation_reason_template", "Not provided")}
Primary Targets:
{_format_list(intervention.get("primary_targets"))}
Secondary Targets:
{_format_list(intervention.get("secondary_targets"))}
Mitigates:
{_format_list(intervention.get("mitigates"))}
Evidence Level: {intervention.get("evidence_level", "Not provided")}"""


def build_action_plan_prompt(
    student_name: str,
    risk_profile: dict,
    root_causes: list[str],
    recommended_interventions: list[dict],
) -> str:
    """Build a structured prompt for generating a student action plan.

    The prompt instructs the model to use only supplied information, avoid
    unsupported medical or psychological claims, and produce a concise
    teacher-facing action plan tied to retrieved interventions.
    """
    overall_risk = risk_profile.get("overall_risk", "Not provided")

    intervention_context = "\n\n".join(
        format_intervention_context(
            {**intervention, "recommendation_rank": rank}
        )
        for rank, intervention in enumerate(recommended_interventions, start=1)
    )

    if not intervention_context:
        intervention_context = "No retrieved interventions were provided."

    return f"""{PROMPT_ROLE}

============================================================
Student Information
============================================================

Student Name:
{student_name}

Overall Risk Level:
{overall_risk}

============================================================
Risk Profile:
============================================================
{_format_mapping(risk_profile)}

============================================================
Root Cause Analysis:
============================================================
{_format_list(root_causes)}

============================================================
Retrieved Intervention Context:
============================================================
The interventions below are listed in ranked order. Recommendation Rank 1 is
the highest-priority retrieved intervention.

{intervention_context}

============================================================
Generation Instructions:
============================================================
- Use only the supplied student information, risk profile, root causes, and
  retrieved intervention context.
- The action plan must use only the retrieved interventions.
- Do not recommend interventions that are not present in the supplied
  intervention context.
- Do not invent additional programs, services, referrals, therapies,
  counseling plans, or support mechanisms.
- Do not invent diagnoses, psychological conditions, medical conditions, or
  unsupported claims.
- Focus only on educational interventions.
- Write for classroom teachers, homeroom teachers, and school staff.
- Actions must be realistic, practical, and implementable in a school setting.
- Avoid generic motivational language.
- Avoid vague recommendations.
- Explicitly connect actions to retrieved interventions using wording such as
  "Based on Family Engagement..." or "Using Mentoring/Tutoring..."
- Prefer concise bullet points over paragraphs.
- Produce valid Markdown.
- Use exactly the headings below and do not create additional sections.

Required Markdown Output:

# Student Action Plan

## Student Summary

## Primary Concerns

## Immediate Actions (Next 7 Days)

## Short-Term Actions (2-4 Weeks)

## Monitoring Plan

## Expected Outcomes

## Teacher Notes

Style requirements:
- Use concise professional language.
- Prefer bullet points.
- Avoid long paragraphs.
- Avoid generic motivational advice.
- Tie recommendations directly to the retrieved interventions.
- Keep the plan practical for a teacher to implement."""
