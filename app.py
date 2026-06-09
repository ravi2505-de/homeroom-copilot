from __future__ import annotations

import logging
from html import escape
from pathlib import Path
from typing import Any

import gradio as gr
import pandas as pd

from src.action_plan_generator import build_action_plan_prompt, clean_action_plan_output
from src.intervention_engine import (
    InterventionRecommendation,
    load_intervention_library,
    recommend_interventions,
)
from src.llm_service import generate_text
from src.risk_engine import RiskAssessment, assess_student_risk
from src.root_cause import generate_root_causes

APP_TITLE = "Homeroom Copilot"
APP_SUBTITLE = "AI-Powered Student Intervention Assistant"

logger = logging.getLogger(__name__)

DATA_CSV_PATH = Path("data/students.csv")
DATA_XLSX_FALLBACK_PATH = Path("data/student_data.csv.xlsx")

RISK_FILTER_OPTIONS = [
    "All",
    "Low Risk",
    "Moderate Risk",
    "High Risk",
    "Critical Risk",
]

RISK_COLORS = {
    "Low": "#22C55E",
    "Moderate": "#F59E0B",
    "High": "#F97316",
    "Critical": "#EF4444",
}

RISK_LABELS = {
    "Low": "Low Risk",
    "Moderate": "Moderate Risk",
    "High": "High Risk",
    "Critical": "Critical Risk",
}

CSS = """
:root {
    --primary: #2563EB;
    --primary-dark: #1D4ED8;
    --primary-soft: #EFF6FF;
    --success: #22C55E;
    --warning: #F59E0B;
    --high: #F97316;
    --critical: #EF4444;
    --background: #F8FAFC;
    --card: #FFFFFF;
    --text: #1E293B;
    --muted: #64748B;
    --border: #DDE7F1;
    --shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
    --shadow-soft: 0 4px 18px rgba(15, 23, 42, 0.055);
}

body,
.gradio-container {
    background: linear-gradient(180deg, #F8FBFF 0%, #F3F7FC 100%) !important;
    color: var(--text) !important;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

body::before {
    background: radial-gradient(
        circle,
        rgba(59, 130, 246, 0.10) 0%,
        rgba(59, 130, 246, 0.04) 35%,
        rgba(59, 130, 246, 0.00) 70%
    );
    border-radius: 50%;
    content: "";
    height: 500px;
    left: 50%;
    pointer-events: none;
    position: fixed;
    top: -250px;
    transform: translateX(-50%);
    width: 900px;
    z-index: 0;
}

.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 28px !important;
    position: relative;
    z-index: 1;
}

.dashboard-header {
    align-items: center;
    display: flex;
    gap: 24px;
    justify-content: space-between;
    margin-bottom: 24px;
    padding: 4px 0 2px;
}

.section-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: var(--shadow);
}

.dashboard-title,
.brand-title {
    margin: 0;
    color: var(--text);
    font-size: 34px;
    font-weight: 850;
    letter-spacing: -0.01em;
    line-height: 1.08;
}

.dashboard-subtitle,
.brand-subtitle {
    margin: 8px 0 0;
    color: var(--muted);
    font-size: 16px;
    font-weight: 550;
    letter-spacing: 0;
}

.teacher-profile {
    align-items: center;
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    min-width: 300px;
    text-align: right;
}

.teacher-avatar {
    align-items: center;
    background: var(--primary-soft);
    border-radius: 999px;
    color: var(--primary);
    display: flex;
    flex: 0 0 auto;
    font-size: 22px;
    height: 44px;
    justify-content: center;
    width: 44px;
}

.teacher-name {
    color: var(--text);
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 4px;
}

.teacher-school,
.teacher-role {
    color: var(--muted);
    font-size: 14px;
    line-height: 1.45;
}

.demo-badge {
    background: #DBEAFE;
    border: 1px solid #BFDBFE;
    border-radius: 999px;
    color: var(--primary-dark);
    display: inline-flex;
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 18px;
    padding: 7px 12px;
    text-transform: uppercase;
}

.status-bar {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: -4px 0 20px;
}

.status-pill {
    align-items: center;
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(203, 213, 225, 0.82);
    border-radius: 999px;
    color: #334155;
    display: flex;
    font-size: 14px;
    font-weight: 650;
    gap: 8px;
    padding: 8px 12px;
}

.status-check {
    align-items: center;
    background: rgba(220, 252, 231, 0.92);
    border-radius: 999px;
    color: #15803D;
    display: inline-flex;
    font-size: 12px;
    font-weight: 900;
    height: 20px;
    justify-content: center;
    width: 20px;
}

.controls-shell {
    margin-bottom: 4px;
}

.controls-shell > .block {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.controls-row {
    align-items: end;
    gap: 18px !important;
}

.controls-row > .form {
    display: grid !important;
    gap: 18px !important;
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    width: 100% !important;
}

.controls-row > .form > div,
.controls-row > div {
    min-width: 0 !important;
    width: 100% !important;
}

.controls-row .block,
.controls-row .form,
.controls-row .input-container {
    min-height: 48px !important;
    width: 100% !important;
}

.advanced-note {
    background: rgba(248, 250, 252, 0.82);
    border: 1px solid var(--border);
    border-radius: 16px;
    color: var(--muted);
    font-size: 14px;
    line-height: 1.55;
    padding: 14px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 16px;
}

.kpi-card {
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid rgba(221, 231, 241, 0.96);
    border-left: 5px solid var(--primary);
    border-radius: 16px;
    box-shadow: var(--shadow-soft);
    min-height: 120px;
    padding: 18px;
    transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.kpi-card:hover {
    border-color: rgba(203, 213, 225, 0.95);
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.075);
    transform: translateY(-2px);
}

.kpi-card.total { border-left-color: var(--primary); }
.kpi-card.low { border-left-color: var(--success); }
.kpi-card.moderate { border-left-color: var(--warning); }
.kpi-card.high { border-left-color: var(--high); }
.kpi-card.critical { border-left-color: var(--critical); }

.kpi-label {
    color: var(--muted);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.kpi-value {
    color: var(--text);
    font-size: 34px;
    font-weight: 800;
    line-height: 1.1;
    margin-top: 10px;
}

.section-card {
    padding: 24px;
}

.filter-card {
    margin-bottom: 20px;
}

.panel-title {
    color: var(--text);
    font-size: 20px;
    font-weight: 800;
    margin: 0 0 16px;
}

.section-eyebrow {
    color: var(--primary);
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
    text-transform: uppercase;
}

.student-name {
    color: var(--text);
    font-size: 26px;
    font-weight: 800;
    margin: 0 0 6px;
}

.student-meta {
    color: var(--muted);
    font-size: 14px;
    margin-bottom: 18px;
}

.risk-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin: 12px 0 18px;
}

.risk-item {
    background: transparent;
    border: 0;
    border-left: 3px solid var(--border);
    border-radius: 0;
    padding: 6px 0 6px 12px;
}

.risk-label {
    color: var(--muted);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.risk-value {
    align-items: center;
    color: var(--text);
    display: flex;
    font-size: 16px;
    font-weight: 800;
    gap: 8px;
    margin-top: 7px;
}

.risk-chip {
    align-items: center;
    border-radius: 999px;
    color: #FFFFFF;
    display: inline-flex;
    font-size: 13px;
    font-weight: 800;
    line-height: 1;
    padding: 7px 10px;
}

.risk-dot {
    border-radius: 999px;
    display: inline-block;
    height: 10px;
    width: 10px;
}

.root-list {
    margin: 10px 0 0;
    padding-left: 20px;
}

.root-cause-scroll {
    box-sizing: border-box;
    height: 180px;
    min-height: 180px;
    max-height: 180px;
    overflow-y: auto;
    padding-right: 8px;
}

.root-list li {
    color: var(--text);
    line-height: 1.55;
    margin-bottom: 8px;
}

.analysis-subsection {
    border-top: 1px solid var(--border);
    margin-top: 18px;
    padding-top: 18px;
}

.trend-strip {
    background: transparent;
    border: 0;
    border-left: 3px solid var(--primary);
    border-radius: 0;
    color: var(--muted);
    font-size: 14px;
    line-height: 1.5;
    padding: 4px 0 4px 14px;
}

.placeholder-box {
    background: #EFF6FF;
    border: 1px dashed #93C5FD;
    border-radius: 16px;
    color: #1D4ED8;
    font-weight: 700;
    line-height: 1.45;
    padding: 16px 18px;
}

.placeholder-title {
    color: #1E40AF;
    font-size: 15px;
    font-weight: 850;
    margin-bottom: 4px;
}

.placeholder-copy {
    color: #2563EB;
    font-size: 14px;
    font-weight: 650;
}

.intervention-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-height: none;
    overflow: visible;
    padding-right: 6px;
}

.recommendations-container {
    box-sizing: border-box;
    height: 550px;
    max-height: 550px;
    overflow-y: auto;
    padding-right: 6px;
}

.balanced-panel {
    height: 840px !important;
    min-height: 840px !important;
    overflow: hidden !important;
}

.balanced-panel > .html-container {
    height: 100% !important;
    min-height: 0 !important;
}

.balanced-panel .section-card {
    display: flex;
    flex-direction: column;
    box-shadow: none;
    height: 100%;
    overflow: hidden;
}

.analysis-body,
.intervention-body {
    display: flex;
    flex: 1;
    flex-direction: column;
    min-height: 0;
}

.analysis-main-scroll {
    flex: 0 0 auto;
    min-height: auto;
    overflow: visible;
    padding-right: 0;
}

.intervention-output-wrap {
    display: flex;
    flex: 0 0 auto;
    flex-direction: column;
    min-height: 0;
}

.intervention-output-wrap > .html-container,
.intervention-output-wrap > .block,
.intervention-output-wrap > div {
    display: flex;
    flex: 0 0 auto;
    flex-direction: column;
    min-height: 0;
}

.intervention-output-wrap .placeholder-box {
    margin-top: 0;
}

.action-plan-shell {
    border-top: 1px solid rgba(226, 232, 240, 0.9);
    margin-top: 18px;
    padding-top: 18px;
}

.action-plan-output {
    background: rgba(248, 250, 252, 0.84);
    border: 1px solid rgba(226, 232, 240, 0.92);
    border-radius: 16px;
    height: 650px;
    max-height: 650px;
    overflow-y: auto;
    padding: 16px 18px;
}

.action-plan-output h1 {
    color: var(--text);
    font-size: 20px;
    font-weight: 850;
    margin-top: 0;
}

.action-plan-output h2 {
    color: var(--text);
    font-size: 16px;
    font-weight: 800;
    margin-top: 18px;
}

.action-plan-output li {
    color: var(--text);
    line-height: 1.5;
    margin-bottom: 6px;
}

.action-plan-output p {
    color: var(--muted);
    line-height: 1.5;
}

.intervention-card {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(221, 231, 241, 0.96);
    border-left: 5px solid var(--primary);
    border-radius: 16px;
    box-shadow: var(--shadow-soft);
    padding: 18px;
}

.intervention-card h2 {
    color: var(--text);
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0;
    margin: 0 0 6px;
}

.intervention-category {
    color: var(--primary);
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 14px;
    text-transform: uppercase;
}

.intervention-section-title {
    color: var(--text);
    font-size: 14px;
    font-weight: 800;
    margin: 14px 0 6px;
}

.intervention-card ul {
    margin: 0;
    padding-left: 20px;
}

.intervention-card li {
    color: var(--text);
    line-height: 1.5;
    margin-bottom: 6px;
}

.intervention-meta {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.45;
    margin-top: 12px;
}

.intervention-meta a {
    color: var(--primary);
    font-weight: 700;
    text-decoration: none;
}

.intervention-meta a:hover {
    text-decoration: underline;
}

button.primary-button {
    background: var(--primary) !important;
    border: 0 !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.2) !important;
    color: #FFFFFF !important;
    flex: 0 0 56px !important;
    font-weight: 800 !important;
    height: 56px !important;
    max-width: 320px !important;
    min-height: 56px !important;
    margin: 0 auto 18px !important;
    transition: transform 180ms ease, box-shadow 180ms ease, background-color 180ms ease !important;
    width: 100% !important;
}

.primary-button {
    max-width: 320px !important;
    margin: 0 auto 18px !important;
}

.primary-button button {
    height: 56px !important;
    min-height: 56px !important;
}

button.primary-button:hover {
    background: var(--primary-dark) !important;
    box-shadow: 0 10px 22px rgba(37, 99, 235, 0.24) !important;
    filter: none;
    transform: translateY(-1px);
}

.block,
.form,
.input-container,
.wrap {
    border-radius: 14px !important;
}

label,
.gr-input-label {
    color: var(--text) !important;
    font-weight: 800 !important;
}

details {
    border-radius: 16px !important;
}

@media (max-width: 980px) {
    .dashboard-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .teacher-profile {
        justify-content: flex-start;
        min-width: 0;
        text-align: left;
    }

    .kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .controls-row {
        display: grid !important;
        grid-template-columns: 1fr !important;
    }

    .risk-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 640px) {
    .gradio-container {
        padding: 18px !important;
    }

    .dashboard-title {
        font-size: 30px;
    }

    .brand-card,
    .section-card {
        border-radius: 16px;
    }

    .kpi-grid {
        grid-template-columns: 1fr;
    }

    .risk-grid {
        grid-template-columns: 1fr;
    }
}
"""


def load_students() -> pd.DataFrame:
    """Load student data, preferring data/students.csv with a workbook fallback."""
    if DATA_CSV_PATH.exists():
        dataframe = pd.read_csv(DATA_CSV_PATH)
    elif DATA_XLSX_FALLBACK_PATH.exists():
        dataframe = pd.read_excel(DATA_XLSX_FALLBACK_PATH)
    else:
        raise FileNotFoundError(
            "Could not find data/students.csv or data/student_data.csv.xlsx."
        )

    return enrich_students(dataframe)


def enrich_students(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Calculate risk fields for every student in the dataset."""
    enriched = dataframe.copy()
    risk_profiles = [
        assess_student_risk(
            attendance=float(row["attendance_p3"]),
            grades=float(row["grade_p3"]),
            homework=float(row["homework_p3"]),
            behavior_incidents=int(row["behavior_incident_count"]),
        )
        for _, row in enriched.iterrows()
    ]

    for field_name in RiskAssessment.__annotations__:
        enriched[field_name] = [profile[field_name] for profile in risk_profiles]

    enriched["student_display"] = enriched.apply(
        lambda row: f"{row['student_name']} ({row['student_id']})",
        axis=1,
    )
    return enriched


STUDENTS = load_students()


def render_top_header() -> str:
    """Render the public-demo product header."""
    return f"""
    <div class="dashboard-header">
        <div>
            <h1 class="brand-title">{APP_TITLE}</h1>
            <p class="brand-subtitle">{APP_SUBTITLE}</p>
        </div>
        <div class="teacher-profile">
            <div>
                <div class="teacher-name">👤 Sarah Johnson</div>
                <div class="teacher-school">Lincoln Middle School</div>
                <div class="teacher-role">Grade 7 Homeroom Teacher</div>
            </div>
        </div>
    </div>
    """


def render_status_bar() -> str:
    """Render slim dataset and engine status pills."""
    student_count = len(STUDENTS)
    return f"""
    <div class="status-bar">
        <div class="demo-badge">Demo Mode</div>
        <div class="status-pill"><span class="status-check">✓</span>Demo Dataset Active</div>
        <div class="status-pill"><span class="status-check">✓</span>{student_count} Students Loaded</div>
        <div class="status-pill"><span class="status-check">✓</span>Risk Engine Ready</div>
        <div class="status-pill"><span class="status-check">✓</span>Intervention Library Ready</div>
    </div>
    """


def risk_filter_to_value(risk_filter: str) -> str | None:
    """Convert a UI filter label to an internal risk value."""
    if risk_filter == "All":
        return None
    return risk_filter.replace(" Risk", "")


def filtered_students(risk_filter: str) -> pd.DataFrame:
    """Return students matching the selected risk filter."""
    risk_value = risk_filter_to_value(risk_filter)
    if risk_value is None:
        return STUDENTS
    return STUDENTS[STUDENTS["overall_risk"] == risk_value]


def student_choices(risk_filter: str) -> list[str]:
    """Return dropdown choices for the selected risk category."""
    return filtered_students(risk_filter)["student_display"].tolist()


def get_student(student_display: str | None) -> pd.Series | None:
    """Find a selected student row by dropdown display value."""
    if not student_display:
        return None

    matches = STUDENTS[STUDENTS["student_display"] == student_display]
    if matches.empty:
        return None
    return matches.iloc[0]


def render_kpi_cards() -> str:
    """Render dashboard KPI cards as HTML."""
    total_students = len(STUDENTS)
    counts = STUDENTS["overall_risk"].value_counts().to_dict()

    cards = [
        ("Total Students", total_students, "total"),
        ("Low Risk", counts.get("Low", 0), "low"),
        ("Moderate Risk", counts.get("Moderate", 0), "moderate"),
        ("High Risk", counts.get("High", 0), "high"),
        ("Critical Risk", counts.get("Critical", 0), "critical"),
    ]

    card_html = "".join(
        f"""
        <div class="kpi-card {css_class}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """
        for label, value, css_class in cards
    )
    return f'<div class="kpi-grid">{card_html}</div>'


def render_risk_item(label: str, risk_value: str) -> str:
    """Render one risk metric with a color indicator."""
    color = RISK_COLORS.get(risk_value, "#64748B")
    display = RISK_LABELS.get(risk_value, risk_value)
    return f"""
    <div class="risk-item">
        <div class="risk-label">{escape(label)}</div>
        <div class="risk-value">
            <span class="risk-chip" style="background:{color};">{escape(display)}</span>
        </div>
    </div>
    """


def render_analysis(student_display: str | None) -> str:
    """Render the selected student's analysis panel."""
    student = get_student(student_display)
    if student is None:
        return """
        <div class="section-card">
            <div class="section-eyebrow">Risk Assessment</div>
            <h2 class="panel-title">Student Analysis</h2>
            <div class="analysis-body">
                <p class="student-meta">Select a student to view their risk profile.</p>
            </div>
        </div>
        """

    root_causes = student_root_causes(student)
    root_cause_items = "".join(f"<li>{escape(item)}</li>" for item in root_causes)
    trend_summary = " ".join(escape(item) for item in root_causes[:3])

    risk_items = "".join(
        [
            render_risk_item("Overall Risk", str(student["overall_risk"])),
            render_risk_item("Attendance Risk", str(student["attendance_risk"])),
            render_risk_item("Academic Risk", str(student["academic_risk"])),
            render_risk_item("Homework Risk", str(student["homework_risk"])),
            render_risk_item("Behavior Risk", str(student["behavior_risk"])),
            f"""
            <div class="risk-item">
                <div class="risk-label">Engagement Score</div>
                <div class="risk-value">{float(student["engagement_score"]):.2f}</div>
            </div>
            """,
        ]
    )

    return f"""
    <div class="section-card">
        <div class="section-eyebrow">Risk Assessment</div>
        <h2 class="panel-title">Student Analysis</h2>
        <h3 class="student-name">{escape(str(student["student_name"]))}</h3>
        <div class="student-meta">
            Grade {escape(str(int(student["grade_level"])))} · Homeroom {escape(str(student["homeroom"]))}
        </div>

        <div class="analysis-body">
            <div class="analysis-main-scroll">
                <div class="analysis-subsection">
                    <h3 class="panel-title">Risk Profile</h3>
                    <div class="risk-grid">{risk_items}</div>
                </div>

                <div class="analysis-subsection">
                    <h3 class="panel-title">Trend Analysis</h3>
                    <div class="trend-strip">{trend_summary}</div>
                </div>

                <div class="analysis-subsection">
                    <h3 class="panel-title">Root Causes</h3>
                    <div class="root-cause-scroll">
                        <ul class="root-list">{root_cause_items}</ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """


def student_root_causes(student: pd.Series) -> list[str]:
    """Generate root-cause explanations for a selected student row."""
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


def render_intervention_placeholder() -> str:
    """Render placeholder content before intervention retrieval."""
    return """
    <div class="recommendations-container">
        <div class="placeholder-box">
            <div class="placeholder-title">No recommendations generated yet.</div>
            <div class="placeholder-copy">Click Generate Intervention Plan.</div>
        </div>
    </div>
    """


def render_no_interventions() -> str:
    """Render a friendly empty state when no recommendations are found."""
    return """
    <div class="recommendations-container">
        <div class="placeholder-box">
            No suitable interventions found.
        </div>
    </div>
    """


def render_intervention_error(message: str) -> str:
    """Render a user-friendly intervention loading error."""
    return f"""
    <div class="recommendations-container">
        <div class="placeholder-box">
            Unable to load intervention recommendations. {escape(message)}
        </div>
    </div>
    """


def render_bullet_list(items: list[str]) -> str:
    """Render a list of strings as HTML bullet points."""
    if not items:
        return "<ul><li>No details provided.</li></ul>"
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def render_intervention_card(recommendation: InterventionRecommendation) -> str:
    """Render one intervention recommendation as a dashboard card."""
    reference_url = escape(recommendation.reference_url)
    reference_link = (
        f'<a href="{reference_url}" target="_blank" rel="noreferrer">{reference_url}</a>'
        if reference_url
        else "No reference URL provided."
    )

    return f"""
    <div class="intervention-card">
        <h2>{escape(recommendation.intervention_name)}</h2>
        <div class="intervention-category">{escape(recommendation.category)}</div>

        <div class="intervention-section-title">Summary</div>
        {render_bullet_list(recommendation.summary)}

        <div class="intervention-section-title">Expected Benefits</div>
        {render_bullet_list(recommendation.expected_benefits)}

        <div class="intervention-section-title">Why This Recommendation</div>
        <div class="intervention-meta">{escape(recommendation.recommendation_reason)}</div>

        <div class="intervention-meta">
            <strong>Evidence Level:</strong> {escape(recommendation.evidence_level or "Not specified")}<br>
            <strong>Source:</strong> {escape(recommendation.source or "Not specified")}<br>
            <strong>Reference URL:</strong> {reference_link}
        </div>
    </div>
    """


def student_risk_profile(student: pd.Series) -> dict[str, str]:
    """Return the risk profile dictionary for a selected student record."""
    assessment = assess_student_risk(
        attendance=float(student["attendance_p3"]),
        grades=float(student["grade_p3"]),
        homework=float(student["homework_p3"]),
        behavior_incidents=int(student["behavior_incident_count"]),
    )
    return {field_name: str(value) for field_name, value in assessment.items()}


def recommendation_to_prompt_context(
    recommendation: InterventionRecommendation,
    intervention_library: list[dict[str, Any]],
) -> dict[str, Any]:
    """Merge a ranked recommendation with its source library metadata."""
    matching_intervention = next(
        (
            intervention
            for intervention in intervention_library
            if str(intervention.get("intervention_name", ""))
            == recommendation.intervention_name
        ),
        {},
    )

    return {
        **matching_intervention,
        "intervention_name": recommendation.intervention_name,
        "category": recommendation.category,
        "summary": recommendation.summary,
        "expected_benefits": recommendation.expected_benefits,
        "evidence_level": recommendation.evidence_level,
        "source": recommendation.source,
        "reference_url": recommendation.reference_url,
        "relevance_score": recommendation.relevance_score,
        "recommendation_reason_template": matching_intervention.get(
            "recommendation_reason_template",
            recommendation.recommendation_reason,
        ),
        "recommendation_reason": recommendation.recommendation_reason,
    }


def format_action_plan_source(intervention: dict[str, Any]) -> str:
    """Format one intervention source as a Markdown link when a URL exists."""
    intervention_name = str(intervention.get("intervention_name", "")).strip()
    reference_url = str(intervention.get("reference_url", "")).strip()

    if not intervention_name:
        return "Unnamed intervention"
    if reference_url:
        safe_name = intervention_name.replace("[", "\\[").replace("]", "\\]")
        safe_url = reference_url.replace(")", "%29")
        return f"[{safe_name}]({safe_url})"
    return intervention_name


def generate_ai_action_plan(student_record: pd.Series) -> str:
    """Generate a teacher-facing AI action plan for a selected student."""
    risk_profile = student_risk_profile(student_record)
    root_causes = student_root_causes(student_record)
    intervention_library = load_intervention_library()
    recommendations = recommend_interventions(
        root_causes=root_causes,
        risk_profile=risk_profile,
        intervention_library=intervention_library,
        max_results=5,
    )
    prompt_interventions = [
        recommendation_to_prompt_context(recommendation, intervention_library)
        for recommendation in recommendations
    ]

    logger.info("Building action plan prompt...")
    prompt = build_action_plan_prompt(
        student_name=str(student_record["student_name"]),
        risk_profile=risk_profile,
        root_causes=root_causes,
        recommended_interventions=prompt_interventions,
    )

    logger.info("Generating response with Qwen...")
    action_plan = generate_text(prompt)
    action_plan = clean_action_plan_output(
        generated_text=action_plan,
        student_name=str(student_record["student_name"]),
        source_names=[
            format_action_plan_source(intervention)
            for intervention in prompt_interventions
        ],
    )
    logger.info("Action plan generated successfully.")
    return action_plan


def generate_intervention_plan(student_display: str | None) -> str:
    """Generate and render intervention recommendations for a selected student."""
    student = get_student(student_display)
    if student is None:
        return render_intervention_error("Select a student first.")

    try:
        intervention_library = load_intervention_library()
    except (FileNotFoundError, ValueError, OSError) as error:
        return render_intervention_error(str(error))

    root_causes = student_root_causes(student)
    risk_profile = student_risk_profile(student)
    recommendations = recommend_interventions(
        root_causes=root_causes,
        risk_profile=risk_profile,
        intervention_library=intervention_library,
        max_results=5,
    )

    if not recommendations:
        return render_no_interventions()

    cards = "".join(render_intervention_card(recommendation) for recommendation in recommendations)
    return f'<div class="recommendations-container"><div class="intervention-list">{cards}</div></div>'


def render_action_plan_placeholder() -> str:
    """Render placeholder markdown before AI action-plan generation."""
    return (
        "No AI action plan generated yet.\n\n"
        "Click **Generate AI Action Plan** to create a teacher-facing roadmap."
    )


def generate_ai_action_plan_for_student(student_display: str | None) -> str:
    """Generate an AI action plan for the currently selected student."""
    student = get_student(student_display)
    if student is None:
        return "Unable to generate an AI action plan. Select a student first."

    student_name = str(student["student_name"])
    logger.info("Action plan generation requested for %s.", student_name)
    try:
        action_plan = generate_ai_action_plan(student)
    except Exception as error:
        logger.exception("Action plan generation failed for %s.", student_name)
        return f"Unable to generate AI action plan: {error}"

    logger.info("Action plan generation completed for %s.", student_name)
    return action_plan


def update_student_dropdown(risk_filter: str) -> tuple[Any, str, str]:
    """Update student options when the risk category filter changes."""
    choices = student_choices(risk_filter)
    if not choices:
        selected = "No students available"
        choices = [selected]
        analysis_html = render_analysis(None)
    else:
        selected = choices[0]
        analysis_html = render_analysis(selected)

    return (
        gr.Dropdown(choices=choices, value=selected, interactive=True),
        analysis_html,
        render_action_plan_placeholder(),
    )


def update_student_analysis(student_display: str | None) -> tuple[str, str]:
    """Update the analysis panel when a student is selected."""
    if student_display == "No students available":
        student_display = None
    return (
        render_analysis(student_display),
        render_action_plan_placeholder(),
    )


initial_choices = student_choices("All")
initial_student = initial_choices[0] if initial_choices else None

theme = gr.themes.Soft(
    primary_hue="blue",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_background_fill="#F8FAFC",
    button_primary_background_fill="#2563EB",
    button_primary_background_fill_hover="#1D4ED8",
    button_primary_text_color="#FFFFFF",
    block_background_fill="#FFFFFF",
    block_border_color="#E2E8F0",
    block_radius="16px",
)

with gr.Blocks(
    title=APP_TITLE,
    analytics_enabled=False,
) as demo:
    gr.HTML(render_top_header())

    gr.HTML(render_kpi_cards())
    gr.HTML(render_status_bar())

    with gr.Column(elem_classes=["controls-shell"]):
        with gr.Row(elem_classes=["controls-row"]):
            risk_dropdown = gr.Dropdown(
                label="Risk Category",
                choices=RISK_FILTER_OPTIONS,
                value="All",
                interactive=True,
                scale=1,
            )
            student_dropdown = gr.Dropdown(
                label="Student Selector",
                choices=initial_choices,
                value=initial_student,
                interactive=True,
                scale=1,
            )

    with gr.Row(equal_height=True):
        with gr.Column(scale=1, min_width=0, elem_classes=["balanced-panel"]):
            analysis_panel = gr.HTML(render_analysis(initial_student))

        with gr.Column(scale=1, min_width=0, elem_classes=["section-card", "balanced-panel"]):
            gr.Markdown("## AI Action Plan")
            generate_ai_button = gr.Button(
                "Generate AI Action Plan",
                variant="primary",
                elem_classes=["primary-button"],
            )
            action_plan_panel = gr.Markdown(
                render_action_plan_placeholder(),
                elem_classes=["action-plan-output"],
            )

    with gr.Accordion("Advanced Options", open=False):
        gr.Markdown(
            """
            **Custom Dataset Upload**

            Coming Soon

            Future versions will support:

            - CSV ingestion
            - Column mapping
            - Data validation
            - Automatic transformation pipelines
            """
        )
        gr.HTML(
            """
            <div class="advanced-note">
                This prototype focuses on the intervention workflow and currently uses a curated demonstration dataset.
            </div>
            """
        )

    risk_dropdown.change(
        fn=update_student_dropdown,
        inputs=risk_dropdown,
        outputs=[
            student_dropdown,
            analysis_panel,
            action_plan_panel,
        ],
    )
    student_dropdown.change(
        fn=update_student_analysis,
        inputs=student_dropdown,
        outputs=[analysis_panel, action_plan_panel],
    )
    generate_ai_button.click(
        fn=generate_ai_action_plan_for_student,
        inputs=student_dropdown,
        outputs=action_plan_panel,
    )


if __name__ == "__main__":
    demo.launch(theme=theme, css=CSS)
