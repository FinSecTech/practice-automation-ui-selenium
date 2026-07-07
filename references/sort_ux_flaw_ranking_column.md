# DataTables 2.x — Sorting UX Flaw Report: Rank Column

## Summary

The **Sortable Table** on `https://practice-automation.com/tables/` uses **DataTables 2.x** for client-side sorting. The **Rank** column exhibits a **3-state sort cycle** that violates user expectations: clicking an already-sorted column header should toggle to the opposite direction, but here it re-applies the _same_ direction on the first click.

---

## Observed Behaviour

| Click #     | Sort Direction    | Visible Data Change | Sort Arrow         |
| ----------- | ----------------- | ------------------- | ------------------ |
| 0 (initial) | Ascending (1→25)  | —                   | Hidden / default   |
| 1           | Ascending (1→25)  | ❌ No change        | Shows ascending ▲  |
| 2           | Descending (25→1) | ✅ Reversed         | Shows descending ▼ |
| 3           | Ascending (1→25)  | ✅ Reversed back    | Shows ascending ▲  |
| 4           | Descending (25→1) | ✅ Reversed         | Shows descending ▼ |
| …           | cycles 2–3–2–3…   |                     |                    |

The 3-state cycle is **`asc → asc → desc → asc → desc → …`**.  
The expected 2-state cycle is **`asc → desc → asc → desc → …`**.

---

## Affected Columns

| Column               | Default Sorted? | 1st Click Behaviour             | UX Flaw? |
| -------------------- | --------------- | ------------------------------- | -------- |
| Rank                 | ✅ Yes (asc)    | Re-applies asc (no data change) | ✅ Yes   |
| Country              | ❌ No           | Ascending (data changes)        | ❌ No    |
| Population (million) | ❌ No           | Ascending (data changes)        | ❌ No    |

Only **Rank** (the initially-sorted column) is affected. Country and Population work as expected because they start in a "no sort" state.

---

## Root Cause

DataTables 2.x defaults to a **3-state sort cycle** per column:

```
unsorted → ascending → descending → unsorted → …
```

For a column that starts **already sorted ascending** (like Rank), the state machine begins at state 1 (`ascending`), so the first click transitions to state 2 (`ascending` again → no visible change). The second click reaches state 3 (`descending`). The third click goes back to `unsorted` (which defaults back to ascending → 1→25).

In DataTables initialisation options, this is controlled by the [`orderSequence`](https://datatables.net/reference/option/columns.orderSequence) option, which defaults to `['asc', 'desc']` but when the column is initialised with a sort direction already applied, it behaves as a 3-state cycle internally.

---

## Why This Is a UX/UI Flaw

1. **Fitts's Law violation**: The user performs an action (click) and receives zero feedback in the data — the only change is a small arrow icon. The data table does not visibly respond to the interaction, making the user think the click "did nothing".

2. **Inconsistency with other columns**: Country and Population toggle immediately on first click. Rank requires two clicks for the same result. This inconsistency erodes the predictability of the interface.

3. **Cognitive overhead**: Users must learn that Rank behaves differently from other columns. Good UI should be self-evident; requiring memorisation of column-specific behaviour is a failure.

4. **Accessibility concern**: Users relying on screen readers or keyboard navigation may not perceive the arrow-icon-only change, further reducing discoverability of the sort toggle.

---

## Suggested Fix

### Option A: 2-state cycle for Rank (Recommended)

Configure DataTables with a **2-state sort cycle** for the Rank column using `orderSequence`:

```javascript
$("#tablepress-1").DataTable({
  columns: [
    { orderSequence: ["asc", "desc"] }, // Rank — 2-state
    null, // Country — default
    null, // Population — default
  ],
  // other options...
});
```

With this, the cycle becomes: **`asc → desc → asc → desc → …`**, matching user expectations. The first click on Rank would toggle directly to descending (25→1).

### Option B: Remove initial sort indicator

Initialise the table with **no default sort order** on any column, then let the first click on any column establish the sort:

```javascript
$("#tablepress-1").DataTable({
  ordering: true,
  order: [], // No initial sort
});
```

This makes all columns behave identically from the start, but changes the default view (rows would appear in their original DOM order, not rank order).

### Option C: Visual cue for "already sorted"

If the 3-state cycle must be preserved, make it **visible** that the first click actually did something. For example, a brief flash animation on the column, a tooltip "Already sorted ascending — click again to reverse", or a non-zero-duration transition on the data rows.

---

## Test Adaptation (Already Applied)

The test `test_sort_by_rank` in `TestSorting` was adapted to accommodate this behaviour:

```python
# Two clicks: first keeps ascending (no data change),
# second switches to descending.
tables_page.click_column_header("Rank")   # 1st — stays ascending
tables_page.click_column_header("Rank")   # 2nd — now descending
```

This correctly verifies that sorting _does_ work, but also documents the UX flaw in the test's docstring.

---

## Files Changed

- `tests/test_tables.py` — `test_sort_by_rank` adapted to two-click pattern with numeric comparison

---

_Report generated 2026-07-01 during automated testing of https://practice-automation.com/tables/_
