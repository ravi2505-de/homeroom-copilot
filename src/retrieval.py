from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


DEFAULT_LIBRARY_PATH = Path("knowledge_base/interventions.json")
FALLBACK_LIBRARY_PATH = Path("knowledge_base/Intreventions.json")

RootCauseCategory = Literal[
    "ATTENDANCE",
    "ACADEMIC",
    "HOMEWORK",
    "BEHAVIOR",
    "ENGAGEMENT",
    "FAMILY_SUPPORT",
]

MAX_RECOMMENDATIONS = 5
PRIMARY_CATEGORY_SCORE = 100
SECONDARY_WHEN_TO_USE_SCORE = 30
TERTIARY_KEYWORD_SCORE = 5
EXPLICIT_BOOST_SCORE = 40
MINIMUM_RELEVANCE_SCORE = 35


@dataclass(frozen=True)
class InterventionRecommendation:
    """Evidence-based intervention recommendation for a student risk profile."""

    name: str
    category: str
    summary: str
    benefit: str
    reference_url: str


CATEGORY_TRIGGERS: dict[RootCauseCategory, tuple[str, ...]] = {
    "ATTENDANCE": (
        "attendance",
        "absent",
        "absence",
        "attendance declined",
    ),
    "ACADEMIC": (
        "academic",
        "academic performance",
        "grade",
        "grades",
        "learning gap",
    ),
    "HOMEWORK": (
        "homework",
        "homework completion",
        "study skills",
        "missing work",
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
        "declining participation",
    ),
    "FAMILY_SUPPORT": (
        "family",
        "parent",
        "guardian",
        "home support",
        "teacher observations",
    ),
}

CATEGORY_TO_RISK_CATEGORY: dict[RootCauseCategory, str] = {
    "ATTENDANCE": "attendance",
    "ACADEMIC": "academic",
    "HOMEWORK": "homework",
    "BEHAVIOR": "behavior",
    "ENGAGEMENT": "engagement",
    "FAMILY_SUPPORT": "attendance",
}

CATEGORY_WHEN_TO_USE_TERMS: dict[RootCauseCategory, tuple[str, ...]] = {
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

CATEGORY_KEYWORD_TERMS: dict[RootCauseCategory, tuple[str, ...]] = {
    "ATTENDANCE": ("attendance", "parent communication", "family support"),
    "ACADEMIC": ("low grades", "academic support", "tutoring", "learning gaps"),
    "HOMEWORK": ("homework", "tutoring", "study skills"),
    "BEHAVIOR": ("behavior", "mentoring", "counseling", "behavioral supports"),
    "ENGAGEMENT": ("engagement", "participation", "motivation", "active learning"),
    "FAMILY_SUPPORT": (
        "family support",
        "family engagement",
        "parent communication",
        "guardian",
    ),
}

GENERIC_NOISE_TERMS = {
    "academic",
    "homework",
    "engagement",
    "declined",
    "performance",
    "concerns",
    "completion",
}


def load_intervention_library(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the intervention library from JSON.

    Args:
        path: Optional explicit path to an interventions JSON file.

    Returns:
        A list of intervention dictionaries.
    """
    library_path = path or DEFAULT_LIBRARY_PATH
    if not library_path.exists() and path is None:
        library_path = FALLBACK_LIBRARY_PATH

    with library_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Intervention library must be a list of dictionaries.")

    return data


def retrieve_interventions(
    root_causes: list[str],
    intervention_library: list[dict],
    max_results: int = 5,
) -> list[InterventionRecommendation]:
    """Retrieve top matching interventions for identified root causes.

    Matching is based on simple keyword overlap between root-cause explanations
    and intervention metadata. Duplicate interventions are removed, and results
    are sorted by descending relevance score.

    Args:
        root_causes: Human-readable root-cause explanations for a student.
        intervention_library: Intervention dictionaries loaded from JSON.
        max_results: Maximum number of recommendations to return.

    Returns:
        A ranked list of InterventionRecommendation objects.
    """
    if max_results <= 0:
        return []

    categories = _extract_root_cause_categories(root_causes)
    scored_interventions: list[tuple[int, int, InterventionRecommendation]] = []
    seen_ids: set[str] = set()
    capped_results = min(max_results, MAX_RECOMMENDATIONS)

    for index, intervention in enumerate(intervention_library):
        intervention_id = _intervention_id(intervention, index)
        if intervention_id in seen_ids:
            continue

        score = _score_intervention(intervention, categories, root_causes)
        if score < MINIMUM_RELEVANCE_SCORE:
            continue

        seen_ids.add(intervention_id)
        scored_interventions.append(
            (score, index, _to_recommendation(intervention))
        )

    scored_interventions.sort(key=lambda item: (-item[0], item[1]))
    return [
        recommendation
        for _, _, recommendation in scored_interventions[:capped_results]
    ]


def _extract_root_cause_categories(
    root_causes: list[str],
) -> set[RootCauseCategory]:
    """Extract explicit risk categories from root-cause explanations."""
    categories: set[RootCauseCategory] = set()

    for root_cause in root_causes:
        text = root_cause.lower()
        if text.startswith("teacher observations:"):
            categories.add("ENGAGEMENT")
            categories.add("FAMILY_SUPPORT")

        for category, triggers in CATEGORY_TRIGGERS.items():
            if any(trigger in text for trigger in triggers):
                categories.add(category)

    return categories


def _score_intervention(
    intervention: dict,
    categories: set[RootCauseCategory],
    root_causes: list[str],
) -> int:
    """Calculate a precision-oriented relevance score for one intervention."""
    searchable_text = _intervention_search_text(intervention)
    risk_categories = _lower_list(intervention.get("risk_categories", []))
    when_to_use = _lower_text_list(intervention.get("when_to_use", []))
    keywords = _lower_text_list(intervention.get("keywords", []))
    score = 0
    supporting_signal_score = 0

    for category in categories:
        risk_category = CATEGORY_TO_RISK_CATEGORY[category]
        if risk_category in risk_categories:
            score += PRIMARY_CATEGORY_SCORE

        for term in CATEGORY_WHEN_TO_USE_TERMS[category]:
            if _contains_structured_match(term, when_to_use):
                score += SECONDARY_WHEN_TO_USE_SCORE
                supporting_signal_score += SECONDARY_WHEN_TO_USE_SCORE

        for term in CATEGORY_KEYWORD_TERMS[category]:
            if term in GENERIC_NOISE_TERMS:
                continue
            if _contains_structured_match(term, keywords):
                score += TERTIARY_KEYWORD_SCORE
                supporting_signal_score += TERTIARY_KEYWORD_SCORE

    if _has_teacher_observation(root_causes):
        boost = _teacher_observation_boost(searchable_text, risk_categories)
        score += boost
        supporting_signal_score += boost

    if "BEHAVIOR" in categories:
        boost = _behavior_boost(searchable_text, risk_categories)
        score += boost
        supporting_signal_score += boost

    if supporting_signal_score <= 0:
        return 0
    return score


def _contains_structured_match(term: str, values: list[str]) -> bool:
    """Check whether a structured metadata field contains a specific term."""
    normalized_term = term.lower()
    return any(normalized_term in value for value in values)


def _has_teacher_observation(root_causes: list[str]) -> bool:
    """Return whether teacher observations are present in root causes."""
    return any(
        root_cause.lower().startswith("teacher observations:")
        for root_cause in root_causes
    )


def _teacher_observation_boost(
    searchable_text: str,
    risk_categories: set[str],
) -> int:
    """Boost family-engagement and student-engagement interventions."""
    boost = 0
    if "family engagement" in searchable_text or "family support" in searchable_text:
        boost += EXPLICIT_BOOST_SCORE
    if "engagement" in risk_categories or "active learning" in searchable_text:
        boost += EXPLICIT_BOOST_SCORE
    return boost


def _behavior_boost(searchable_text: str, risk_categories: set[str]) -> int:
    """Boost behavior-specific supports such as mentoring and counseling."""
    boost = 0
    if "behavior" in risk_categories or "behavioral supports" in searchable_text:
        boost += EXPLICIT_BOOST_SCORE
    if "mentoring" in searchable_text:
        boost += EXPLICIT_BOOST_SCORE
    if "counseling" in searchable_text:
        boost += EXPLICIT_BOOST_SCORE
    return boost


def _intervention_search_text(intervention: dict) -> str:
    """Build searchable text from relevant intervention metadata."""
    fields = [
        intervention.get("id", ""),
        intervention.get("name", ""),
        intervention.get("intervention_name", ""),
        intervention.get("category", ""),
        intervention.get("retrieval_text", ""),
        intervention.get("source", ""),
    ]
    fields.extend(_string_list(intervention.get("keywords", [])))
    fields.extend(_string_list(intervention.get("risk_categories", [])))
    fields.extend(_string_list(intervention.get("summary", [])))
    fields.extend(_string_list(intervention.get("when_to_use", [])))
    fields.extend(_string_list(intervention.get("expected_benefits", [])))
    return " ".join(str(field) for field in fields).lower()


def _to_recommendation(intervention: dict) -> InterventionRecommendation:
    """Convert an intervention dictionary into a recommendation dataclass."""
    return InterventionRecommendation(
        name=str(
            intervention.get("intervention_name")
            or intervention.get("name")
            or "Unnamed Intervention"
        ),
        category=str(intervention.get("category") or "Uncategorized"),
        summary=_join_field(intervention.get("summary", "")),
        benefit=_join_field(
            intervention.get("expected_benefits")
            or intervention.get("benefit")
            or ""
        ),
        reference_url=str(intervention.get("reference_url") or ""),
    )


def _join_field(value: Any) -> str:
    """Convert a string or list field into readable text."""
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value)


def _string_list(value: Any) -> list[str]:
    """Safely normalize a possible list field to a list of strings."""
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def _lower_list(value: Any) -> set[str]:
    """Safely normalize a possible list field to lowercase strings."""
    return {item.lower() for item in _string_list(value)}


def _lower_text_list(value: Any) -> list[str]:
    """Safely normalize a possible list field to lowercase strings."""
    return [item.lower() for item in _string_list(value)]


def _intervention_id(intervention: dict, fallback_index: int) -> str:
    """Return a stable identifier for duplicate detection."""
    return str(
        intervention.get("id")
        or intervention.get("intervention_name")
        or intervention.get("name")
        or fallback_index
    )
