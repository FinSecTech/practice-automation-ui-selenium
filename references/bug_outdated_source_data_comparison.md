# Bug Report: Sortable Table Data Outdated Compared to Source of Truth

## Summary

The Sortable Table on `https://practice-automation.com/tables/` contains **outdated population data** compared to the source of truth at `https://www.worldometers.info/world-population/population-by-country/`. Every one of the 25 displayed rows has population values that do not match the current worldometers data. Additionally, the country ordering by rank is partially incorrect — several countries appear in the wrong rank position.

---

## Affected Tests

| Test                                      | Status |
| ----------------------------------------- | ------ |
| `test_compare_column1_rank`               | PASS   |
| `test_compare_column2_country` (pairwise) | FAIL   |
| `test_compare_column3_population`         | FAIL   |

---

## Observations

### Column 1 (Rank)

All 25 Rank values (1–25) exist in the source-of-truth set. Set membership passes.

**This column appears correct** — the ranks are a static index that doesn't change, so they match.

### Column 2 (Country) — Pairwise Mismatches

The set-membership check passes (every tested country exists in the source set), but the **pairwise comparison** fails for 11 rows. The following rows have swapped positions relative to the source:

| Row | Tested Country | Source Country (should be here) |
| --- | -------------- | ------------------------------- |
| 10  | Mexico         | Ethiopia                        |
| 11  | Ethiopia       | Mexico                          |
| 13  | Philippines    | Egypt                           |
| 14  | Egypt          | Philippines                     |
| 17  | Turkey         | Iran                            |
| 18  | Iran           | Turkey                          |
| 20  | Thailand       | Tanzania                        |
| 21  | United Kingdom | Thailand                        |
| 22  | France         | United Kingdom                  |
| 23  | Italy          | France                          |
| 24  | Tanzania       | South Africa                    |
| 25  | South Africa   | Italy                           |

Some countries differ by only a few rank positions (e.g. Mexico ↔ Ethiopia are off by 1), while others are off by 2–3 positions (e.g. Tanzania, South Africa, Italy). This pattern is consistent with **population changes over time** — some countries grew faster than others, causing their rank to shift.

### Column 3 (Population) — All 25 Rows Fail

Every row's population value differs from the source-of-truth. The test output shows **all 25 rows** failing both set-membership and pairwise checks. Example:

| Row | Country       | Tested Value | Source Value (÷1M) | Source Raw    |
| --- | ------------- | ------------ | ------------------ | ------------- |
| 1   | India         | `1,429`      | 1476.6             | 1,476,625,576 |
| 2   | China         | `1,426`      | 1412.9             | 1,412,914,089 |
| 3   | United States | `340`        | 349.0              | 349,035,494   |
| 4   | Indonesia     | `277.5`      | 287.9              | 287,886,782   |
| 5   | Pakistan      | `240.5`      | 259.3              | 259,299,791   |
| 6   | Nigeria       | `223.8`      | 242.4              | 242,431,832   |
| 7   | Brazil        | `216.4`      | 213.6              | 213,562,666   |
| 8   | Bangladesh    | `173`        | 177.8              | 177,818,044   |
| …   | …             | …            | …                  | …             |

All tested values are **lower** than the source values for rows 1–6 (growing countries), then some rows show the tested value as **higher** (e.g. Brazil 216.4 vs source 213.6 — either the source data is from a later year where Brazil's population declined, or the tested data was from an earlier estimate).

---

## Severity

**High** — The data displayed to users is factually incorrect against the current source of truth. While the table is advertised as a teaching/demo page, users relying on this data for any real-world purpose would receive inaccurate information.

---

## Root Cause

The tested table displays **historical/static population estimates** while the worldometers source shows **live or frequently updated projections**. The discrepancy suggests the tested table data was captured at an earlier point in time and never refreshed.

---

## Steps to Reproduce

1. Navigate to https://practice-automation.com/tables/
2. Open the "Source" link in a new tab to load worldometers
3. Compare population values row-by-row
4. Observe that no population value matches exactly

---

## Suggested Fix

Update the Sortable Table data to match the current worldometers source. This could be done by:

1. **Re-importing** the worldometers dataset into the table
2. **Automating** periodic updates via a scheduled job that pulls fresh data
3. Adding a **"last updated" timestamp** to the table so users know how fresh the data is

---

## Test Coverage

- `TestSourceOfTruth::test_compare_column2_country` — pairwise comparison fails (11 rows)
- `TestSourceOfTruth::test_compare_column3_population` — set membership + pairwise fails (all 25 rows)

---

_Report generated 2026-07-01 during automated testing of https://practice-automation.com/tables/_
