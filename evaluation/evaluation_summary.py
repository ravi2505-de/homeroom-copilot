"""Summarize Homeroom Copilot evaluation scores.

Inputs:
- human_evaluation_template.csv with completed score columns.
- GPT judge JSON files placed in this directory or in gpt_evaluations/.

Output:
- evaluation_summary.csv
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean


EVALUATION_DIR = Path(__file__).resolve().parent
HUMAN_EVALUATION_PATH = EVALUATION_DIR / "human_evaluation_template.csv"
OUTPUT_PATH = EVALUATION_DIR / "evaluation_summary.csv"

METRICS = [
    "relevance",
    "correctness",
    "root_cause_alignment",
    "evidence_alignment",
    "actionability",
    "clarity",
    "overall_quality",
]


def _parse_score(value: str | int | float | None) -> float | None:
    """Parse one score value, returning None for blanks or invalid values."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    try:
        score = float(text)
    except ValueError:
        return None

    if 1 <= score <= 5:
        return score
    return None


def load_human_scores() -> dict[str, list[float]]:
    """Load completed human evaluation scores from CSV."""
    scores = {metric: [] for metric in METRICS}
    if not HUMAN_EVALUATION_PATH.exists():
        return scores

    with HUMAN_EVALUATION_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            for metric in METRICS:
                score = _parse_score(row.get(metric))
                if score is not None:
                    scores[metric].append(score)
    return scores


def gpt_json_paths() -> list[Path]:
    """Return likely GPT judge JSON files."""
    paths = list(EVALUATION_DIR.glob("*.json"))
    nested_dir = EVALUATION_DIR / "gpt_evaluations"
    if nested_dir.exists():
        paths.extend(nested_dir.glob("*.json"))

    return [
        path
        for path in paths
        if path.name != "evaluation_dataset.json"
    ]


def load_gpt_scores() -> dict[str, list[float]]:
    """Load GPT judge scores from JSON files."""
    scores = {metric: [] for metric in METRICS}
    for path in gpt_json_paths():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        for metric in METRICS:
            score = _parse_score(data.get(metric))
            if score is not None:
                scores[metric].append(score)
    return scores


def average(values: list[float]) -> float | None:
    """Return a rounded average or None when there are no scores."""
    if not values:
        return None
    return round(mean(values), 3)


def write_summary() -> None:
    """Write evaluation_summary.csv."""
    human_scores = load_human_scores()
    gpt_scores = load_gpt_scores()

    rows = []
    for metric in METRICS:
        combined_scores = human_scores[metric] + gpt_scores[metric]
        rows.append(
            {
                "metric": metric,
                "human_average": average(human_scores[metric]),
                "gpt_average": average(gpt_scores[metric]),
                "combined_average": average(combined_scores),
                "human_count": len(human_scores[metric]),
                "gpt_count": len(gpt_scores[metric]),
            }
        )

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "metric",
                "human_average",
                "gpt_average",
                "combined_average",
                "human_count",
                "gpt_count",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    write_summary()
    print(f"Wrote {OUTPUT_PATH}")
