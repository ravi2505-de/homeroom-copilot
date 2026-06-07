from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import gradio as gr
import pandas as pd

from src.intervention_engine import (
    InterventionRecommendation,
    load_intervention_library,
    recommend_interventions,
)
from src.risk_engine import RiskAssessment, assess_student_risk
from src.root_cause import generate_root_causes

APP_TITLE = "Homeroom Copilot"
APP_SUBTITLE = "AI-Powered Early Warning and Intervention Support System"

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
    --success: #22C55E;
    --warning: #F59E0B;
    --high: #F97316;
    --critical: #EF4444;
    --background: #F8FAFC;
    --card: #FFFFFF;
    --text: #1E293B;
    --muted: #64748B;
    --border: #E2E8F0;
}

body,
.gradio-container {
    background: var(--background) !important;
    color: var(--text) !important;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

.gradio-container {
    max-width: 1280px !important;
    margin: 0 auto !important;
    padding: 28px !important;
}

.dashboard-header {
    margin-bottom: 24px;
}

.dashboard-title {
    margin: 0;
    color: var(--text);
    font-size: 36px;
    font-weight: 800;
    letter-spacing: 0;
}

.dashboard-subtitle {
    margin: 8px 0 0;
    color: var(--muted);
    font-size: 16px;
    font-weight: 500;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 22px;
}

.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 5px solid var(--primary);
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.07);
    padding: 18px;
    transition: transform 160ms ease, box-shadow 160ms ease;
}

.kpi-card:hover {
    box-shadow: 0 16px 38px rgba(15, 23, 42, 0.11);
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
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: 0 12px 34px rgba(15, 23, 42, 0.07);
    padding: 22px;
}

.filter-card {
    margin-bottom: 22px;
}

.panel-title {
    color: var(--text);
    font-size: 20px;
    font-weight: 800;
    margin: 0 0 16px;
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
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin: 18px 0;
}

.risk-item {
    background: #F8FAFC;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 14px;
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

.root-list li {
    color: var(--text);
    line-height: 1.55;
    margin-bottom: 8px;
}

.placeholder-box {
    background: #EFF6FF;
    border: 1px dashed #93C5FD;
    border-radius: 16px;
    color: #1D4ED8;
    font-weight: 700;
    padding: 18px;
}

.intervention-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-height: 680px;
    overflow-y: auto;
    padding-right: 6px;
}

.intervention-card {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-left: 5px solid var(--primary);
    border-radius: 16px;
    box-shadow: 0 10px 26px rgba(15, 23, 42, 0.07);
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
    box-shadow: 0 12px 24px rgba(37, 99, 235, 0.22) !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    min-height: 48px !important;
}

button.primary-button:hover {
    filter: brightness(0.97);
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

@media (max-width: 980px) {
    .kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .risk-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 640px) {
    .gradio-container {
        padding: 18px !important;
    }

    .dashboard-title {
        font-size: 30px;
    }

    .kpi-grid {
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
            <span class="risk-dot" style="background:{color};"></span>
            {escape(display)}
        </div>
    </div>
    """


def render_analysis(student_display: str | None) -> str:
    """Render the selected student's analysis panel."""
    student = get_student(student_display)
    if student is None:
        return """
        <div class="section-card">
            <h2 class="panel-title">Student Analysis</h2>
            <p class="student-meta">Select a student to view their risk profile.</p>
        </div>
        """

    root_causes = student_root_causes(student)
    root_cause_items = "".join(f"<li>{escape(item)}</li>" for item in root_causes)

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
        <h2 class="panel-title">Student Analysis</h2>
        <h3 class="student-name">{escape(str(student["student_name"]))}</h3>
        <div class="student-meta">
            Grade {escape(str(int(student["grade_level"])))} · Homeroom {escape(str(student["homeroom"]))}
        </div>
        <div class="risk-grid">{risk_items}</div>
        <h3 class="panel-title">Root Causes</h3>
        <ul class="root-list">{root_cause_items}</ul>
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
    <div class="placeholder-box">
        Click Generate Intervention Plan to retrieve evidence-based recommendations.
    </div>
    """


def render_no_interventions() -> str:
    """Render a friendly empty state when no recommendations are found."""
    return """
    <div class="placeholder-box">
        No suitable interventions found.
    </div>
    """


def render_intervention_error(message: str) -> str:
    """Render a user-friendly intervention loading error."""
    return f"""
    <div class="placeholder-box">
        Unable to load intervention recommendations. {escape(message)}
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

        <div class="intervention-meta">
            <strong>Evidence Level:</strong> {escape(recommendation.evidence_level or "Not specified")}<br>
            <strong>Source:</strong> {escape(recommendation.source or "Not specified")}<br>
            <strong>Reference URL:</strong> {reference_link}
        </div>
    </div>
    """


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
    recommendations = recommend_interventions(
        root_causes=root_causes,
        intervention_library=intervention_library,
        max_results=5,
        overall_risk=str(student["overall_risk"]),
    )

    if not recommendations:
        return render_no_interventions()

    cards = "".join(render_intervention_card(recommendation) for recommendation in recommendations)
    return f'<div class="intervention-list">{cards}</div>'


def update_student_dropdown(risk_filter: str) -> tuple[Any, str, str]:
    """Update student options when the risk category filter changes."""
    choices = student_choices(risk_filter)
    selected = choices[0] if choices else None
    return (
        gr.update(choices=choices, value=selected),
        render_analysis(selected),
        render_intervention_placeholder(),
    )


def update_student_analysis(student_display: str | None) -> tuple[str, str]:
    """Update the analysis panel when a student is selected."""
    return render_analysis(student_display), render_intervention_placeholder()


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
    gr.HTML(
        f"""
        <div class="dashboard-header">
            <h1 class="dashboard-title">{APP_TITLE}</h1>
            <p class="dashboard-subtitle">{APP_SUBTITLE}</p>
        </div>
        """
    )

    gr.HTML(render_kpi_cards())

    with gr.Column(elem_classes=["section-card", "filter-card"]):
        gr.Markdown("### Filters")
        with gr.Row():
            risk_dropdown = gr.Dropdown(
                label="Risk Category",
                choices=RISK_FILTER_OPTIONS,
                value="All",
                interactive=True,
            )
            student_dropdown = gr.Dropdown(
                label="Student",
                choices=initial_choices,
                value=initial_student,
                interactive=True,
            )

    with gr.Row():
        with gr.Column(scale=7):
            analysis_panel = gr.HTML(render_analysis(initial_student))

        with gr.Column(scale=5, elem_classes=["section-card"]):
            gr.Markdown("## Intervention Plan")
            generate_button = gr.Button(
                "Generate Intervention Plan",
                variant="primary",
                elem_classes=["primary-button"],
            )
            intervention_panel = gr.HTML(render_intervention_placeholder())

    risk_dropdown.change(
        fn=update_student_dropdown,
        inputs=risk_dropdown,
        outputs=[student_dropdown, analysis_panel, intervention_panel],
    )
    student_dropdown.change(
        fn=update_student_analysis,
        inputs=student_dropdown,
        outputs=[analysis_panel, intervention_panel],
    )
    generate_button.click(
        fn=generate_intervention_plan,
        inputs=student_dropdown,
        outputs=intervention_panel,
    )


if __name__ == "__main__":
    demo.launch(theme=theme, css=CSS)
