from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

RiskLevel = Literal["Low", "Moderate", "High", "Critical"]

ENGAGEMENT_ATTENDANCE_WEIGHT = 0.4
ENGAGEMENT_HOMEWORK_WEIGHT = 0.4
ENGAGEMENT_GRADE_WEIGHT = 0.2


class RiskAssessment(TypedDict):
    """Structured risk output for a single student."""

    attendance_risk: RiskLevel
    academic_risk: RiskLevel
    homework_risk: RiskLevel
    behavior_risk: RiskLevel
    engagement_score: float
    engagement_risk: RiskLevel
    overall_risk: RiskLevel


_RISK_ORDER: dict[RiskLevel, int] = {
    "Low": 0,
    "Moderate": 1,
    "High": 2,
    "Critical": 3,
}


@dataclass(frozen=True)
class StudentMetrics:
    """Input metrics used to calculate student risk levels.

    Scores are expected on a 0-100 scale, while behavior incidents are a
    non-negative count over the relevant reporting period.
    """

    attendance: float
    grades: float
    homework: float
    behavior_incidents: int


def validate_percentage(value: float, field_name: str) -> None:
    """Validate that a percentage value is within the inclusive 0-100 range.

    Args:
        value: Percentage value to validate.
        field_name: Name of the field being validated.

    Raises:
        ValueError: If the value is less than 0 or greater than 100.
    """
    if value < 0 or value > 100:
        raise ValueError(
            f"{field_name} must be between 0 and 100. Got {value}."
        )


def attendance_risk(attendance: float) -> RiskLevel:
    """Classify risk from an attendance percentage."""
    if attendance >= 95:
        return "Low"
    if attendance >= 90:
        return "Moderate"
    if attendance >= 80:
        return "High"
    return "Critical"


def academic_risk(grades: float) -> RiskLevel:
    """Classify risk from an academic grade percentage."""
    if grades >= 90:
        return "Low"
    if grades >= 75:
        return "Moderate"
    if grades >= 60:
        return "High"
    return "Critical"


def homework_risk(homework: float) -> RiskLevel:
    """Classify risk from a homework completion percentage."""
    if homework >= 90:
        return "Low"
    if homework >= 75:
        return "Moderate"
    if homework >= 50:
        return "High"
    return "Critical"


def behavior_risk(behavior_incidents: int) -> RiskLevel:
    """Classify risk from the number of behavior incidents."""
    if behavior_incidents <= 0:
        return "Low"
    if behavior_incidents <= 2:
        return "Moderate"
    if behavior_incidents <= 5:
        return "High"
    return "Critical"


def engagement_score(attendance: float, homework: float, grades: float) -> float:
    """Calculate the weighted engagement score.

    Formula: 0.4 * attendance + 0.4 * homework + 0.2 * grades.
    """
    return round(
        (ENGAGEMENT_ATTENDANCE_WEIGHT * attendance)
        + (ENGAGEMENT_HOMEWORK_WEIGHT * homework)
        + (ENGAGEMENT_GRADE_WEIGHT * grades),
        2,
    )


def engagement_risk(score: float) -> RiskLevel:
    """Classify risk from the weighted engagement score.

    Engagement risk uses dedicated thresholds:
    - Low: score >= 85
    - Moderate: score >= 70 and score < 85
    - High: score >= 55 and score < 70
    - Critical: score < 55
    """
    if score >= 85:
        return "Low"
    if score >= 70:
        return "Moderate"
    if score >= 55:
        return "High"
    return "Critical"


def overall_risk(*risks: RiskLevel) -> RiskLevel:
    """Return the highest risk level across all provided risk categories."""
    return max(risks, key=lambda risk: _RISK_ORDER[risk])


def assess_student_risk(
    attendance: float,
    grades: float,
    homework: float,
    behavior_incidents: int,
) -> RiskAssessment:
    """Create a complete risk assessment for one student.

    Args:
        attendance: Attendance percentage from 0 to 100.
        grades: Academic grade percentage from 0 to 100.
        homework: Homework completion percentage from 0 to 100.
        behavior_incidents: Count of behavior incidents.

    Returns:
        A dictionary containing category risk levels, engagement score,
        engagement risk, and the overall highest risk level.
    """
    validate_percentage(attendance, "attendance")
    validate_percentage(grades, "grades")
    validate_percentage(homework, "homework")
    if behavior_incidents < 0:
        raise ValueError("behavior_incidents must be non-negative.")

    attendance_level = attendance_risk(attendance)
    academic_level = academic_risk(grades)
    homework_level = homework_risk(homework)
    behavior_level = behavior_risk(behavior_incidents)
    score = engagement_score(attendance, homework, grades)
    engagement_level = engagement_risk(score)

    return {
        "attendance_risk": attendance_level,
        "academic_risk": academic_level,
        "homework_risk": homework_level,
        "behavior_risk": behavior_level,
        "engagement_score": score,
        "engagement_risk": engagement_level,
        "overall_risk": overall_risk(
            attendance_level,
            academic_level,
            homework_level,
            behavior_level,
            engagement_level,
        ),
    }


def assess_metrics(metrics: StudentMetrics) -> RiskAssessment:
    """Create a risk assessment from a StudentMetrics instance."""
    return assess_student_risk(
        attendance=metrics.attendance,
        grades=metrics.grades,
        homework=metrics.homework,
        behavior_incidents=metrics.behavior_incidents,
    )
