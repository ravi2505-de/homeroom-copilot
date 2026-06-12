---
title: Homeroom Copilot
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.17.3
python_version: "3.11"
app_file: app.py
suggested_hardware: t4-small
pinned: false
license: mit
short_description: AI copilot for student intervention planning.
---

# 🎓 Homeroom Copilot

**AI-Powered Student Intervention Planning for Educators**

Homeroom Copilot helps educators identify at-risk students, understand the underlying causes of academic and behavioral challenges, retrieve evidence-based interventions, and generate structured AI-supported action plans.

Built for the **Hugging Face Build Small Hackathon** using **Qwen 2.5 1.5B Instruct**.

This experiment branch runs the Action Plan Generator with **llama.cpp**,
`llama-cpp-python`, CUDA offload, and the
`Qwen/Qwen2.5-1.5B-Instruct-GGUF` Q4_K_M model.

---

## 🚀 Links

### Live Demo

https://huggingface.co/spaces/ravi2505/llama-experiment

### Technical Article

https://medium.com/@ravimutthina/homeroom-copilot-building-an-ai-decision-support-system-for-student-intervention-planning-3e34af800831

### Open Development Traces

https://huggingface.co/datasets/ravi2505/homeroom-copilot-open-traces

---

## 🏅 Hackathon Features

Homeroom Copilot includes features aligned with the following Build Small Hackathon categories:

* 🎯 Well-Tuned — Fine-tuned model integration
* 🎨 Off-Brand — Custom Gradio dashboard and UI styling
* 📡 Sharing is Caring — Published development traces
* 📓 Field Notes — Technical write-up documenting the project journey

---

## ⚡ Quick Start

1. Select a student from the dropdown menu.
2. Review the Risk Assessment, Trend Analysis, and Root Cause Analysis.
3. Click **Generate AI Action Plan**.
4. Review the evidence-based interventions and AI-generated recommendations.
5. Explore students across different risk levels to see how recommendations adapt to individual needs.

---

## 📚 Problem

Teachers often manage large classrooms while monitoring attendance, academic performance, engagement, homework completion, and behavioral indicators.

While many educational dashboards identify students who may be struggling, they rarely explain why those students are at risk or provide actionable next steps.

Homeroom Copilot was designed to bridge this gap by combining:

* Student Risk Assessment
* Root Cause Analysis
* Trend Analysis
* Evidence-Based Intervention Retrieval
* AI Action Plan Generation

into a single educator-friendly workflow.

---

## ✨ Key Features

### Risk Assessment

Evaluates student performance across:

* Attendance
* Academic Performance
* Homework Completion
* Engagement
* Behavior Indicators
* Family Support Signals

Risk Categories:

* Low
* Moderate
* High
* Critical

### Root Cause Analysis

Provides transparent explanations for why a student has been identified as at risk.

Examples include:

* Attendance concerns
* Academic difficulties
* Engagement challenges
* Behavioral concerns
* Family support concerns

### Trend Analysis

Helps educators identify whether student performance is:

* Improving
* Stable
* Worsening

over time.

### Evidence-Based Intervention Retrieval

Retrieves educational intervention strategies from a curated intervention knowledge base.

Recommendations are aligned with identified student needs and root causes.

### AI Action Plans

Uses **Qwen 2.5 1.5B Instruct** to generate structured intervention plans based on:

* Student Profile
* Risk Assessment
* Root Cause Analysis
* Retrieved Interventions

The system generates practical, week-by-week recommendations that educators can use as a starting point for intervention planning.

---

## 🏗️ System Architecture

```text
Student Data
      ↓
Risk Assessment
      ↓
Root Cause Analysis
      ↓
Trend Analysis
      ↓
Evidence-Based Intervention Retrieval
      ↓
AI Action Plan Generation
```

---

## 🤖 Model & Technology Stack

### Model

* Qwen 2.5 1.5B Instruct

### Frontend

* Gradio

### Backend

* Python
* llama.cpp
* llama-cpp-python
* Qwen2.5 1.5B Instruct GGUF

### Deployment

* Hugging Face Spaces

---

## 📊 Evaluation

### Human Evaluation

The system was evaluated using 8 representative student cases:

* 2 Low Risk
* 2 Moderate Risk
* 2 High Risk
* 2 Critical Risk

Evaluation Metrics:

* Relevance
* Correctness
* Root Cause Alignment
* Evidence Alignment
* Actionability
* Clarity
* Overall Quality

### Key Finding

Initial evaluation revealed that Low and Moderate Risk students were receiving overly aggressive intervention plans.

To address this, a risk-aware prompting strategy was introduced to better align intervention intensity with actual student needs.

### Results

Overall Quality improved from:

**3.13 → 3.50**

High Risk and Critical Risk students demonstrated the strongest performance.

---

## 👩‍🏫 User Evaluation

Homeroom Copilot was evaluated by:

* 1 Instructor
* 2 Education Majors
* 1 Teaching Assistant
* 2 Computer Science / AI Students
* 1 General User

### Results

| Metric                      | Score    |
| --------------------------- | -------- |
| Overall Usefulness          | 4.86 / 5 |
| Ease of Use                 | 5.00 / 5 |
| Risk Assessment Quality     | 4.71 / 5 |
| Root Cause Analysis Quality | 4.86 / 5 |
| AI Action Plan Quality      | 4.57 / 5 |

### Adoption Metrics

* 100% would recommend the system
* 100% would use the system

### Reviewer Feedback

> "Many educational dashboards can identify which students are struggling, but they often do not explain why. The breakdown of attendance, engagement, academic performance, and behavioral factors provides actionable information that could help educators make more informed intervention decisions."

— Instructor Reviewer

> "I would love to use this in my future classroom because it would save me a lot of time."

— Education Major

---

## 🔍 Open Development Traces

Development traces were published as sanitized Codex JSONL traces to support transparency and reproducibility.

Included traces:

* Evaluation Framework Creation
* Evaluation Analysis
* Prompt Refinement
* Mobile Responsiveness Improvements
* Dark Mode Improvements
* Scroll UX Improvements

Trace Dataset:

https://huggingface.co/datasets/ravi2505/homeroom-copilot-open-traces

---

## 💻 Running Locally

Clone the repository:

```bash
git clone <REPOSITORY_URL>
cd homeroom-copilot
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open the local Gradio URL in your browser.

---

## 📂 Project Structure

```text
src/
├── risk_assessment.py
├── root_cause_analysis.py
├── intervention_retriever.py
├── action_plan_generator.py

evaluation/
├── case_001.md
├── ...
├── evaluation_dataset.json

scripts/
├── generate_evaluation_cases.py

app.py
README.md
```

---

## 🛣️ Future Work

Potential future enhancements include:

* Student trend visualizations
* Intervention outcome tracking
* CSV-based student data uploads
* Student Information System (SIS) integrations
* Collaborative intervention workflows
* Classroom activity recommendations

---

## 🏆 Built For

Hugging Face Build Small Hackathon

Homeroom Copilot is designed to help educators spend less time identifying problems and more time helping students succeed.
