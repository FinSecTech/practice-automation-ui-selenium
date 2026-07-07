# Bug Report: Popup Maker Modals Have No Visible Trigger

**Page**: https://practice-automation.com/popups/  
**Detected**: 2026-06-30  
**Severity**: Medium  
**Status**: Confirmed

---

## Summary

The `/popups/` page defines two Popup Maker (pum) overlay modals — a **Simple Modal** (`pum-1318`) and a **Modal Containing A Form** (`pum-674`) — but neither has a visible trigger element wired up in the page content. Users cannot open either modal through any UI interaction on this page.

Meanwhile, functional equivalents of these two modals **already exist** on the separate page `/modals/`, where they can be opened and interacted with normally.

---

## Affected Elements

| Modal        | ID         | Expected Trigger                                                        | Actual                    |
| ------------ | ---------- | ----------------------------------------------------------------------- | ------------------------- |
| Simple Modal | `pum-1318` | Title: "Simple Modal", Content: "Hi, I'm a simple modal."               | No trigger element exists |
| Form Modal   | `pum-674`  | Title: "Modal Containing A Form", Fields: Name, Email, Message + Submit | No trigger element exists |

---

## Root Cause

Both modals are configured in the Popup Maker plugin data attributes with `"click_open":{"extra_selectors":""}` — meaning no CSS selector or button class was configured to open them. A search of the full page HTML confirms there is **no element** with class `popmake-1318`, `popmake-674`, or any other Popup Maker trigger class in the page content.

---

## How to Reproduce

1. Navigate to https://practice-automation.com/popups/
2. Inspect the page DOM (or search for `pum-1318` / `pum-674`)
3. Observe that the overlay `<div>` elements exist but have `display: none`
4. Attempt to find any button, link, or element that opens them — none exist

The modals can _only_ be opened via the browser console:

- `PUM.open(1318)` — Simple Modal
- `PUM.open(674)` — Form Modal

---

## Automated Tests

Three tests in `tests/test_popups.py` document this issue:

| Test                                     | What It Checks                                | Current Result             |
| ---------------------------------------- | --------------------------------------------- | -------------------------- |
| `test_simple_modal_visible_on_page_load` | Simple Modal overlay `is_displayed()`         | FAIL — overlay is hidden   |
| `test_form_modal_visible_on_page_load`   | Form Modal overlay `is_displayed()`           | FAIL — overlay is hidden   |
| `test_form_modal_fields_interactable`    | Form field inside Form Modal `is_displayed()` | FAIL — field hidden inside |

These tests are **not erroneous** — they are written against one valid fix approach (see **Option A** below) and serve as regression detection should that approach be adopted.

---

## Recommended Fix Approaches

There are two legitimate ways to resolve this issue. Both are valid; the choice depends on the intended architecture of the practice site.

---

### Option A (Adopted by the Automated Tests) — Add Triggers on `/popups/`

Add visible trigger buttons to the `/popups/` page so the two modals sit alongside the existing "Alert Popup", "Confirm Popup", and "Prompt Popup" buttons. This would make the page a single, comprehensive practice destination for **all** popup-type interactions.

**Strengths:**

- Single learning destination: students can practice alerts, confirms, prompts, tooltips, **and** modals without navigating away.
- Consistent UX: every popup type has a visible, labelled trigger on the same page.
- Minimal code change: the overlay markup already exists in the DOM; only trigger buttons need wiring (e.g., `<button class="popmake-1318">Simple Modal</button>`).
- Tests already exist and will pass immediately.

**Weaknesses:**

- The page gets longer — more buttons compete for the student's attention.
- Duplicates functionality that already lives on `/modals/`, creating two paths to the same interaction.

---

### Option B (Site Developers' Likely Intent) — Move Modals to `/modals/` and Clean Up `/popups/` DOM

The modals already have working implementations on the separate page https://practice-automation.com/modals/. Under this approach:

1. **Remove** the orphaned Popup Maker overlay markup (`pum-1318` and `pum-674` `<div>` elements) entirely from the `/popups/` page DOM.
2. Ensure the `/modals/` page covers the functionality fully (it already does).

**Why simply hiding the modals is not enough:**
The current state of `/popups/` does **not** just lack trigger buttons — it still carries full Popup Maker overlay HTML in the DOM, including form fields, close buttons, background overlays, and plugin-generated styles/scripts. Leaving this debris in the DOM causes real problems:

- **Page bloat**: Unnecessary HTML inflates page size and load time, even if the elements are `display: none`. Images, fonts, and other resources referenced inside these hidden overlays may still be requested by the browser.
- **CSS/JS conflicts**: Popup Maker loads its own stylesheets and JavaScript. Orphaned plugin code can interfere with other elements on the page — for example, global click handlers, z-index stacking, or CSS that accidentally targets hidden elements.
- **Misleading test results**: Any automated check for element existence, count, or attribute state on `/popups/` will pick up these ghost elements, leading to false positives or confusing failures (e.g., `find_elements` returning more results than expected).
- **Maintenance debt**: Future developers (or the original author months later) will see markup in the DOM with no visible purpose and waste time figuring out whether it's dead code or should have a trigger.

**Correct action**: Strip the modal markup entirely — remove the `<div id="pum-1318">`, `<div id="pum-674">`, and any Popup Maker initialisation script blocks tied to these popups from the `/popups/` page. The `/modals/` page is the canonical home for these interactions.

---

## Summary of Options

| Criterion                | Option A (Add triggers on `/popups/`) | Option B (Clean DOM, rely on `/modals/`)          |
| ------------------------ | ------------------------------------- | ------------------------------------------------- |
| Fix scope                | Add trigger buttons                   | Strip orphaned markup from `/popups/`             |
| User-facing change       | Two new buttons appear on `/popups/`  | No visible change — modals stay on `/modals/`     |
| Code change              | Minimal (triggers only)               | Moderate (remove markup + scripts)                |
| Tests affected           | Existing tests pass as-is             | Tests must be removed or moved to `/modals/` page |
| Page cohesion            | All popup types in one place          | Each interaction type on its own page             |
| Risk of DOM side effects | None (additive change only)           | Eliminates ghost-element risks                    |
