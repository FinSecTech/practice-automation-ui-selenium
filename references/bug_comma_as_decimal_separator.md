# Bug Report: Comma Used Instead of Dot as Decimal Separator

## Summary

In the Sortable Table's **Population (million)** column, the values for rows 1 and 2 use a **comma** as the decimal/thousands separator instead of a **dot**. Since the column represents population values in millions as floating-point numbers, the expected format uses a dot (e.g. `1429.0`), but these rows display a comma (e.g. `1,429`).

---

## Affected Rows

| Row | Country | Displayed Value | Expected Value |
| --- | ------- | --------------- | -------------- |
| 1   | India   | `1,429`         | `1429.0`       |
| 2   | China   | `1,426`         | `1426.0`       |

---

## Observed Behaviour

- Row 1 (India): `1,429` — the comma is used in place of the decimal point.
- Row 2 (China): `1,426` — the comma is used in place of the decimal point.

All other rows use a dot as decimal separator (e.g. `277.5`, `240.5`, `223.8`).

---

## Expected Behaviour

The values should be formatted as floating-point numbers with a dot as the decimal separator:

- Row 1 (India): `1429.0`
- Row 2 (China): `1426.0`

---

## Severity

**Medium** — The data is numerically correct (1429 million ≠ 1.429 million), but the presentation is misleading. A user reading `1,429` may interpret it as "one point four two nine million" instead of "one thousand four hundred twenty-nine million." The comma here appears to serve as a thousands separator for the integer part, but in a millions-as-float column, the dot is the standard separator and the comma creates ambiguity.

---

## Root Cause

Likely a locale/formatting mismatch in the data pipeline that generates the table. The comma behaviour is inconsistent with the rest of the column, suggesting a template or export configuration that applies thousands-separator formatting to these specific rows instead of the floating-point format.

---

## Steps to Reproduce

1. Navigate to https://practice-automation.com/tables/
2. Locate the Sortable Table
3. Examine row 1 (India) and row 2 (China) in the "Population (million)" column
4. Observe the comma where a dot is expected

---

## Suggested Fix

Ensure the column formatting applies a consistent floating-point representation. If the source value is `1429000000` (raw integer from worldometers), dividing by 1 million gives `1429.0`, which should be displayed as `"1429.0"` — not `"1,429"`.

---

## Test Coverage

- `TestCommaBug::test_comma_as_decimal_separator_bug` — always fails with the buggy rows listed
- Detected as side-effect in `TestSourceOfTruth::test_compare_column3_population` (population comparison)

---

_Report generated 2026-07-01 during automated testing of https://practice-automation.com/tables/_
