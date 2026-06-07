from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_INTERVENTION_LIBRARY_PATH = Path("knowledge_base/interventions.json")
FALLBACK_INTERVENTION_LIBRARY_PATH = Path("knowledge_base/Intreventions.json")

SUPPORTED_RISK_CATEGORIES = {
    "ATTENDANCE",
    "ACADEMIC",
    "HOMEWORK",
    "BEHAVIOR",
    "ENGAGEMENT",
    "FAMILY_SUPPORT",
}

RISK_CATEGORY_SCORE = 100
WHEN_TO_USE_SCORE = 30
KEYWORD_SCORE = 5
SPECIAL_RULE_SCORE = 40
MINIMUM_RELEVANCE_SCORE = 35

RISK_WEIGHTS = {
    "Low": 1,
    "Moderate": 2,
    "High": 3,
    "Critical": 4,
}

RISK_RESULT_LIMITS = {
    "Low": 1,
    "Moderate": 2,
    "High": 3,
    "Critical": 5,
}

CATEGORY_TO_LIBRARY_VALUE = {
    "ATTENDANCE": "attendance",
    "ACADEMIC": "academic",
    "HOMEWORK": "homework",
    "BEHAVIOR": "behavior",
    "ENGAGEMENT": "engagement",
    "FAMILY_SUPPORT": "family_support",
}

CATEGORY_TRIGGERS = {
    "ATTENDANCE": (
        "attendance",
        "attendance declined",
        "attendance decline",
        "absent",
        "absence",
    ),
    "ACADEMIC": (
        "academic",
        "academic performance",
        "grade",
        "grades",
        "low grades",
        "learning gap",
    ),
    "HOMEWORK": (
        "homework",
        "homework completion",
        "missing work",
        "study skills",
    ),
    "BEHAVIOR": (
        "behavior",
        "behavioral",
        "behavior concerns",
        "classroom disruptions",
        "conflict",
    ),
    "ENGAGEMENT": (
        "engagement",
        "participation",
        "motivation",
        "classroom disengagement",
    ),
    "FAMILY_SUPPORT": (
        "family",
        "parent",
        "guardian",
        "home support",
        "teacher observations",
    ),
}

CATEGORY_WHEN_TO_USE_TERMS = {
    "ATTENDANCE": ("attendance decline", "attendance"),
    "ACADEMIC": (
        "academic performance concerns",
        "academic concerns",
        "course difficulties",
        "low grades",
        "persistent academic struggles",
        "low assessment performance",
    ),
    "HOMEWORK": (
        "homework completion issues",
        "homework",
        "incomplete homework",
    ),
    "BEHAVIOR": (
        "behavioral concerns",
        "behavior",
        "classroom disruptions",
    ),
    "ENGAGEMENT": (
        "low engagement",
        "classroom disengagement",
        "low participation",
        "decreasing motivation",
    ),
    "FAMILY_SUPPORT": (
        "attendance decline",
        "homework completion issues",
        "academic performance concerns",
        "behavioral concerns",
    ),
}

CATEGORY_KEYWORD_TERMS = {
    "ATTENDANCE": (
        "attendance",
        "family engagement",
        "family support",
        "parent communication",
    ),
    "ACADEMIC": (
        "low grades",
        "academic support",
        "tutoring",
        "learning gaps",
    ),
    "HOMEWORK": (
        "homework support",
        "tutoring",
        "study skills",
    ),
    "BEHAVIOR": (
        "behavioral supports",
        "mentoring",
        "counseling",
    ),
    "ENGAGEMENT": (
        "student engagement",
        "engagement",
        "active learning",
        "participation",
        "motivation",
    ),
    "FAMILY_SUPPORT": (
        "family engagement",
        "family support",
        "parent communication",
        "guardian",
    ),
}


@dataclass(frozen=True)
class InterventionRecommendation:
    """Ranked intervention recommendation from the curated knowledge base."""

    intervention_name: str
    category: str
    summary: list[str]
    expected_benefits: list[str]
    evidence_level: str
    source: str
    reference_url: str
    relevance_score: int
    recommendation_reason: str


def monitoring_recommendation() -> InterventionRecommendation:
    """Return a monitoring recommendation for low-risk students."""
    return InterventionRecommendation(
        intervention_name="Continue Monitoring",
        category="Monitoring",
        summary=[
            "Student is currently performing well.",
            "Continue positive reinforcement.",
            "Maintain routine communication.",
            "Reassess during the next reporting cycle.",
        ],
        expected_benefits=[
            "Sustains current progress without unnecessary intervention fatigue.",
            "Keeps teachers and families aligned on continued student success.",
            "Supports early detection if the student's risk profile changes.",
        ],
        evidence_level="school practice",
        source="Homeroom Copilot",
        reference_url="",
        relevance_score=0,
        recommendation_reason=(
            "Recommended because the student is currently low risk and does "
            "not need a targeted intervention program."
        ),
    )


def load_intervention_library(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the curated intervention library from JSON.

    The intended path is knowledge_base/interventions.json. A fallback is
    included for the current workspace's misspelled file name.
    """
    library_path = path or DEFAULT_INTERVENTION_LIBRARY_PATH
    if path is None and not library_path.exists():
        library_path = FALLBACK_INTERVENTION_LIBRARY_PATH

    with library_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Intervention library must be a list of dictionaries.")

    return data


def extract_risk_categories(root_causes: list[str]) -> set[str]:
    """Extract standardized risk categories from root-cause explanations.

    Teacher observations intentionally produce both ENGAGEMENT and
    FAMILY_SUPPORT because teachers often document participation concerns and
    signals that should trigger communication with families.
    """
    categories: set[str] = set()

    for root_cause in root_causes:
        text = root_cause.lower()
        if not _is_actionable_root_cause(text):
            continue

        if text.startswith("teacher observations:"):
            categories.add("ENGAGEMENT")
            categories.add("FAMILY_SUPPORT")

        for category, triggers in CATEGORY_TRIGGERS.items():
            if any(trigger in text for trigger in triggers):
                categories.add(category)

    return categories


def recommend_interventions(
    root_causes: list[str],
    risk_profile: dict[str, str],
    intervention_library: list[dict],
    max_results: int = 5,
) -> list[InterventionRecommendation]:
    """Recommend high-precision interventions for a student risk profile.

    This deterministic engine uses only structured intervention fields:
    risk_categories, when_to_use, and keywords. It does not use semantic
    similarity, embeddings, or broad free-text token overlap.
    """
    if max_results <= 0:
        return []

    normalized_risk = _normalize_overall_risk(risk_profile.get("overall_risk"))
    if normalized_risk == "Low":
        return [monitoring_recommendation()]

    categories = extract_risk_categories(root_causes)
    if not categories:
        return []

    result_limit = _result_limit(normalized_risk, max_results)

    scored_recommendations: list[InterventionRecommendation] = []
    seen_ids: set[str] = set()

    for index, intervention in enumerate(intervention_library):
        intervention_id = _intervention_id(intervention, index)
        if intervention_id in seen_ids:
            continue

        score, matched_areas = _score_intervention(
            intervention=intervention,
            categories=categories,
            risk_profile=risk_profile,
            root_causes=root_causes,
        )
        if score < MINIMUM_RELEVANCE_SCORE:
            continue

        seen_ids.add(intervention_id)
        scored_recommendations.append(
            _to_recommendation(intervention, score, matched_areas)
        )

    scored_recommendations.sort(
        key=lambda recommendation: recommendation.relevance_score,
        reverse=True,
    )
    return scored_recommendations[:result_limit]


def _score_intervention(
    intervention: dict,
    categories: set[str],
    risk_profile: dict[str, str],
    root_causes: list[str],
) -> tuple[int, set[str]]:
    """Calculate a structured, precision-oriented relevance score."""
    primary_targets = _lower_set(intervention.get("primary_targets", []))
    secondary_targets = _lower_set(intervention.get("secondary_targets", []))
    mitigates = _lower_set(intervention.get("mitigates", []))
    when_to_use = _lower_list(intervention.get("when_to_use", []))
    keywords = _lower_list(intervention.get("keywords", []))

    score = 0
    supporting_signal_score = 0
    matched_areas: set[str] = set()

    for category in categories:
        risk_area = CATEGORY_TO_LIBRARY_VALUE[category]
        risk_weight = _risk_weight_for_area(risk_area, risk_profile)

        if risk_area in primary_targets:
            score += 100 * risk_weight
            supporting_signal_score += 100 * risk_weight
            matched_areas.add(risk_area)

        if risk_area in secondary_targets:
            score += 50 * risk_weight
            supporting_signal_score += 50 * risk_weight
            matched_areas.add(risk_area)

        if risk_area in mitigates:
            score += 25 * risk_weight
            supporting_signal_score += 25 * risk_weight
            matched_areas.add(risk_area)

        for term in CATEGORY_WHEN_TO_USE_TERMS[category]:
            if _contains_match(term, when_to_use):
                score += 20
                supporting_signal_score += 20

        for term in CATEGORY_KEYWORD_TERMS[category]:
            if _contains_match(term, keywords):
                score += KEYWORD_SCORE
                supporting_signal_score += KEYWORD_SCORE

    if supporting_signal_score <= 0:
        return 0, set()

    return score, matched_areas


def _to_recommendation(
    intervention: dict,
    relevance_score: int,
    matched_areas: set[str],
) -> InterventionRecommendation:
    """Convert an intervention dictionary to a ranked recommendation."""
    reason_template = str(intervention.get("recommendation_reason_template") or "")
    return InterventionRecommendation(
        intervention_name=str(
            intervention.get("intervention_name") or "Unnamed Intervention"
        ),
        category=str(intervention.get("category") or "Uncategorized"),
        summary=_string_list(intervention.get("summary", [])),
        expected_benefits=_string_list(intervention.get("expected_benefits", [])),
        evidence_level=str(intervention.get("evidence_level") or ""),
        source=str(intervention.get("source") or ""),
        reference_url=str(intervention.get("reference_url") or ""),
        relevance_score=relevance_score,
        recommendation_reason=_recommendation_reason(
            reason_template,
            matched_areas,
        ),
    )


def _contains_match(term: str, values: list[str]) -> bool:
    """Return whether a structured field contains the term."""
    normalized_term = term.lower()
    return any(normalized_term in value for value in values)


def _is_actionable_root_cause(text: str) -> bool:
    """Return whether a root cause should trigger intervention matching."""
    if "remained relatively stable" in text:
        return False

    actionable_terms = (
        "declined",
        "decline",
        "significantly",
        "behavior concerns:",
        "teacher observations:",
        "concern",
        "disruption",
        "conflict",
        "missing",
        "low ",
    )
    return any(term in text for term in actionable_terms)


def _normalize_overall_risk(overall_risk: str | None) -> str | None:
    """Normalize an optional overall risk label."""
    if overall_risk is None:
        return None

    normalized = overall_risk.replace(" Risk", "").strip().title()
    if normalized in RISK_RESULT_LIMITS:
        return normalized
    return None


def _result_limit(overall_risk: str | None, max_results: int) -> int:
    """Return the maximum number of intervention programs for a risk level."""
    if overall_risk is None:
        return max_results
    return min(max_results, RISK_RESULT_LIMITS[overall_risk])


def _has_teacher_observations(root_causes: list[str]) -> bool:
    """Return whether root causes include teacher observations."""
    return any(
        root_cause.lower().startswith("teacher observations:")
        for root_cause in root_causes
    )


def _risk_weight_for_area(risk_area: str, risk_profile: dict[str, str]) -> int:
    """Return the student's risk weight for a target risk area."""
    field_name = {
        "attendance": "attendance_risk",
        "academic": "academic_risk",
        "homework": "homework_risk",
        "behavior": "behavior_risk",
        "engagement": "engagement_risk",
        "family_support": "overall_risk",
    }.get(risk_area, "overall_risk")

    risk_level = _normalize_overall_risk(risk_profile.get(field_name))
    if risk_level is None:
        risk_level = _normalize_overall_risk(risk_profile.get("overall_risk"))
    return RISK_WEIGHTS.get(risk_level or "Low", 1)


def _recommendation_reason(
    reason_template: str,
    matched_areas: set[str],
) -> str:
    """Build an explanation from template text and matched risk areas."""
    matched_text = _format_matched_areas(matched_areas)
    if reason_template and matched_text:
        return f"{reason_template} Matched risk areas: {matched_text}."
    if reason_template:
        return reason_template
    if matched_text:
        return f"Recommended because {matched_text} were identified as concerns."
    return "Recommended based on the student's current risk profile."


def _format_matched_areas(matched_areas: set[str]) -> str:
    """Format matched risk areas for display in a recommendation reason."""
    labels = {
        "attendance": "attendance",
        "academic": "academic performance",
        "homework": "homework completion",
        "behavior": "behavior",
        "engagement": "engagement",
        "family_support": "family support",
    }
    ordered = [
        labels[area]
        for area in (
            "attendance",
            "academic",
            "homework",
            "behavior",
            "engagement",
            "family_support",
        )
        if area in matched_areas
    ]

    if not ordered:
        return ""
    if len(ordered) == 1:
        return ordered[0]
    return ", ".join(ordered[:-1]) + f" and {ordered[-1]}"


def _string_list(value: Any) -> list[str]:
    """Normalize a JSON string-or-list field to a list of strings."""
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def _lower_list(value: Any) -> list[str]:
    """Normalize a JSON string-or-list field to lowercase strings."""
    return [item.lower() for item in _string_list(value)]


def _lower_set(value: Any) -> set[str]:
    """Normalize a JSON string-or-list field to a lowercase set."""
    return set(_lower_list(value))


def _intervention_id(intervention: dict, fallback_index: int) -> str:
    """Return a stable identifier for duplicate removal."""
    return str(
        intervention.get("id")
        or intervention.get("intervention_name")
        or fallback_index
    )
