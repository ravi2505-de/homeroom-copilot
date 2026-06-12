"""Prompt construction utilities for teacher-facing student action plans.

This module prepares structured context for an external language model such as
Qwen 2.5 7B. It does not load models, call model runtimes, or perform text
generation directly.
"""

from __future__ import annotations

import logging
import re
from typing import Any


PROMPT_ROLE = (
    "You are an experienced school intervention specialist and student success "
    "coordinator."
)


def _implementation_guidance(intervention_name: str) -> list[str]:
    """Return concrete implementation ideas for a retrieved intervention."""
    normalized_name = intervention_name.lower()

    if "continue monitoring" in normalized_name:
        return [
            "Review attendance, homework, engagement, and behavior records once per week.",
            "Give brief positive feedback when the student maintains current performance.",
            "Escalate only if a monitored indicator declines during the next reporting cycle.",
        ]

    if "family engagement" in normalized_name:
        return [
            "Schedule a family check-in and agree on one attendance or homework goal.",
            "Set a weekly update routine so home and school use the same expectations.",
            "Review progress with the family before adjusting supports.",
        ]

    if "mentoring" in normalized_name or "tutoring" in normalized_name:
        return [
            "Assign a mentor or tutor for a weekly check-in.",
            "Use the session to review missing assignments and practice one priority skill.",
            "Track whether the student completes agreed follow-up work before the next meeting.",
        ]

    if "individualized instruction" in normalized_name:
        return [
            "Identify one priority skill gap from recent classwork.",
            "Provide a short targeted practice routine with clear success criteria.",
            "Adjust instruction after reviewing the student's work sample or assessment result.",
        ]

    if "after-school" in normalized_name:
        return [
            "Connect the student with a structured after-school or lunch support opportunity.",
            "Use the time for assignment completion, guided practice, or engagement-building activities.",
            "Confirm attendance and follow through with the student after each support session.",
        ]

    if "active learning" in normalized_name:
        return [
            "Use a collaborative or problem-solving classroom activity tied to current coursework.",
            "Assign a defined participation role so engagement is observable.",
            "Review participation and adjust the activity structure the following week.",
        ]

    return [
        "Convert this intervention into a specific school-based action.",
        "Include a follow-up step and a simple way to monitor progress.",
    ]


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
    intervention_name = str(intervention.get("intervention_name", "Not provided"))

    return f"""Recommendation Rank: {rank}
Intervention Name: {intervention_name}
Category: {intervention.get("category", "Not provided")}
Summary:
{_format_list(intervention.get("summary"))}
Expected Benefits:
{_format_list(intervention.get("expected_benefits"))}
Concrete Implementation Ideas:
{_format_list(_implementation_guidance(intervention_name))}"""


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
    overall_risk = str(risk_profile.get("overall_risk", "Not provided"))

    intervention_context = "\n\n".join(
        format_intervention_context(
            {**intervention, "recommendation_rank": rank}
        )
        for rank, intervention in enumerate(recommended_interventions, start=1)
    )

    if not intervention_context:
        intervention_context = "No retrieved interventions were provided."

    return f"""You are a school intervention coordinator.

You are provided:
- Student risk information
- Root cause analysis
- Retrieved intervention recommendations

Student: {student_name}
Overall Risk Level: {overall_risk}

Internal risk context:
{_format_mapping(risk_profile)}

Internal root cause context:
{_format_list(root_causes)}

Retrieved intervention options:
{intervention_context}

The teacher already has access to all analysis.

Do NOT repeat:
- Risk levels
- Risk scores
- Attendance percentages
- Academic scores
- Homework statistics
- Behavior summaries
- Root causes
- Intervention explanations
- Intervention rationale

Your responsibility is ONLY to create a practical weekly implementation plan.

PLANNING REQUIREMENTS
- Treat retrieved interventions as available options, not a checklist.
- Select only the interventions needed for the student's risk level and root
  causes.
- Do not accumulate interventions just because they were retrieved.
- Do not restate intervention descriptions.
- Do not convert intervention names directly into action items.
- Determine which actions should happen first.
- Determine which actions should continue across multiple weeks.
- Determine which actions should happen later.
- Create a realistic school implementation schedule.

RISK-BASED PLANNING
Low Risk:
- Monitoring, maintenance, and positive reinforcement only.
- Maximum 1 action per week.
- Do not recommend tutoring, mentoring, family meetings, after-school programs,
  or behavior supports unless they are explicitly justified by the supplied
  evidence.
- If the only retrieved intervention is Continue Monitoring, use only Continue
  Monitoring.
- Do not escalate support for stable trends, no incidents, or positive teacher
  observations.

Moderate Risk:
- Light targeted support.
- Select at most 1-2 retrieved interventions.
- Avoid intervention accumulation.
- If trends are stable, emphasize monitoring and prevention.
- Use 1-2 actions per week.

High Risk:
- Structured intervention plan.
- Multiple coordinated actions.
- Up to 2 actions per week.

Critical Risk:
- Intensive intervention plan.
- Immediate support actions.
- Family-school coordination.
- Weekly progress reviews.
- Up to 2 actions per week.

ACTION RULES
Actions must:
- Be realistic for teachers and school staff.
- Be achievable in a school environment.
- Build logically from week to week.
- Include follow-up activities.
- Include monitoring activities.
- Use details from the retrieved intervention summaries and expected benefits.
- Translate intervention options into concrete educator tasks.
- Use the Concrete Implementation Ideas to create a schedule, but do not copy
  them word-for-word.
- Include specific routines, check-ins, goals, or measurable classroom supports
  when the retrieved evidence supports them.
- Stay proportional to the student's overall risk level.
- Treat stable trends as monitoring signals, not intervention triggers.
- Treat "No incidents" as a positive behavior signal, not a behavior concern.
- Treat positive teacher observations as strengths, not intervention triggers.
- For High and Critical Risk students, do not repeat generic monitoring across
  weeks. Each week must add, continue, review, or adjust a specific support.
- Every action must include at least one concrete detail such as who will act,
  what routine will be used, what goal will be set, or how progress will be
  checked.

Do NOT:
- Invent diagnoses.
- Invent therapies.
- Invent medical recommendations.
- Invent counseling plans.
- Invent external services.
- Invent programs that were not retrieved.
- Copy intervention summaries as action items.
- Write generic actions such as "Continue monitoring" unless the action also
  names what will be monitored and how the teacher will respond.

REQUIRED OUTPUT FORMAT

# Action Plan

## Week 1

* Specific educator action sentence
* Optional second action sentence only if justified by risk level

## Week 2

* Specific educator action sentence that builds on Week 1
* Optional second action sentence only if justified by risk level

## Week 3

* Specific educator action sentence focused on monitoring and adjustment
* Optional second action sentence only if justified by risk level

## Week 4

* Specific educator action sentence focused on review and next steps
* Optional second action sentence only if justified by risk level

## Sources Used

* Selected intervention actually used

OUTPUT RULES
- Generate only the sections above.
- Start directly with "# Action Plan".
- Do not create additional headings.
- Do not generate summaries.
- Do not generate assessments.
- Do not generate rationale sections.
- Do not explain intervention selection.
- Do not write "Source Used" or "Sources Used" inside Week 1-4.
- Sources Used must contain only intervention names actually used in the plan.
- The Week sections must contain action sentences, not intervention names.
- Do not use "Action:" labels.
- Use a maximum of 1 action per week for Low Risk.
- Use a maximum of 2 actions per week for Moderate, High, and Critical Risk.
- Avoid repeating the same monitoring sentence across multiple weeks.
- Use retrieved intervention details to make actions specific and personalized.
- Do not start an action with the intervention name.
- Do not write only a strategy label such as "Continue Monitoring",
  "Family Engagement", "Mentoring/Tutoring", or "Active Learning".
- For family engagement, include a concrete communication goal or follow-up.
- For tutoring or individualized instruction, include a concrete academic
  support routine.
- For after-school or active learning strategies, include a concrete
  participation or engagement activity.
- Keep actions concise.
- Focus only on execution and implementation.
- The plan should feel like a weekly roadmap for teachers.
- The intensity of the plan must match the student's overall risk level.

STYLE TARGET
Weak:
* Establish regular communication with parents or guardians.

Better:
* Schedule a 15-minute family check-in to set one attendance or homework goal
  and agree on a weekly update routine.

Weak:
* Provide one-to-one mentoring or tutoring support.

Better:
* Assign a mentor or tutor to review missing assignments weekly and practice
  one priority skill before the next progress check."""


def _clean_action_item(text: str) -> str:
    """Convert analysis-style wording into teacher-action wording."""
    cleaned = text.strip()

    phrase_replacements = [
        (
            r"^continue monitoring and positive reinforcement\.?",
            "Review attendance, homework, engagement, and behavior records, "
            "then give brief positive feedback for maintained progress.",
        ),
        (
            r"^continue monitoring, maintenance, and positive reinforcement\.?",
            "Review weekly indicators and reinforce the strongest classroom "
            "habit the student maintained.",
        ),
        (
            r"^continue monitoring\.?",
            "Review the student's weekly indicators and respond only if a "
            "new concern appears.",
        ),
        (
            r"^establish regular communication with parents or guardians\.?",
            "Schedule a 15-minute family check-in to set one attendance or "
            "homework goal and agree on a weekly update routine.",
        ),
        (
            r"^provide one-to-one mentoring or tutoring support\.?",
            "Assign a mentor or tutor to review missing assignments weekly "
            "and practice one priority academic skill.",
        ),
        (
            r"^adapt instruction to individual student needs\.?",
            "Identify one priority skill gap and provide a short targeted "
            "practice routine with clear success criteria.",
        ),
        (
            r"^increase student participation during learning\.?",
            "Give the student a defined role in a collaborative activity so "
            "participation can be observed and reinforced.",
        ),
        (
            r"^provide .* with structured after-school learning opportunities\.?",
            "Connect the student with a structured after-school support block "
            "for assignment completion and guided practice.",
        ),
        (
            r"\bto discuss (?:her|his|their) declining attendance and "
            r"academic performance\b",
            "to establish attendance goals, academic support priorities, "
            "and communication expectations",
        ),
        (
            r"\bto discuss declining attendance and academic performance\b",
            "to establish attendance goals, academic support priorities, "
            "and communication expectations",
        ),
        (
            r"\bto discuss (?:her|his|their) declining attendance\b",
            "to establish attendance goals and communication expectations",
        ),
        (
            r"\bto discuss declining attendance\b",
            "to establish attendance goals and communication expectations",
        ),
        (
            r"\bto discuss (?:her|his|their) academic performance concerns\b",
            "to set academic support goals",
        ),
        (
            r"\bto discuss academic performance concerns\b",
            "to set academic support goals",
        ),
        (
            r"\bto discuss (?:her|his|their) homework completion concerns\b",
            "to create a homework tracking routine",
        ),
        (
            r"\bto discuss homework completion concerns\b",
            "to create a homework tracking routine",
        ),
        (
            r"\bto discuss (?:her|his|their) behavior concerns\b",
            "to agree on classroom behavior expectations and supports",
        ),
        (
            r"\bto discuss behavior concerns\b",
            "to agree on classroom behavior expectations and supports",
        ),
        (
            r"\baddress (?:her|his|their) academic challenges\b",
            "support priority academic skills",
        ),
        (
            r"\baddress academic challenges\b",
            "support priority academic skills",
        ),
        (
            r"\bwhere (?:she|he|they) (?:is|are) struggling\b",
            "where additional practice is needed",
        ),
        (
            r"\bstudents who may be struggling academically\b",
            "students who need additional academic practice",
        ),
        (
            r"\bdeclining attendance\b",
            "attendance goals",
        ),
        (
            r"\bacademic performance concerns\b",
            "academic support goals",
        ),
        (
            r"\bhomework completion concerns\b",
            "homework tracking goals",
        ),
        (
            r"\bbehavior concerns\b",
            "classroom behavior goals",
        ),
        (
            r"\brisk level\b",
            "support need",
        ),
    ]

    for pattern, replacement in phrase_replacements:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _normalize_generated_heading(line: str) -> str | None:
    """Map model heading variants to the canonical action-plan sections."""
    normalized = line.strip().strip("*").strip()
    normalized = re.sub(r"^#+\s*", "", normalized)
    normalized = normalized.rstrip(":").strip().lower()

    if normalized == "action plan":
        return "# Action Plan"

    week_match = re.fullmatch(r"week\s*([1-4])", normalized)
    if week_match:
        return f"## Week {week_match.group(1)}"

    if normalized in {"sources", "source", "sources used", "source used"}:
        return "## Sources Used"

    return None


def _strip_inline_source_text(line: str) -> str:
    """Remove malformed inline source notes from a generated action line."""
    return re.split(
        r"\bsource(?:s)?\s+used\s*:?\s*\*?\*?",
        line,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()


def _is_source_or_risk_leak(line: str) -> bool:
    """Return True when a line is source/risk metadata rather than an action."""
    normalized = line.strip().lower()
    if not normalized:
        return True

    if re.match(r"^source(?:s)?\s+used\s*:?", normalized):
        return True

    if re.fullmatch(r"(attendance|academic|homework|behavior|engagement|family support)\s+risk", normalized):
        return True

    if " risk," in normalized or normalized.endswith(" risk"):
        return True

    return False


def _source_label(source: str) -> str:
    """Return the display label from a plain or Markdown-linked source."""
    text = source.strip().lstrip("*- ").strip()
    markdown_match = re.fullmatch(r"\[([^\]]+)\]\([^)]+\)", text)
    if markdown_match:
        return markdown_match.group(1).strip()
    return text


def _normalize_source_label(source: str) -> str:
    """Normalize a source label for exact source validation."""
    label = _source_label(source)
    return re.sub(r"\s+", " ", label).strip().lower()


def _minimum_source_count(overall_risk: str) -> int:
    """Return the minimum number of evidence sources to show by risk level."""
    if overall_risk == "Critical":
        return 3
    if overall_risk == "High":
        return 2
    return 1


def _infer_sources_from_actions(
    actions: list[str],
    valid_sources: dict[str, str],
) -> list[str]:
    """Infer valid evidence sources referenced by action wording."""
    action_text = " ".join(actions).lower()
    inferred: list[str] = []

    source_cues = {
        "family engagement": (
            "family",
            "parent",
            "guardian",
            "home and school",
            "home-school",
        ),
        "mentoring/tutoring": (
            "mentor",
            "tutor",
            "tutoring",
            "priority skill",
            "academic skill",
            "missing assignment",
        ),
        "after-school opportunities": (
            "after-school",
            "after school",
            "lunch support",
            "support block",
            "structured support",
        ),
        "individualized instruction": (
            "individualized",
            "skill gap",
            "targeted practice",
            "clear success criteria",
            "adjust instruction",
        ),
        "active learning": (
            "collaborative",
            "problem-solving",
            "participation role",
            "classroom activity",
            "learning activities",
        ),
        "continue monitoring": (
            "monitor",
            "positive feedback",
            "positive reinforcement",
            "review current indicators",
        ),
    }

    for source_label, cues in source_cues.items():
        matched_source = valid_sources.get(source_label)
        if matched_source and any(cue in action_text for cue in cues):
            inferred.append(matched_source)

    return inferred


def _is_monitoring_action(action: str) -> bool:
    """Return True when an action is primarily monitoring-oriented."""
    normalized = action.lower()
    return any(
        phrase in normalized
        for phrase in (
            "monitor",
            "review progress",
            "review attendance",
            "review homework",
            "review engagement",
            "review behavior",
            "review the student's weekly indicators",
            "continue monitoring",
            "check attendance",
            "check homework",
            "track",
        )
    )


def _is_low_risk_action_allowed(action: str, valid_source_labels: set[str]) -> bool:
    """Allow only maintenance-focused actions for low-risk students."""
    normalized = action.lower()
    rejected_terms = (
        "tutor",
        "tutoring",
        "mentor",
        "mentoring",
        "escalat",
        "intensive",
        "counsel",
        "after-school",
        "after school",
        "intervention",
        "behavior support",
        "support block",
        "skill gap",
        "missing assignments",
    )
    if any(term in normalized for term in rejected_terms):
        return False

    family_terms = ("family", "parent", "guardian")
    has_family_source = "family engagement" in valid_source_labels
    if any(term in normalized for term in family_terms) and not has_family_source:
        return False

    allowed_terms = (
        "monitor",
        "positive feedback",
        "positive reinforcement",
        "encourage",
        "encouragement",
        "check-in",
        "check in",
        "celebrate",
        "progress",
        "maintain",
        "review",
        "classroom",
        "attendance",
        "homework",
        "engagement",
        "behavior",
        "family",
        "parent",
        "guardian",
    )
    return any(term in normalized for term in allowed_terms)


def _fallback_action(overall_risk: str, week_number: int) -> str:
    """Return a risk-appropriate fallback action for an empty week."""
    low_risk_actions = {
        1: "Review current indicators and reinforce the strongest positive classroom habit.",
        2: "Continue monitoring progress and encourage consistent classroom participation.",
        3: "Check for any new concerns and celebrate maintained attendance, homework, or engagement.",
        4: "Review the month of progress and continue routine monitoring if performance remains stable.",
    }
    moderate_actions = {
        1: "Review progress and confirm the targeted support routine for the week.",
        2: "Check whether the current support is improving follow-through and adjust if needed.",
        3: "Monitor progress indicators and refine the support strategy with the teacher team.",
        4: "Review progress and decide whether to continue, reduce, or adjust support next month.",
    }
    high_actions = {
        1: "Confirm the intervention routine and assign staff follow-up responsibilities.",
        2: "Monitor intervention effectiveness and coordinate follow-up support.",
        3: "Review progress data and adjust the intervention routine with the support team.",
        4: "Evaluate intervention outcomes and set next-month support priorities.",
    }
    critical_actions = {
        1: "Coordinate immediate support actions and confirm family-school communication steps.",
        2: "Review weekly progress with school staff and adjust intensive supports as needed.",
        3: "Check intervention follow-through and address barriers with the support team.",
        4: "Conduct a formal review of intervention outcomes and determine next support steps.",
    }

    if overall_risk == "Low":
        return low_risk_actions.get(week_number, low_risk_actions[4])
    if overall_risk == "Moderate":
        return moderate_actions.get(week_number, moderate_actions[4])
    if overall_risk == "High":
        return high_actions.get(week_number, high_actions[4])
    if overall_risk == "Critical":
        return critical_actions.get(week_number, critical_actions[4])
    return moderate_actions.get(week_number, moderate_actions[4])


def _select_week_actions(
    actions: list[str],
    overall_risk: str,
    valid_source_labels: set[str],
    seen_monitoring_actions: set[str],
    seen_actions: set[str],
    week_number: int,
) -> list[str]:
    """Select risk-appropriate, non-repetitive actions for one week."""
    max_actions = 1 if overall_risk == "Low" else 2
    selected: list[str] = []
    monitoring_candidates: list[str] = []

    for action in actions:
        action = action.strip()
        if not action:
            continue

        if overall_risk == "Low" and not _is_low_risk_action_allowed(
            action,
            valid_source_labels,
        ):
            continue

        normalized = re.sub(r"\s+", " ", action.lower())
        if normalized in seen_actions:
            continue

        is_monitoring = _is_monitoring_action(action)
        if is_monitoring:
            if normalized in seen_monitoring_actions:
                continue
            monitoring_candidates.append(action)
            continue

        selected.append(action)
        seen_actions.add(normalized)
        if len(selected) >= max_actions:
            break

    if len(selected) < max_actions:
        for action in monitoring_candidates:
            selected.append(action)
            normalized = re.sub(r"\s+", " ", action.lower())
            seen_actions.add(normalized)
            seen_monitoring_actions.add(normalized)
            if len(selected) >= max_actions:
                break

    if not selected:
        fallback = _fallback_action(overall_risk, week_number)
        selected.append(fallback)
        seen_actions.add(re.sub(r"\s+", " ", fallback.lower()))
        if _is_monitoring_action(fallback):
            seen_monitoring_actions.add(re.sub(r"\s+", " ", fallback.lower()))

    return selected[:max_actions]


def clean_action_plan_output(
    generated_text: str,
    student_name: str,
    source_names: list[str],
    overall_risk: str,
) -> str:
    """Return only the UI-ready action-plan sections.

    Local models sometimes add short prefaces, extra headings, or explanations.
    This helper keeps the generated teacher-facing output constrained to the
    sections the UI expects while preserving the model's week-by-week actions.
    """
    allowed_headings = [
        "# Action Plan",
        "## Week 1",
        "## Week 2",
        "## Week 3",
        "## Week 4",
        "## Sources",
        "## Sources Used",
    ]
    exact_title = "# Action Plan"
    lines = generated_text.splitlines()
    sections: dict[str, list[str]] = {heading: [] for heading in allowed_headings[1:]}
    valid_sources = {
        _normalize_source_label(source): source
        for source in source_names
        if _normalize_source_label(source)
    }
    valid_source_labels = set(valid_sources)
    source_validation_failures = 0

    current_heading: str | None = None
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        normalized_heading = _normalize_generated_heading(line)
        if normalized_heading:
            if normalized_heading == "# Action Plan":
                current_heading = "# Action Plan"
            elif normalized_heading in sections:
                current_heading = normalized_heading
            continue

        if line.startswith("#"):
            current_heading = None
            continue

        if current_heading in sections:
            bullet_text = line.lstrip("*- ").strip()
            bullet_text = _strip_inline_source_text(bullet_text)
            if not bullet_text:
                continue
            if bullet_text.lower().startswith(("action:", "metric:")):
                bullet_text = bullet_text.split(":", 1)[1].strip()
            if current_heading not in ("## Sources", "## Sources Used") and _is_source_or_risk_leak(bullet_text):
                continue
            if bullet_text:
                if current_heading not in ("## Sources", "## Sources Used"):
                    bullet_text = _clean_action_item(bullet_text)
                sections[current_heading].append(bullet_text)

    output_lines = [exact_title]
    seen_monitoring_actions: set[str] = set()
    seen_actions: set[str] = set()
    empty_weeks: list[str] = []
    selected_actions_by_week: list[str] = []
    for week_number, heading in enumerate(
        ["## Week 1", "## Week 2", "## Week 3", "## Week 4"],
        start=1,
    ):
        selected_actions = _select_week_actions(
            sections[heading],
            overall_risk,
            valid_source_labels,
            seen_monitoring_actions,
            seen_actions,
            week_number,
        )
        if not sections[heading]:
            empty_weeks.append(heading.replace("## ", ""))
        selected_actions_by_week.extend(selected_actions)
        output_lines.extend(["", heading, ""])
        output_lines.extend(f"* {item}" for item in selected_actions)

    generated_sources = sections["## Sources Used"] or sections["## Sources"]
    if generated_sources:
        sources = []
        for generated_source in generated_sources:
            normalized_source = _normalize_source_label(generated_source)
            matched_source = valid_sources.get(normalized_source)
            if matched_source:
                sources.append(matched_source)
            else:
                source_validation_failures += 1
    else:
        sources = source_names

    inferred_sources = _infer_sources_from_actions(
        selected_actions_by_week,
        valid_sources,
    )
    sources.extend(inferred_sources)

    if not sources and overall_risk == "Low":
        sources = [valid_sources.get("continue monitoring", "Continue Monitoring")]
    elif not sources:
        sources = source_names

    deduped_sources = []
    seen_sources = set()
    for source in sources:
        normalized_source = _normalize_source_label(source)
        if normalized_source and normalized_source not in seen_sources:
            deduped_sources.append(source)
            seen_sources.add(normalized_source)
    sources = deduped_sources

    minimum_source_count = _minimum_source_count(overall_risk)
    if len(sources) < minimum_source_count and overall_risk in {"High", "Critical"}:
        for source in source_names:
            normalized_source = _normalize_source_label(source)
            if normalized_source and normalized_source not in seen_sources:
                sources.append(source)
                seen_sources.add(normalized_source)
            if len(sources) >= minimum_source_count:
                break

    output_lines.extend(["", "## Sources Used", ""])
    output_lines.extend(f"* {source}" for source in sources[:5])

    logging.getLogger(__name__).info(
        "Action plan cleanup metrics: weeks_present=%s empty_weeks=%s "
        "source_count=%s source_validation_failures=%s",
        4 - len(empty_weeks),
        empty_weeks,
        len(sources),
        source_validation_failures,
    )

    return "\n".join(output_lines).strip()
