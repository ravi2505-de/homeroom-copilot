from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from src.intervention_engine import (
    InterventionRecommendation,
    load_intervention_library,
    recommend_interventions,
)
from src.risk_engine import assess_student_risk
from src.root_cause import generate_root_causes

DATA_PATH = PROJECT_ROOT / "data" / "students.csv"
EVALUATION_DIR = PROJECT_ROOT / "evaluation"
EVALUATION_DATASET_PATH = EVALUATION_DIR / "evaluation_dataset.json"
ACTION_PLAN_PLACEHOLDER = "[PASTE ACTION PLAN HERE]"

# Edit this list when preparing a specific evaluation set. The defaults provide
# 2 Low, 2 Moderate, 2 High, and 2 Critical risk students from the demo dataset.
STUDENT_NAMES = [
    "Olivia Moore",
    "Ava Martinez",
    "Noah Taylor",
    "William Anderson",
    "John Smith",
    "Emma Brown",
    "Sarah Johnson",
    "Lily Green",
]

PROFILE_FIELDS = [
    "student_id",
    "student_name",
    "gender",
    "grade_level",
    "homeroom",
    "attendance_p1",
    "attendance_p2",
    "attendance_p3",
    "grade_p1",
    "grade_p2",
    "grade_p3",
    "homework_p1",
    "homework_p2",
    "homework_p3",
    "behavior_incident_count",
    "behavior_notes",
    "teacher_notes",
]

RISK_FACTOR_FIELDS = [
    "attendance_risk",
    "academic_risk",
    "homework_risk",
    "behavior_risk",
    "engagement_risk",
]


def json_safe(value: Any) -> Any:
    """Convert pandas/numpy scalar values into JSON-safe Python values."""
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def load_students() -> pd.DataFrame:
    """Load the demo student dataset."""
    return pd.read_csv(DATA_PATH)


def selected_student_names() -> list[str]:
    """Return CLI-provided student names or the configured default list."""
    return sys.argv[1:] or STUDENT_NAMES


def find_student(students: pd.DataFrame, student_name: str) -> pd.Series:
    """Find a student row by case-insensitive exact name."""
    matches = students[
        students["student_name"].astype(str).str.casefold() == student_name.casefold()
    ]
    if matches.empty:
        raise ValueError(f"Student not found in dataset: {student_name}")
    return matches.iloc[0]


def build_risk_assessment(student: pd.Series) -> dict[str, Any]:
    """Calculate risk assessment values using the existing risk engine."""
    assessment = assess_student_risk(
        attendance=float(student["attendance_p3"]),
        grades=float(student["grade_p3"]),
        homework=float(student["homework_p3"]),
        behavior_incidents=int(student["behavior_incident_count"]),
    )
    return {key: json_safe(value) for key, value in assessment.items()}


def build_root_causes(student: pd.Series) -> list[str]:
    """Generate root-cause analysis using the existing root-cause engine."""
    return generate_root_causes(
        attendance_p1=float(student["attendance_p1"]),
        attendance_p2=float(student["attendance_p2"]),
        attendance_p3=float(student["attendance_p3"]),
        grade_p1=float(student["grade_p1"]),
        grade_p2=float(student["grade_p2"]),
        grade_p3=float(student["grade_p3"]),
        homework_p1=float(student["homework_p1"]),
        homework_p2=float(student["homework_p2"]),
        homework_p3=float(student["homework_p3"]),
        behavior_notes=str(student.get("behavior_notes", "") or ""),
        teacher_notes=str(student.get("teacher_notes", "") or ""),
    )


def build_student_profile(student: pd.Series) -> dict[str, Any]:
    """Extract student profile fields for an evaluation case."""
    return {field: json_safe(student.get(field)) for field in PROFILE_FIELDS}


def build_risk_factors(risk_assessment: dict[str, Any]) -> list[str]:
    """Summarize non-low risk factors for evaluator review."""
    factors = [
        f"{field.replace('_', ' ').title()}: {risk_assessment[field]}"
        for field in RISK_FACTOR_FIELDS
        if risk_assessment.get(field) != "Low"
    ]
    if not factors:
        factors.append("No elevated category risks identified.")
    factors.append(f"Overall Risk: {risk_assessment['overall_risk']}")
    return factors


def intervention_to_dict(
    recommendation: InterventionRecommendation,
) -> dict[str, Any]:
    """Convert a recommendation into evaluation evidence."""
    return {
        "intervention_name": recommendation.intervention_name,
        "category": recommendation.category,
        "summary": recommendation.summary,
        "expected_benefits": recommendation.expected_benefits,
        "evidence_level": recommendation.evidence_level,
        "source": recommendation.source,
        "reference_url": recommendation.reference_url,
        "recommendation_reason": recommendation.recommendation_reason,
    }


def source_to_dict(recommendation: InterventionRecommendation) -> dict[str, str]:
    """Extract source label and URL for one recommendation."""
    return {
        "label": recommendation.intervention_name,
        "reference_url": recommendation.reference_url,
    }


def build_case(
    case_id: str,
    student: pd.Series,
    intervention_library: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build one evaluation package without generating an AI action plan."""
    risk_assessment = build_risk_assessment(student)
    root_causes = build_root_causes(student)
    recommendations = recommend_interventions(
        root_causes=root_causes,
        risk_profile=risk_assessment,
        intervention_library=intervention_library,
        max_results=5,
    )
    return {
        "case_id": case_id,
        "student_name": str(student["student_name"]),
        "student_profile": build_student_profile(student),
        "risk_level": risk_assessment["overall_risk"],
        "risk_factors": build_risk_factors(risk_assessment),
        "risk_assessment": risk_assessment,
        "root_cause_analysis": root_causes,
        "retrieved_evidence_based_interventions": [
            intervention_to_dict(recommendation)
            for recommendation in recommendations
        ],
        "evidence_sources": [
            source_to_dict(recommendation)
            for recommendation in recommendations
        ],
        "generated_ai_action_plan": ACTION_PLAN_PLACEHOLDER,
    }


def markdown_mapping(mapping: dict[str, Any]) -> str:
    """Render dictionary values as Markdown bullets."""
    return "\n".join(f"- **{key}:** {value}" for key, value in mapping.items())


def markdown_list(items: list[str]) -> str:
    """Render strings as Markdown bullets."""
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def markdown_interventions(interventions: list[dict[str, Any]]) -> str:
    """Render retrieved interventions as compact Markdown evidence."""
    if not interventions:
        return "No interventions retrieved."

    blocks = []
    for index, intervention in enumerate(interventions, start=1):
        summary = "\n".join(
            f"   - {item}" for item in intervention.get("summary", [])
        )
        benefits = "\n".join(
            f"   - {item}" for item in intervention.get("expected_benefits", [])
        )
        blocks.append(
            "\n".join(
                [
                    f"{index}. **{intervention['intervention_name']}**",
                    f"   - Category: {intervention['category']}",
                    f"   - Evidence Level: {intervention['evidence_level']}",
                    f"   - Source: {intervention['source']}",
                    f"   - Reference URL: {intervention['reference_url']}",
                    "   - Summary:",
                    summary or "   - Not provided",
                    "   - Expected Benefits:",
                    benefits or "   - Not provided",
                    (
                        "   - Recommendation Reason: "
                        f"{intervention['recommendation_reason']}"
                    ),
                ]
            )
        )
    return "\n\n".join(blocks)


def markdown_evidence_sources(sources: list[dict[str, str]]) -> str:
    """Render source links as Markdown bullets."""
    if not sources:
        return "No evidence sources available."
    return "\n".join(
        f"- [{source['label']}]({source['reference_url']})"
        if source["reference_url"]
        else f"- {source['label']}"
        for source in sources
    )


def render_case_markdown(case: dict[str, Any]) -> str:
    """Render one evaluation case using the required section structure."""
    return f"""# Student Profile

## Case Metadata

- **case_id:** {case["case_id"]}
- **student_name:** {case["student_name"]}

{markdown_mapping(case["student_profile"])}

# Risk Assessment

{markdown_mapping(case["risk_assessment"])}

# Risk Factors

{markdown_list(case["risk_factors"])}

# Root Cause Analysis

{markdown_list(case["root_cause_analysis"])}

# Retrieved Evidence-Based Interventions

{markdown_interventions(case["retrieved_evidence_based_interventions"])}

# Evidence Sources

{markdown_evidence_sources(case["evidence_sources"])}

# Generated AI Action Plan

{case["generated_ai_action_plan"]}
"""


def export_cases(student_names: list[str]) -> list[dict[str, Any]]:
    """Export evaluation packages for the provided student names."""
    students = load_students()
    intervention_library = load_intervention_library()
    EVALUATION_DIR.mkdir(exist_ok=True)

    cases = []
    for index, student_name in enumerate(student_names, start=1):
        student = find_student(students, student_name)
        case = build_case(
            case_id=f"case_{index:03d}",
            student=student,
            intervention_library=intervention_library,
        )
        (EVALUATION_DIR / f"{case['case_id']}.md").write_text(
            render_case_markdown(case),
            encoding="utf-8",
        )
        cases.append(case)

    EVALUATION_DATASET_PATH.write_text(
        json.dumps(cases, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return cases


def main() -> None:
    """Generate evaluation packages without calling the AI action-plan pipeline."""
    names = selected_student_names()
    if not names:
        raise ValueError("Add student names to STUDENT_NAMES or pass names as arguments.")

    cases = export_cases(names)
    print(f"Exported {len(cases)} evaluation cases to {EVALUATION_DIR}")
    print(f"Wrote dataset JSON to {EVALUATION_DATASET_PATH}")


if __name__ == "__main__":
    main()
