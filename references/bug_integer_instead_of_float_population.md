# Bug Report: Integer Instead of Float in Population Column

## Summary

In the Sortable Table's **Population (million)** column, several rows display integer values (e.g. `340`) instead of **floating-point values** (e.g. `340.0`). Since the column consistently represents population in millions as floating-point numbers with one decimal place, the integer format is a formatting inconsistency.

---

## Affected Rows

| Row | Country       | Displayed Value | Expected Value |
| --- | ------------- | --------------- | -------------- |
| 1   | India         | `1,429`         | `1429.0`       |
| 2   | China         | `1,426`         | `1426.0`       |
| 3   | United States | `340`           | `340.0`        |
| 8   | Bangladesh    | `173`           | `173.0`        |
| 15  | D.R. Congo    | `102`           | `102.0`        |
| 16  | Vietnam       | `99`            | `99.0`         |
| 18  | Iran          | `84`            | `84.0`         |

**Note:** Rows 1 and 2 also have the **comma-bug** (comma instead of dot). These are flagged here because their value is also missing a decimal point.

---

## Observed Behaviour

The column uses floating-point notation for most rows (e.g. `277.5`, `240.5`, `223.8`, `216.4`, `144.4`, etc.), but 7 rows lack the decimal portion entirely. This is inconsistent formatting within the same column.

---

## Expected Behaviour

Every value in the Population (million) column should be displayed as a floating-point number with a dot and at least one decimal digit:

- `340` → `340.0`
- `173` → `173.0`
- `102` → `102.0`
- `99` → `99.0`
- `84` → `84.0`
- `1,429` → `1429.0`
- `1,426` → `1426.0`

---

## Severity

**Low** — The numerical value is correct (340 million = 340.0 million), so no data corruption occurs. However, the inconsistent formatting within a single column is a presentation bug that reduces the professional appearance of the table.

---

## Root Cause

The logic that formats the population value in millions appears to only add a `.0` suffix when the value has a fractional part. Integer values (e.g. 340 million exactly) are displayed as-is without the decimal suffix. This suggests the formatting code uses something like:

```javascript
value % 1 === 0 ? String(value) : value.toFixed(1);
```

instead of always calling `.toFixed(1)`.

---

## Steps to Reproduce

1. Navigate to https://practice-automation.com/tables/
2. Locate the Sortable Table
3. Examine the "Population (million)" column for rows 1, 2, 3, 8, 15, 16, 18
4. Observe the absence of `.0` (and for rows 1, 2, the comma bug)

---

## Suggested Fix

Apply a consistent formatting function to all values in the column:

```javascript
function formatPopulationMillions(value) {
  return Number(value).toFixed(1); // Always show one decimal place
}
```

This ensures every row displays a consistent floating-point format.

---

## Test Coverage

- `TestIntegerBug::test_integer_not_float_bug` — always fails with the buggy rows listed
- Detected as side-effect in `TestSourceOfTruth::test_compare_column3_population`

---

_Report generated 2026-07-01 during automated testing of https://practice-automation.com/tables/_
