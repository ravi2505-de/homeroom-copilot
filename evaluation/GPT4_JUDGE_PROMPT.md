# GPT-4 Judge Prompt

You are evaluating one Homeroom Copilot action-plan case.

Evaluate the provided:

- Student Profile
- Risk Assessment
- Root Cause Analysis
- Retrieved Interventions
- Evidence Sources
- Generated Action Plan

Use exactly these seven metrics:

1. relevance
2. correctness
3. root_cause_alignment
4. evidence_alignment
5. actionability
6. clarity
7. overall_quality

Scoring scale:

1 = Poor
2 = Limited
3 = Moderate
4 = Good
5 = Excellent

Return JSON output only. Do not include Markdown. Do not include commentary outside JSON.

Expected format:

```json
{
  "case_id": "case_001",
  "relevance": 5,
  "correctness": 4,
  "root_cause_alignment": 5,
  "evidence_alignment": 4,
  "actionability": 5,
  "clarity": 5,
  "overall_quality": 5,
  "summary": "Brief explanation of the judgment."
}
```
