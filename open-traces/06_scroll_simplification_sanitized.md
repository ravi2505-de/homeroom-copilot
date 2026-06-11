# Scroll Simplification

## Trace Metadata

- Source session: `rollout-2026-06-07T14-26-07-019ea38c-b315-7f40-a7f5-a53e2e9d91c8.jsonl`
- Source line range: `4795-4849`
- Status: sanitized excerpt for human review
- Upload status: not uploaded, not published

## Summary

Scroll audit and CSS cleanup to reduce nested scroll regions, improve scrollbar usability, and keep Root Causes / AI Action Plan content readable.

## Redaction Actions Applied

- Local user paths replaced

## Curated Conversation Excerpt

### User (source line 4795)

We have one final UI issue before freezing the application.



Problem:



Scrolling feels congested and inconsistent.



Observed behavior:



* Some sections have tiny scrollbars.

* Some content areas stop scrolling before all content is visible.

* Some panels appear clipped.

* Multiple nested scroll regions exist.

* Mouse wheel scrolling sometimes affects the wrong container.

* Root Causes and AI Action Plan are the most noticeable areas.



Goal:



Simplify scrolling behavior.



Requirements:



1. Audit all containers using:



   * overflow

   * overflow-y

   * fixed heights

   * max-height



2. Identify nested scroll containers.



3. Reduce scroll nesting wherever possible.



Preferred behavior:



Desktop:



* Student Analysis should have one primary scrollbar.



* Trend Analysis, Root Causes, and Risk Profile should scroll together.



* Root Causes should not have its own scrollbar unless absolutely necessary.



* AI Action Plan should have one primary scrollbar.



Mobile:



* Preserve current mobile layout.

* Preserve mobile responsiveness fixes.



4. Improve scrollbar usability:



   * Slightly wider scrollbar.

   * Better visibility in dark mode.

   * Better contrast.



5. Remove clipping issues.



6. Do not redesign layout.



7. Do not modify functionality.



8. Do not change risk analysis, retrieval, action plans, or business logic.



Deliverable:



* Explain which containers were causing nested-scroll problems.

* Implement the smallest possible CSS/layout changes to achieve clean scrolling.

* Verify that every section can be fully read without fighting multiple scrollbars.

### Assistant (source line 4799)

I’ll audit the scroll-related CSS first, then I’ll make the smallest layout/CSS change: one scroll container for Student Analysis, one for AI Action Plan, and better scrollbar styling. No logic changes.

### Assistant (source line 4809)

The nested-scroll culprits are clear: `.root-cause-scroll` creates a second scrollbar inside Student Analysis, while `.analysis-main-scroll` is hidden instead of scrollable. The AI panel has a better single-scroll setup, but the scrollbar styling is too subtle. I’ll make Student Analysis scroll as one unit on desktop and keep mobile’s full-page flow intact.

### Assistant (source line 4815)

I’m going to move the desktop scrollbar from the Root Causes box up to the full Student Analysis content area. That lets Risk Profile, Trend Analysis, and Root Causes scroll together, while the AI plan keeps its single scrollbar.

### Assistant (source line 4821)

The nested Root Causes scrollbar is gone on desktop now. I’m updating the mobile override so it doesn’t reintroduce a second root-cause scrollbar there.

### Assistant (source line 4827)

Now I’m adding matching dark-mode scrollbar colors so the scrollbars are visible but not visually loud. This is purely CSS polish.

### Assistant (source line 4834)

The scroll behavior is now simplified in CSS: Student Analysis gets one internal scroll area on desktop, Root Causes no longer owns one, and AI Action Plan keeps one readable scroll area. I’m running a syntax check and reviewing the scroll-related diff.

### Assistant (source line 4844)

Implemented the scroll simplification in [app.py]([LOCAL_USER_HOME]/Desktop/homeroom-copilot/app.py).

What was causing the nested-scroll problem:
- `.root-cause-scroll` had its own fixed `height: 180px` and `overflow-y: auto`, creating a tiny scrollbar inside Student Analysis.
- `.analysis-main-scroll` had `overflow: hidden`, so content could feel clipped instead of scrollable.
- `.balanced-panel .section-card` also uses `overflow: hidden`, so the intended scroll area needed to be the direct inner content region.
- `.action-plan-output` was already the main AI Action Plan scroll container, but its scrollbar was subtle.

What changed:
- Removed the independent Root Causes scrollbar.
- Made `.analysis-main-scroll` the single primary Student Analysis scrollbar.
- Risk Profile, Trend Analysis, and Root Causes now scroll together.
- Kept AI Action Plan as one primary scrollbar.
- Added slightly wider, higher-contrast scrollbar styling.
- Added dark-mode scrollbar contrast.
- Preserved mobile behavior by keeping root causes visible in normal page flow on mobile.

No functionality, layout structure, risk logic, retrieval, or action-plan logic changed.

Verification:
- `app.py` syntax check passed.
- Static CSS audit now shows Root Causes no longer owns a vertical scrollbar, while Student Analysis and AI Action Plan each have one clear scroll region.
