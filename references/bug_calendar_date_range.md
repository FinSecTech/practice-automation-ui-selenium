# Bug Report: Date Input Accepts Values Outside 1926–2126 Range

**Reported:** 2026-07-01  
**Tested on:** https://practice-automation.com/calendars/  
**Browser:** Firefox

---

## Summary

The interactive date picker correctly restricts year selection to the range **1926–2126** (inclusive), but the **direct text input** field (`<input class="date jp-contact-form-date grunion-field">`) accepts **any** date string in `YYYY-MM-DD` format without enforcing this range. This allows users to submit dates outside the intended boundary, which is inconsistent with the picker's behaviour and almost certainly unintended.

---

## Steps to Reproduce

1. Open https://practice-automation.com/calendars/
2. Locate the date input field (placeholder: "Select or enter a date (YYYY-MM-DD)")
3. Enter any of the following out-of-range dates:
   - `1925-12-31`
   - `1925-01-01`
   - `1800-06-15`
   - `2127-01-01`
   - `2127-12-31`
   - `3000-01-01`
4. Click the **Submit** button
5. Observe the success message "Thank you for your response." and the submitted value

## Expected Behaviour

Submitting a date outside the **1926–2126** range should either:

- Reject the input with a validation error message, or
- Prevent form submission, or
- Automatically clamp the value to the nearest boundary (1926 or 2126)

## Actual Behaviour

The form accepts all out-of-range dates and displays them in the success response without any validation error. For example:

- Input: `1925-12-31` → Success: "Select or enter a date: 1925-12-31"
- Input: `3000-01-01` → Success: "Select or enter a date: 3000-01-01"

## Contrast with Interactive Date Picker

When using the interactive date picker (click the input field → click the year selector button), only years **1926 through 2126** (inclusive) are displayed as selectable buttons. Years outside this range, including 1925 and 2127, are absent from the picker.

This inconsistency means:

- **The interactive picker correctly enforces the range** — a user cannot accidentally (or intentionally) select 1800 or 3000 via the calendar UI.
- **The direct text input bypasses the range** — a user can type any year and submit the form.

## Impact

| Severity | Likelihood | Notes                                                                       |
| -------- | ---------- | --------------------------------------------------------------------------- |
| Medium   | Low        | Requires manual typing of an out-of-range value; picker users are protected |

The bug permits invalid historical or far-future dates to be stored/submitted, which could cause downstream data-processing errors or violate business rules that assume dates are within the 1926–2126 window.

## Suggested Fix

Add server-side and/or client-side validation on the text input to reject dates outside the 1926–2126 range. Options include:

1. **HTML5 `min` / `max` attributes** on the `<input>` element (e.g., `min="1926-01-01"`, `max="2126-12-31"`) so that the browser natively validates the range before submission.
2. **Custom JavaScript validation** that checks the entered date against the allowed range on form submit.
3. **Server-side validation** in the Jetpack contact-form endpoint to return an error for out-of-range dates.

The simplest and most consistent fix would be option 1 (HTML5 `min`/`max`), which aligns the text input with the interactive picker's behaviour at zero implementation complexity.

---

## Test Cases That Demonstrate the Bug

All six parametrised cases in `test_out_of_range_dates.py::test_direct_input_accepts_out_of_range` pass, confirming the bug:

| Input        | Expected (correct behaviour) | Actual (bug) |
| ------------ | ---------------------------- | ------------ |
| `1925-12-31` | Should be rejected           | Accepted ✅  |
| `1925-01-01` | Should be rejected           | Accepted ✅  |
| `1800-06-15` | Should be rejected           | Accepted ✅  |
| `2127-01-01` | Should be rejected           | Accepted ✅  |
| `2127-12-31` | Should be rejected           | Accepted ✅  |
| `3000-01-01` | Should be rejected           | Accepted ✅  |
