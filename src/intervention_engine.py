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

CATEGORY_TO_LIBRARY_VALUE = {
    "ATTENDANCE": "attendance",
    "ACADEMIC": "academic",
    "HOMEWORK": "homework",
    "BEHAVIOR": "behavior",
    "ENGAGEMENT": "engagement",
    "FAMILY_SUPPORT": "attendance",
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

        if text.startswith("teacher observations:"):
            categories.add("ENGAGEMENT")
            categories.add("FAMILY_SUPPORT")

        for category, triggers in CATEGORY_TRIGGERS.items():
            if any(trigger in text for trigger in triggers):
                categories.add(category)

    return categories


def recommend_interventions(
    root_causes: list[str],
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

    categories = extract_risk_categories(root_causes)
    if not categories:
        return []

    scored_recommendations: list[InterventionRecommendation] = []
    seen_ids: set[str] = set()

    for index, intervention in enumerate(intervention_library):
        intervention_id = _intervention_id(intervention, index)
        if intervention_id in seen_ids:
            continue

        score = _score_intervention(intervention, categories, root_causes)
        if score < MINIMUM_RELEVANCE_SCORE:
            continue

        seen_ids.add(intervention_id)
        scored_recommendations.append(_to_recommendation(intervention, score))

    scored_recommendations.sort(
        key=lambda recommendation: recommendation.relevance_score,
        reverse=True,
    )
    return scored_recommendations[:max_results]


def _score_intervention(
    intervention: dict,
    categories: set[str],
    root_causes: list[str],
) -> int:
    """Calculate a structured, precision-oriented relevance score."""
    risk_categories = _lower_set(intervention.get("risk_categories", []))
    when_to_use = _lower_list(intervention.get("when_to_use", []))
    keywords = _lower_list(intervention.get("keywords", []))
    intervention_name = str(intervention.get("intervention_name", "")).lower()

    score = 0
    supporting_signal_score = 0

    for category in categories:
        library_category = CATEGORY_TO_LIBRARY_VALUE[category]
        if library_category in risk_categories:
            score += RISK_CATEGORY_SCORE

        for term in CATEGORY_WHEN_TO_USE_TERMS[category]:
            if _contains_match(term, when_to_use):
                score += WHEN_TO_USE_SCORE
                supporting_signal_score += WHEN_TO_USE_SCORE

        for term in CATEGORY_KEYWORD_TERMS[category]:
            if _contains_match(term, keywords):
                score += KEYWORD_SCORE
                supporting_signal_score += KEYWORD_SCORE

    boost = _special_rule_boost(
        intervention_name=intervention_name,
        risk_categories=risk_categories,
        keywords=keywords,
        categories=categories,
        root_causes=root_causes,
    )
    score += boost
    supporting_signal_score += boost

    if supporting_signal_score <= 0:
        return 0

    return score


def _special_rule_boost(
    intervention_name: str,
    risk_categories: set[str],
    keywords: list[str],
    categories: set[str],
    root_causes: list[str],
) -> int:
    """Apply explicit precision boosts for teacher-facing intervention rules."""
    boost = 0
    keyword_text = " ".join(keywords)

    if _has_teacher_observations(root_causes):
        if "family engagement" in intervention_name or "family engagement" in keyword_text:
            boost += SPECIAL_RULE_SCORE
        if "engagement" in risk_categories or "active learning" in intervention_name:
            boost += SPECIAL_RULE_SCORE

    if "BEHAVIOR" in categories:
        if "behavior" in risk_categories or "behavioral support" in keyword_text:
            boost += SPECIAL_RULE_SCORE
        if "mentoring" in intervention_name or "mentoring" in keyword_text:
            boost += SPECIAL_RULE_SCORE
        if "counseling" in intervention_name or "counseling" in keyword_text:
            boost += SPECIAL_RULE_SCORE

    if "ATTENDANCE" in categories:
        if "attendance improvement" in intervention_name:
            boost += SPECIAL_RULE_SCORE
        if "family engagement" in intervention_name or "family engagement" in keyword_text:
            boost += SPECIAL_RULE_SCORE

    if "HOMEWORK" in categories:
        if "homework support" in intervention_name or "homework support" in keyword_text:
            boost += SPECIAL_RULE_SCORE
        if "tutoring" in intervention_name or "tutoring" in keyword_text:
            boost += SPECIAL_RULE_SCORE
        if "study skills" in intervention_name or "study skills" in keyword_text:
            boost += SPECIAL_RULE_SCORE

    return boost


def _to_recommendation(
    intervention: dict,
    relevance_score: int,
) -> InterventionRecommendation:
    """Convert an intervention dictionary to a ranked recommendation."""
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
    )


def _contains_match(term: str, values: list[str]) -> bool:
    """Return whether a structured field contains the term."""
    normalized_term = term.lower()
    return any(normalized_term in value for value in values)


def _has_teacher_observations(root_causes: list[str]) -> bool:
    """Return whether root causes include teacher observations."""
    return any(
        root_cause.lower().startswith("teacher observations:")
        for root_cause in root_causes
    )


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
