# Bug Report: Literal `#` Character in Visible Page Text

**Test:** `test_no_special_chars_in_page_text`
**Page:** [Form Fields](https://practice-automation.com/form-fields/)
**File:** `tests/test_form_fields.py`

---

## Summary

The visible text on the page contains a raw `#` character (the radio button label `#FFC0CB`). Raw `#` or `&` characters in visible text suggest HTML entity encoding issues — these characters should be represented as `&#35;` or `&#35;` in source and rendered correctly, or the label should be descriptive text (e.g., "Pink") rather than a hex colour code.

## Steps to Reproduce

1. Open https://practice-automation.com/form-fields/
2. Look at the radio button group labelled "What is your favorite color?"
3. Observe the last radio button label

**Actual result:** The last radio option is labelled `#FFC0CB`.

**Expected result:** The label should either be a human-readable colour name (e.g., "Pink") or, if a hex code must be shown, it should be encoded as `&#35;FFC0CB` in the HTML source rather than a literal `#`.

## Root Cause Analysis

The radio button is declared in the HTML as:

```html
<input type="radio" id="color5" name="fav_color" value="#FFC0CB" />
<label for="color5">#FFC0CB</label>
```

The label text content `#FFC0CB` contains a literal `#` character. While `#` is technically valid in HTML text nodes, it can cause issues:

1. In URL fragments (`#fragment`) if the text were ever copied into a link
2. In markdown rendering (headings)
3. In CSS `id` selectors or colour values if the label text is used programmatically
4. It visually looks like a rendering glitch to automation testers scanning for `&` / `&#` patterns
5. It breaks the convention of all other colour labels which are plain colour names (Red, Blue, Yellow, Green)

## Suggested Fix

Replace the label text and input `value` with a human-readable colour name:

```html
<input type="radio" id="color5" name="fav_color" value="Pink" />
<label for="color5">Pink</label>
```

If the hex value must be preserved for backend processing, keep it in the `value` attribute but use a friendly label:

```html
<input type="radio" id="color5" name="fav_color" value="#FFC0CB" />
<label for="color5">Pink (#FFC0CB)</label>
```

## Severity

Low — Cosmetic / convention issue. The `#` character is valid HTML and does not cause rendering problems in modern browsers. However, it produces a false positive in automated scans that check for improperly escaped HTML entities, and it is inconsistent with the naming pattern of the other radio options.
