# Bug Report: Required Indicator Does Not Disappear After Typing

**Test:** `test_required_indicator_disappears_after_typing`
**Page:** [Form Fields](https://practice-automation.com/form-fields/)
**File:** `tests/test_form_fields.py`

---

## Summary

The red " \* Required" text next to the Name field remains visible even after the user begins typing. Expected behaviour is that the indicator should hide as soon as the field receives input.

## Steps to Reproduce

1. Open https://practice-automation.com/form-fields/
2. Observe the `* Required` text displayed in red below the Name label
3. Click into the Name input field
4. Type a single character

**Actual result:** The `* Required` text remains visible.

**Expected result:** The `* Required` text should disappear the moment the user starts entering text, indicating the validation requirement has been acknowledged.

## Root Cause Analysis

The "Required" indicator is implemented as a static `<p>` element in the HTML:

```html
<label for="name-input"
  >Name
  <input type="text" id="name-input" name="name-input" required="" />
</label>
<p class="red_txt">* Required</p>
```

The `<p class="red_txt">` element has no JavaScript-based show/hide logic attached to the `input` event. It is permanently displayed regardless of the field's state. The `required` attribute on the `<input>` element does provide native HTML5 validation on submit, but there is no client-side script to toggle the visibility of the adjacent `<p>` element.

## Suggested Fix

Add an event listener on the Name input that hides the `.red_txt` element when the input receives any text:

```javascript
const nameInput = document.getElementById("name-input");
const requiredIndicator = document.querySelector(".red_txt");

nameInput.addEventListener("input", function () {
  if (this.value.length > 0) {
    requiredIndicator.style.display = "none";
  } else {
    requiredIndicator.style.display = "block";
  }
});
```

Alternatively, hide the `required` attribute's default tooltip and handle validation programmatically within the `submitForm()` function.

## Severity

Low — Visual polish issue. The form still correctly enforces the required field via HTML5 validation on submit (the browser focuses the empty field and shows its own tooltip). The static indicator is simply misleading cosmetically.
