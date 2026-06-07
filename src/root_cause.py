from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TrendDirection = Literal["declining", "improving", "stable", "mixed"]

STABLE_TOLERANCE = 2.0
SIGNIFICANT_DECLINE_THRESHOLD = 20.0


@dataclass(frozen=True)
class RootCauseInputs:
    """Input data used to generate root-cause explanations for a student."""

    attendance_p1: float
    attendance_p2: float
    attendance_p3: float
    grade_p1: float
    grade_p2: float
    grade_p3: float
    homework_p1: float
    homework_p2: float
    homework_p3: float
    behavior_notes: str | None = None
    teacher_notes: str | None = None


def _format_percentage(value: float) -> str:
    """Format a percentage without unnecessary decimal places."""
    value = float(value)

    if value.is_integer():
        return f"{int(value)}%"
    return f"{value:.1f}%"


def _format_trend_values(values: tuple[float, float, float]) -> str:
    """Format three reporting-period values for a readable explanation."""
    return " → ".join(_format_percentage(value) for value in values)


def _trend_direction(values: tuple[float, float, float]) -> TrendDirection:
    """Classify a three-period trend as declining, improving, stable, or mixed."""
    first, second, third = values
    max_change = max(values) - min(values)

    if max_change <= STABLE_TOLERANCE:
        return "stable"
    if first > second > third:
        return "declining"
    if first < second < third:
        return "improving"
    return "mixed"


def _trend_explanation(
    label: str,
    values: tuple[float, float, float],
    *,
    declined_noun: str | None = None,
) -> str:
    """Generate one human-readable explanation for a metric trend."""
    direction = _trend_direction(values)
    formatted_values = _format_trend_values(values)
    noun = declined_noun or label

    if direction == "declining":
        total_drop = values[0] - values[2]
        if total_drop >= SIGNIFICANT_DECLINE_THRESHOLD:
            return f"{noun} declined significantly ({formatted_values})."
        return f"{label} declined across reporting periods ({formatted_values})."
    if direction == "improving":
        return f"{label} improved across reporting periods ({formatted_values})."
    if direction == "stable":
        return f"{label} remained relatively stable."
    return f"{label} showed a mixed trend across reporting periods ({formatted_values})."


def _clean_note(note: str | None) -> str | None:
    """Normalize optional note text and treat blanks as missing."""
    if note is None:
        return None

    cleaned = note.strip()
    return cleaned or None


def generate_root_causes(
    attendance_p1: float,
    attendance_p2: float,
    attendance_p3: float,
    grade_p1: float,
    grade_p2: float,
    grade_p3: float,
    homework_p1: float,
    homework_p2: float,
    homework_p3: float,
    behavior_notes: str | None = None,
    teacher_notes: str | None = None,
) -> list[str]:
    """Generate root-cause explanations from reporting-period metrics and notes.

    Args:
        attendance_p1: Attendance percentage for reporting period 1.
        attendance_p2: Attendance percentage for reporting period 2.
        attendance_p3: Attendance percentage for reporting period 3.
        grade_p1: Academic grade percentage for reporting period 1.
        grade_p2: Academic grade percentage for reporting period 2.
        grade_p3: Academic grade percentage for reporting period 3.
        homework_p1: Homework completion percentage for reporting period 1.
        homework_p2: Homework completion percentage for reporting period 2.
        homework_p3: Homework completion percentage for reporting period 3.
        behavior_notes: Optional behavior notes from the student record.
        teacher_notes: Optional teacher observations from the student record.

    Returns:
        A list of human-readable root-cause explanations.
    """
    explanations = [
        _trend_explanation(
            "Attendance",
            (attendance_p1, attendance_p2, attendance_p3),
        ),
        _trend_explanation(
            "Academic performance",
            (grade_p1, grade_p2, grade_p3),
        ),
        _trend_explanation(
            "Homework completion",
            (homework_p1, homework_p2, homework_p3),
            declined_noun="Homework completion",
        ),
    ]

    cleaned_behavior_notes = _clean_note(behavior_notes)
    if cleaned_behavior_notes:
        explanations.append(f"Behavior concerns: {cleaned_behavior_notes}")

    cleaned_teacher_notes = _clean_note(teacher_notes)
    if cleaned_teacher_notes:
        explanations.append(f"Teacher observations: {cleaned_teacher_notes}")

    return explanations


def generate_root_causes_from_inputs(inputs: RootCauseInputs) -> list[str]:
    """Generate root-cause explanations from a RootCauseInputs instance."""
    return generate_root_causes(
        attendance_p1=inputs.attendance_p1,
        attendance_p2=inputs.attendance_p2,
        attendance_p3=inputs.attendance_p3,
        grade_p1=inputs.grade_p1,
        grade_p2=inputs.grade_p2,
        grade_p3=inputs.grade_p3,
        homework_p1=inputs.homework_p1,
        homework_p2=inputs.homework_p2,
        homework_p3=inputs.homework_p3,
        behavior_notes=inputs.behavior_notes,
        teacher_notes=inputs.teacher_notes,
    )
