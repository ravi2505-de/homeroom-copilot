# Homeroom Copilot JSONL Open Trace Excerpts

This folder contains sanitized JSONL excerpts from the original Codex session used to build Homeroom Copilot. Nothing in this folder has been uploaded or published by this preparation step.

## Source Trace

- Original source: `rollout-2026-06-07T14-26-07-019ea38c-b315-7f40-a7f5-a53e2e9d91c8.jsonl`
- Original format: JSONL, one JSON event object per line
- Original source file was not modified
- Each sanitized excerpt includes one redacted `session_meta` event followed by the selected source events for that topic

## Redactions Performed

- Local user paths replaced with `[LOCAL_USER_HOME]`
- Local app URLs replaced with `[LOCAL_APP_URL]`
- Codex attachment paths replaced with `[CODEX_ATTACHMENT]`
- Demo student/school names replaced with generic labels where present
- Credential-like strings and private contact details are pattern-redacted if present
- Base/developer instructions inside `session_meta` are omitted from public excerpts
- Encrypted reasoning payloads are replaced with `[REDACTED: encrypted reasoning payload omitted from public trace excerpt]`
- Compacted-history events are removed because they can contain unrelated whole-session history
- Oversized internal tool documentation is replaced with a redaction marker

## Trace Topics

### `01_mobile_responsiveness_fix_sanitized.jsonl`
- Topic: Mobile Responsiveness Fix
- Source lines: 3768-3967
- Events: 201
- Summary: Mobile-only layout fixes that preserved the desktop dashboard while making Student Analysis and AI Action Plan readable on iPhone-sized screens.
- Automated scan status: no credential, message address, local path, local host, or Codex attachment patterns detected

### `02_evaluation_framework_creation_sanitized.jsonl`
- Topic: Evaluation Framework Creation
- Source lines: 3968-4398
- Events: 431
- Summary: Evaluation workflow simplification into developer-only case export artifacts, with no user-facing export controls.
- Automated scan status: no credential, message address, local path, local host, or Codex attachment patterns detected

### `03_evaluation_analysis_sanitized.jsonl`
- Topic: Evaluation Analysis
- Source lines: 4399-4721
- Events: 324
- Summary: Evaluation case preparation, GPT-style judging, type-wise scoring, and analysis showing low/moderate risk over-intervention.
- Automated scan status: no credential, message address, local path, local host, or Codex attachment patterns detected

### `04_risk_aware_prompt_refinement_sanitized.jsonl`
- Topic: Risk-Aware Prompt Refinement
- Source lines: 4562-4729
- Events: 169
- Summary: Prompt diagnosis and revision so low-risk students receive monitoring, moderate-risk students receive targeted support, and high/critical students keep structured plans.
- Automated scan status: no credential, message address, local path, local host, or Codex attachment patterns detected

### `05_dark_mode_polish_sanitized.jsonl`
- Topic: Dark Mode Polish
- Source lines: 4730-4794
- Events: 66
- Summary: Dark-mode readability and contrast pass that preserved layout and day-mode styling while improving card, input, badge, and teacher profile contrast.
- Automated scan status: no credential, message address, local path, local host, or Codex attachment patterns detected

### `06_scroll_simplification_sanitized.jsonl`
- Topic: Scroll Simplification
- Source lines: 4795-4849
- Events: 56
- Summary: Scroll audit and CSS cleanup to reduce nested scroll regions, improve scrollbar usability, and keep Root Causes / AI Action Plan content readable.
- Automated scan status: no credential, message address, local path, local host, or Codex attachment patterns detected

## Trace Viewer Compatibility

These files preserve the Codex JSONL event-object structure and are valid JSONL. They are expected to be closer to Hugging Face trace-viewer-compatible input than Markdown summaries, but final compatibility depends on the exact Open Trace viewer schema accepted by Hugging Face. Validate in the viewer before publishing.

## Human Review Required

A human reviewer should inspect every JSONL excerpt before upload. Do not publish until the final reviewer confirms that the traces contain only project-related content and no sensitive information.
