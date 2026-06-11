# Evaluation Framework Creation

## Trace Metadata

- Source session: `rollout-2026-06-07T14-26-07-019ea38c-b315-7f40-a7f5-a53e2e9d91c8.jsonl`
- Source line range: `3968-4398`
- Status: sanitized excerpt for human review
- Upload status: not uploaded, not published

## Summary

Evaluation workflow simplification into developer-only case export artifacts, with no user-facing export controls.

## Redaction Actions Applied

- Local user paths replaced

## Curated Conversation Excerpt

### User (source line 3968)

We need to simplify the evaluation implementation.



The current export framework is over-engineered for our actual needs.



GOAL



We only need a fixed evaluation dataset consisting of 8 student cases:



* 2 Low Risk

* 2 Moderate Risk

* 2 High Risk

* 2 Critical Risk



These cases will be generated once, manually reviewed, and then stored permanently for evaluation.



We do NOT need dynamic export functionality exposed in the UI.



---



## REMOVE



Remove:



* Export Evaluation Dataset button

* Export Evaluation Dataset workflow

* Automatic generation/export UI controls

* Any UI elements related to evaluation export



The end-user should not see evaluation tooling.



---



## KEEP



Keep the evaluation directory structure.



Keep:



evaluation/

case_001.md

...

case_008.md



Keep:



evaluation/HUMAN_EVALUATION_GUIDE.md



evaluation/GPT4_JUDGE_PROMPT.md



evaluation/evaluation_summary.py



evaluation/human_scores.csv



evaluation/gpt_scores.json



evaluation/evaluation_results.csv



These files are for project evaluation and documentation purposes.



---



## IMPLEMENT NEW WORKFLOW



Create a developer-only utility script.



Suggested location:



scripts/generate_evaluation_cases.py



This script should:



1. Select:



   * 2 Low Risk students

   * 2 Moderate Risk students

   * 2 High Risk students

   * 2 Critical Risk students



2. Generate:



   * Student Profile

   * Risk Assessment

   * Root Cause Analysis

   * Retrieved Interventions

   * AI Action Plan



3. Save outputs into:



evaluation/case_001.md

...

evaluation/case_008.md



4. Generate:



evaluation/evaluation_dataset.json



This script is intended to be run manually one time.



---



## IMPORTANT



Do NOT change:



* Risk scoring logic

* Root cause analysis logic

* Intervention retrieval logic

* Prompt generation logic

* Action plan generation logic



Only change how evaluation cases are created and stored.



---



## SUCCESS CRITERIA



After implementation:



* No evaluation export button exists in the UI.

* Evaluation artifacts remain in the repository.

* A developer can run:



python scripts/generate_evaluation_cases.py



to regenerate the evaluation dataset if needed.



* The application remains unchanged for normal users.

* Existing functionality continues to work exactly as before.

### Assistant (source line 3972)

I’ll strip evaluation export out of the app entirely and move the generation path into a developer-only script. I’ll also check what evaluation artifacts already exist so I don’t accidentally remove useful project docs.

### Assistant (source line 3985)

I’ll remove the UI export path from `app.py`, then move case generation into `scripts/generate_evaluation_cases.py`. I’ll also align the evaluation support files to the simpler names you specified: `human_scores.csv`, `gpt_scores.json`, and `evaluation_results.csv`.

### Assistant (source line 3991)

Now I’m deleting the evaluation helper/export functions from `app.py` so no user-facing export workflow remains.

### Assistant (source line 3997)

Now I’m removing the actual Advanced Options button/status and callback wiring, leaving the app UI clean for end users.

### Assistant (source line 4004)

The app export path is gone. I’ll add the developer utility script under `scripts/` and update the summary utility to use the simplified filenames.

### Assistant (source line 4009)

I’ll replace the summary utility’s filenames to match the new permanent evaluation artifacts: `human_scores.csv`, `gpt_scores.json`, and `evaluation_results.csv`.

### Assistant (source line 4016)

Now I’m adding the manual developer script. It regenerates only the case markdown files and JSON dataset; it does not expose anything in the app.

### Assistant (source line 4023)

I’ll add the permanent evaluation documentation and blank score/result files now. These are not connected to the UI.

### Assistant (source line 4033)

Next I’m adding the blank human/GPT score files and the results CSV header.

### Assistant (source line 4048)

The files are in place. I’m running syntax checks and verifying the app no longer contains any evaluation export UI wiring.

### Assistant (source line 4060)

Simplified the evaluation implementation.

Modified files:
- [app.py]([LOCAL_USER_HOME]\Desktop\homeroom-copilot\app.py)
- [evaluation/evaluation_summary.py]([LOCAL_USER_HOME]\Desktop\homeroom-copilot\evaluation\evaluation_summary.py)

Added files:
- [scripts/generate_evaluation_cases.py]([LOCAL_USER_HOME]\Desktop\homeroom-copilot\scripts\generate_evaluation_cases.py)
- [evaluation/HUMAN_EVALUATION_GUIDE.md]([LOCAL_USER_HOME]\Desktop\homeroom-copilot\evaluation\HUMAN_EVALUATION_GUIDE.md)
- [evaluation/GPT4_JUDGE_PROMPT.md]([LOCAL_USER_HOME]\Desktop\homeroom-copilot\evaluation\GPT4_JUDGE_PROMPT.md)
- [evaluation/human_scores.csv]([LOCAL_USER_HOME]\Desktop\homeroom-copilot\evaluation\human_scores.csv)
- [evaluation/gpt_scores.json]([LOCAL_USER_HOME]\Desktop\homeroom-copilot\evaluation\gpt_scores.json)
- [evaluation/evaluation_results.csv]([LOCAL_USER_HOME]\Desktop\homeroom-copilot\evaluation\evaluation_results.csv)

What changed:
- Removed the `Export Evaluation Dataset` button from the UI.
- Removed all evaluation export UI wiring from `app.py`.
- Removed the dynamic evaluation export workflow from the user-facing app.
- Added developer-only script:

```bash
python scripts/generate_evaluation_cases.py
```

That script selects:
- 2 Low Risk students
- 2 Moderate Risk students
- 2 High Risk students
- 2 Critical Risk students

And generates:
- `evaluation/case_001.md` through `evaluation/case_008.md`
- `evaluation/evaluation_dataset.json`

Kept evaluation artifacts as repo/documentation files:
- Human evaluation guide
- GPT-4 judge prompt
- Human score CSV
- GPT score JSON
- Results CSV
- Summary script

Verified:
- `app.py` syntax passes.
- `scripts/generate_evaluation_cases.py` syntax passes.
- `evaluation/evaluation_summary.py` syntax passes.
- No evaluation export button or callback remains in `app.py`.

I did not run `scripts/generate_evaluation_cases.py` because it would trigger 8 AI action-plan generations.

### User (source line 4066)

We are changing the evaluation workflow again.



Do NOT remove the evaluation documentation files.



We want a one-time evaluation dataset generation process using the deployed HF Space model.



GOAL



After deployment, the application should automatically generate the evaluation dataset ONCE.



The generated files should be saved into:



evaluation/

case_001.md

...

case_008.md



and



evaluation/evaluation_dataset.json



The dataset should contain:



* 2 Low Risk students

* 2 Moderate Risk students

* 2 High Risk students

* 2 Critical Risk students



Each case must include:



* Student Profile

* Risk Assessment

* Root Cause Analysis

* Retrieved Evidence-Based Interventions

* Evidence Sources

* Generated AI Action Plan



IMPORTANT



This generation should happen automatically.



NO UI BUTTONS.



NO USER CONTROLS.



NO EXPORT BUTTONS.



The application should generate the dataset in the background.



Generation should occur only if:



evaluation/evaluation_dataset.json



does NOT already exist.



Pseudo logic:



if evaluation_dataset.json does not exist:

generate all 8 evaluation cases

save files

else:

do nothing



This prevents regeneration on every restart.



After the evaluation files are generated, the application should continue operating normally.



KEEP:



evaluation/HUMAN_EVALUATION_GUIDE.md



evaluation/GPT4_JUDGE_PROMPT.md



evaluation/evaluation_summary.py



Once the evaluation files are successfully generated and committed to the repository, we will remove the automatic generation code in a later cleanup commit.



For now:



* No buttons

* No user-facing evaluation features

* Automatic one-time generation only

* Normal app functionality must remain unchanged

### Assistant (source line 4070)

I’ll add a non-UI background startup hook that checks for `evaluation/evaluation_dataset.json` and only launches generation if it’s missing. It will reuse the existing app pipeline and leave the user-facing workflow alone.

### Assistant (source line 4082)

The current checkout only has `evaluation/evaluation_summary.py`; the guide/prompt/score files and the script are not present. I’ll add the one-time background generator in `app.py` and restore the evaluation documentation artifacts so the evaluation folder is complete, with no UI controls.

### Assistant (source line 4088)

I’m adding the background generator as small helper functions inside `app.py`, because it needs direct access to existing `STUDENTS`, risk/root-cause/retrieval functions, and `generate_ai_action_plan()`. No buttons or user-facing components will be added.

### Assistant (source line 4094)

Next I’m adding the one-time generation helpers. They will do nothing if `evaluation/evaluation_dataset.json` already exists.

### Assistant (source line 4100)

I’ll start the background job after the students and callback functions are defined, but before/around UI construction, so it runs on startup without adding any controls.

### Assistant (source line 4107)

I’m also restoring the evaluation guide and GPT-4 judge prompt files that are expected to live in `evaluation/`.

### Assistant (source line 4113)

Adding the GPT-4 judge prompt file now.

### Assistant (source line 4120)

I’m checking syntax and confirming there are no evaluation UI controls left in the app.

### Assistant (source line 4135)

Implemented the one-time automatic evaluation dataset generation workflow.

Modified:
- [app.py]([LOCAL_USER_HOME]\Desktop\homeroom-copilot\app.py)

Added/restored:
- [evaluation/HUMAN_EVALUATION_GUIDE.md]([LOCAL_USER_HOME]\Desktop\homeroom-copilot\evaluation\HUMAN_EVALUATION_GUIDE.md)
- [evaluation/GPT4_JUDGE_PROMPT.md]([LOCAL_USER_HOME]\Desktop\homeroom-copilot\evaluation\GPT4_JUDGE_PROMPT.md)

What changed:
- No UI buttons were added.
- No export controls exist in the app.
- On app startup, the app checks:

```python
evaluation/evaluation_dataset.json
```

- If it exists: does nothing.
- If it does not exist: starts a daemon background thread to generate:
  - `evaluation/case_001.md` through `evaluation/case_008.md`
  - `evaluation/evaluation_dataset.json`

Each generated case includes:
- Student Profile
- Risk Assessment
- Root Cause Analysis
- Retrieved Evidence-Based Interventions
- Evidence Sources
- Generated AI Action Plan

Preserved:
- Risk scoring
- Root-cause logic
- Retrieval logic
- Prompt generation
- Action-plan generation
- UI workflow

Verified:
- `app.py` syntax passes.
- No `Export Evaluation Dataset` button or export UI wiring remains.
- Evaluation guide and GPT-4 judge prompt exist.

I did not run the generation locally because it would trigger 8 AI action-plan generations. On deployment, it will run automatically only once if `evaluation/evaluation_dataset.json` is missing.

### User (source line 4141)

Show me exactly how startup generation failure is handled.



Questions:



1. If case_005 generation fails, what happens?



2. Does the app still launch normally?



3. Are partial datasets cleaned up?



4. Does generation retry?



5. Is a completion marker only written after all 8 cases succeed?



Show the exact flow.

### Assistant (source line 4144)

I’ll inspect the current startup generation function and walk through its exact behavior from the code, including the partial-write and retry implications.

### Assistant (source line 4150)

I need the full loop section to answer precisely, especially when files are written relative to case generation.

### Assistant (source line 4155)

Here is the exact current flow.

**Startup Trigger**
At module startup:

```python
initial_choices = student_choices("All")
initial_student = initial_choices[0] if initial_choices else None
start_evaluation_generation_thread()
```

Then:

```python
def start_evaluation_generation_thread() -> None:
    if EVALUATION_DATASET_PATH.exists():
        logger.info("Evaluation dataset already exists; no background job needed.")
        return

    thread = threading.Thread(
        target=generate_evaluation_dataset_once,
        name="evaluation-dataset-generator",
        daemon=True,
    )
    thread.start()
```

So generation runs in a background daemon thread only if:

```python
evaluation/evaluation_dataset.json
```

does not exist.

**1. If `case_005` generation fails, what happens?**

All 8 cases are built inside this list comprehension:

```python
cases = [
    build_evaluation_case(
        case_id=f"case_{index:03d}",
        student=student,
        intervention_library=intervention_library,
    )
    for index, student in enumerate(selected_students, start=1)
]
```

If `case_005` fails inside `build_evaluation_case(...)`, the list comprehension stops immediately and jumps to:

```python
except Exception:
    logger.exception("Evaluation dataset generation failed.")
```

So:
- `case_001` through `case_004` may have been generated in memory.
- No case markdown files are written yet.
- `evaluation_dataset.json` is not written.
- The failure is logged.
- The background thread ends.

**2. Does the app still launch normally?**

Yes.

Because generation runs in a daemon background thread:

```python
thread = threading.Thread(..., daemon=True)
thread.start()
```

And exceptions are caught inside:

```python
except Exception:
    logger.exception("Evaluation dataset generation failed.")
```

So the exception does not crash Gradio startup or the main app.

**3. Are partial datasets cleaned up?**

Current answer: mostly not applicable for case-generation failures, but no explicit cleanup exists.

Important detail:
- Markdown files are written only after all `cases` are successfully built.
- `evaluation_dataset.json` is written only after all Markdown files are written.

So if `case_005` fails during generation, no `case_001.md` to `case_004.md` files are written by this run.

But if failure happens later during file writing, for example while writing `case_006.md`, then already-written files like `case_001.md` through `case_005.md` would remain. There is no cleanup step.

**4. Does generation retry?**

Not during the same app run.

If generation fails, the thread exits. There is no retry loop.

On a future restart:
- If `evaluation/evaluation_dataset.json` still does not exist, generation will be attempted again.
- If `evaluation/evaluation_dataset.json` exists, it will skip.

**5. Is a completion marker only written after all 8 cases succeed?**

Yes, currently `evaluation_dataset.json` acts as the completion marker.

It is written only after:

1. All selected students are found.
2. All 8 cases are generated into memory.
3. All 8 Markdown files are written.

Only then:

```python
EVALUATION_DATASET_PATH.write_text(
    json.dumps(cases, indent=2, ensure_ascii=False),
    encoding="utf-8",
)
```

So for the specific `case_005` failure scenario, the completion marker is not written.

**Exact Failure Flow For `case_005`**

```text
App starts
↓
start_evaluation_generation_thread()
↓
evaluation_dataset.json missing
↓
background daemon thread starts
↓
generate_evaluation_dataset_once()
↓
select 8 students
↓
build case_001 in memory
↓
build case_002 in memory
↓
build case_003 in memory
↓
build case_004 in memory
↓
build case_005 fails
↓
jump to except
↓
log "Evaluation dataset generation failed."
↓
thread exits
↓
no evaluation_dataset.json written
↓
app continues running normally
```

Current weakness: if failure occurs during the file-writing phase, partial `case_*.md` files can remain because there is no cleanup/atomic staging directory.

### User (source line 4161)

We are simplifying the evaluation workflow.



DO NOT generate AI Action Plans.



I will manually generate AI Action Plans in the deployed HF Space.



I only need a utility that extracts existing student information.



GOAL



Given a list of student names, generate evaluation packages containing:



* Student Name

* Student Profile

* Risk Level

* Risk Factors

* Risk Assessment

* Root Cause Analysis

* Retrieved Evidence-Based Interventions

* Evidence Sources



DO NOT generate AI Action Plans.



The AI Action Plans will be collected manually from the HF Space and added later.



IMPLEMENT



Create:



scripts/export_student_evaluation_data.py



Input:



A list of student names.



Example:



students = [

"Student A",

"Student B",

...

]



Output:



evaluation/case_001.md

evaluation/case_002.md

...

evaluation/case_008.md



Each file should contain:



# Student Profile



# Risk Assessment



# Risk Factors



# Root Cause Analysis



# Retrieved Evidence-Based Interventions



# Evidence Sources



# Generated AI Action Plan



Leave the AI Action Plan section empty with a placeholder:



[PASTE GENERATED ACTION PLAN HERE]



IMPORTANT



Do not call Qwen.



Do not call generate_text().



Do not call AI Action Plan generation.



Do not modify:



* Risk scoring logic

* Root cause logic

* Intervention retrieval logic

* Prompt logic



The script should only extract existing information already available in the system.



The goal is to prepare evaluation packages that will later be completed manually using AI Action Plans generated from the HF Space.

### Assistant (source line 4165)

I’ll make this safe by removing the startup auto-generation trigger and adding a standalone extraction script that never imports or calls the LLM path. It will use only the existing risk/root-cause/retrieval modules.

### Assistant (source line 4178)

I’ll make the evaluation path developer-only and keep it away from the UI/LLM path. First I’m checking the current startup evaluation code so I can remove the automatic Qwen call cleanly, then I’ll add the extraction script.

### Assistant (source line 4190)

I found the piece causing the mismatch: `app.py` still has a startup background evaluator, and that path calls `generate_ai_action_plan()`. I’m going to remove that automatic generation path entirely and replace it with a standalone script that only exports existing analysis/evidence with a placeholder.

### Assistant (source line 4200)

The script will avoid importing `app.py` so it doesn’t touch the ZeroGPU/model path at all. That keeps this evaluation extraction safe to run locally and on deployment machines without accidentally loading Qwen.

### Assistant (source line 4224)

I’m cutting only the evaluation/export plumbing from the running app. The normal teacher workflow and the AI action-plan button stay as-is; evaluation generation moves to `scripts/` and never calls `generate_text()`.

### Assistant (source line 4239)

The app no longer has the hidden “generate evaluation data on startup” hook. Now I’m adding the manual export script with its own small formatting helpers so it can produce the evaluation package without importing UI code.

### Assistant (source line 4260)

I checked the demo data just enough to provide a ready-to-run default list: 2 low, 2 moderate, 2 high, and 2 critical students. You can still edit that list or pass names on the command line later.

### Assistant (source line 4267)

The developer utility is in place now. I’m doing a quick syntax and safety pass: confirming `app.py` has no evaluation startup hook left, and confirming the script doesn’t reference the LLM/action-plan generation path.

### Assistant (source line 4277)

The only remaining `generate_ai_action_plan()` references are the normal UI action-plan flow, which we’re preserving. The new script has only the placeholder string and no LLM imports or generation calls.

### Assistant (source line 4307)

Verification is clean: the extraction script imports without model dependencies, and the app has no startup evaluation generation symbols left. I did not run the export script because it writes case files; it’s ready for you to run when you want to generate the package.

### Assistant (source line 4309)

Implemented the simplified evaluation workflow.

Changed:
- [app.py]([LOCAL_USER_HOME]/Desktop/homeroom-copilot/app.py): removed the automatic startup evaluation generation path, so the app will no longer generate evaluation cases or call Qwen in the background.
- [export_student_evaluation_data.py]([LOCAL_USER_HOME]/Desktop/homeroom-copilot/scripts/export_student_evaluation_data.py): added a developer-only utility that exports student evaluation packages without calling Qwen, `generate_text()`, or AI action-plan generation.

The script outputs:
- `evaluation/case_001.md` through `case_008.md`
- `evaluation/evaluation_dataset.json`
- Each case includes the required placeholder:
  `[PASTE GENERATED ACTION PLAN HERE]`

Run it with:

```bash
python scripts/export_student_evaluation_data.py
```

It currently includes a default 8-student list with 2 Low, 2 Moderate, 2 High, and 2 Critical risk students. You can edit `STUDENT_NAMES` in the script or pass names as command-line arguments. Syntax checks passed.

### User (source line 4315)

There is a UI bug in the Root Cause Analysis panel.



Issue:



The Root Cause Analysis content does not scroll correctly when the content exceeds the visible panel height.



Expected behavior:



* Root Cause Analysis should remain inside its card/container.

* Vertical scrolling should work when content is longer than the available height.

* No content should be clipped.

* No horizontal scrolling should appear.

* Mobile and desktop should both work.



Please inspect:



* Root Cause Analysis container CSS

* Overflow settings

* Fixed-height containers

* Parent container flex/grid layouts



Verify:



Desktop:



* Long root-cause analysis can be fully read using scroll.



Mobile:



* Long root-cause analysis can be fully read using scroll.



Do not redesign the UI.

Only fix scrolling behavior.

### Assistant (source line 4319)

I’ll trace the root-cause panel from the rendered HTML class names through the CSS, then make the smallest overflow/flex fix so scrolling belongs to that section instead of getting clipped by a parent.

### Assistant (source line 4328)

The CSS shows the likely culprit: the desktop panel is fixed-height with parent `overflow: hidden`, while root causes has a fixed height but not enough flex/min-height protection around it. I’m tightening just that section so the root-cause box gets its own scroll area and text wrapping, without changing the layout.

### Assistant (source line 4334)

I’m going to add a specific root-cause section class in the HTML and make that section a flex child with `min-height: 0`. That small detail matters because scroll containers inside fixed-height flex cards often fail when ancestors don’t allow shrinking.

### Assistant (source line 4340)

Now I’m wiring that class onto only the Root Causes subsection. I’ll also make the mobile rule keep a real fixed-height scroll box instead of `height: auto`, which can be inconsistent inside Gradio’s nested containers.

### Assistant (source line 4351)

The fix is in CSS/HTML only: no scoring, root-cause logic, or layout redesign touched. I’m running a syntax check and checking the final diff so I can make sure this stayed scoped.

### Assistant (source line 4361)

I’ve made the scoped CSS fix. Since your app is already open at `[LOCAL_APP_URL]`, I’ll do a quick browser check on the current page to make sure the root-cause area has a scrollbar and doesn’t create horizontal overflow.

### Assistant (source line 4367)

I’m using the in-app browser to verify this, because the bug is specifically about visible scrolling behavior. I’ll keep it to a quick DOM/viewport check.

### Assistant (source line 4379)

The app server may still be serving the previous CSS until it’s restarted, so I’m checking whether there’s an active local process before deciding if browser verification would reflect the new code or just the old page.

### Assistant (source line 4387)

There doesn’t appear to be a live process on port `7861`, so the current browser tab is stale and won’t verify the updated CSS. I’ll avoid pretending that’s a real check; I’m doing static verification against the CSS and syntax instead.

### Assistant (source line 4393)

Fixed the Root Cause Analysis scrolling in [app.py]([LOCAL_USER_HOME]/Desktop/homeroom-copilot/app.py).

What changed:
- Added a dedicated `.root-cause-section` flex container.
- Made `.analysis-main-scroll` use `flex: 1`, `min-height: 0`, and `overflow: hidden` so the root-cause scroll area is not clipped by the fixed-height parent card.
- Ensured `.root-cause-scroll` uses vertical scrolling, hides horizontal overflow, and wraps long text.
- Updated mobile CSS so Root Causes has a fixed scrollable height instead of relying on inconsistent `height: auto`.

Verified:
- `app.py` syntax passes.
- Static CSS check confirms Root Causes now has its own scroll container on desktop and mobile.

I couldn’t live-verify in the browser because nothing is currently running on `[LOCAL_APP_URL]`; the tab you have open is stale until the app is restarted.
