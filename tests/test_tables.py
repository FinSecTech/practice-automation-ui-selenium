"""
Tests for the Tables page (https://practice-automation.com/tables/).

Covers:
- Simple Table: layout, heading, column names, data validation
- Sortable Table: layout, heading, source link, data comparison with worldometers,
  bug detection (comma/integer), entries per page, sorting, pagination, search
"""

import re
import pytest
from pages.tables_page import TablesPage


class TestSimpleTable:
    """Verifies the Simple Table heading, column structure, and per-cell data format."""

    def test_simple_table_heading(self, tables_page: TablesPage):
        """The heading above the Simple Table must read exactly 'Simple Table'."""
        heading = tables_page.get_simple_table_heading_text()
        assert heading == "Simple Table", (
            f"Simple Table heading expected 'Simple Table', got '{heading}'"
        )

    def test_simple_table_column_names(self, tables_page: TablesPage):
        """First column header must be 'Item', second must be 'Price'."""
        headers = tables_page.get_simple_table_headers()
        assert len(headers) >= 2, (
            f"Expected at least 2 columns, got {len(headers)}"
        )
        assert headers[0] == "Item", (
            f"Column 1 expected 'Item', got '{headers[0]}'"
        )
        assert headers[1] == "Price", (
            f"Column 2 expected 'Price', got '{headers[1]}'"
        )

    def test_simple_table_column1_text_only(self, tables_page: TablesPage):
        """All values in the Item column must be English alphabet letters only (a-z, A-Z).
        
        Checks both isalpha() to reject digits/symbols, and a regex to reject
        non-English characters (e.g. Cyrillic, accents).
        """
        data = tables_page.get_simple_table_data()
        assert len(data) > 0, "Simple Table has no data rows"

        for row_idx, row in enumerate(data, start=1):
            col1_value = row.get("Item", "")
            assert col1_value.isalpha(), (
                f"Row {row_idx}, Column 'Item' value '{col1_value}' "
                f"contains non-alphabetic characters"
            )
            assert re.fullmatch(r"[A-Za-z]+", col1_value), (
                f"Row {row_idx}, Column 'Item' value '{col1_value}' "
                f"contains non-English-alphabet characters"
            )

    def test_simple_table_column2_price_format(self, tables_page: TablesPage):
        """All values in the Price column must start with '$' followed by a positive float.
        
        Validates: prefix '$', then digits with optional decimal portion,
        parseable as a non-negative float.
        """
        data = tables_page.get_simple_table_data()
        assert len(data) > 0, "Simple Table has no data rows"

        for row_idx, row in enumerate(data, start=1):
            col2_value = row.get("Price", "")
            assert col2_value.startswith("$"), (
                f"Row {row_idx}, Column 'Price' value '{col2_value}' "
                f"does not start with '$'"
            )

            numeric_part = col2_value[1:]

            assert re.fullmatch(r"\d+(\.\d+)?", numeric_part), (
                f"Row {row_idx}, Column 'Price' value '{col2_value}' "
                f"has non-numeric characters after '$'"
            )

            try:
                float_val = float(numeric_part)
                assert float_val >= 0, (
                    f"Row {row_idx}, Column 'Price' value '{col2_value}' "
                    f"is negative"
                )
            except ValueError:
                pytest.fail(
                    f"Row {row_idx}, Column 'Price' value '{col2_value}' "
                    f"cannot be parsed as a float"
                )


class TestSortableTableHeadingAndSource:
    """Verifies the Sortable Table heading exists and the Source link points to the correct URL."""

    def test_sortable_table_heading(self, tables_page: TablesPage):
        """The heading above the Sortable Table must read exactly 'Sortable Table'."""
        heading = tables_page.get_sortable_table_heading_text()
        assert heading == "Sortable Table", (
            f"Sortable Table heading expected 'Sortable Table', got '{heading}'"
        )

    def test_source_link_exists_and_opens_new_tab(self, tables_page: TablesPage):
        """The 'Source' link must href to worldometers and open in a new tab (_blank).
        
        This link is the basis for the source-of-truth comparison tests.
        """
        href = tables_page.get_source_link_href()
        expected_url = (
            "https://www.worldometers.info/world-population/population-by-country/"
        )
        assert href == expected_url, (
            f"Source link href expected '{expected_url}', got '{href}'"
        )

        target = tables_page.get_source_link_target()
        assert target == "_blank", (
            f"Source link target expected '_blank', got '{target}'"
        )


class TestSourceOfTruth:
    """Fetches population data from worldometers and compares it against the Sortable Table.
    
    This test fixture navigates to the source URL in a new tab, extracts 100 data rows,
    returns to the original tab, and provides the data to comparison tests.
    The comparison is expected to identify discrepancies because the tested table
    may have outdated data.
    """

    @pytest.fixture
    def source_data(self, tables_page: TablesPage) -> list[dict]:
        """Navigate to the worldometers source, extract 100 rows, return to the tables page."""
        initial_tab_count = tables_page.tab_count

        tables_page.click_source_link()
        tables_page.switch_to_new_tab()

        loaded = tables_page.verify_worldometers_table_loaded()
        if not loaded:
            tables_page.close_current_tab()
            pytest.fail(
                "Source-of-truth page (worldometers) did not load a table "
                "with at least 100 rows — cannot proceed with comparison."
            )

        world_data = tables_page.extract_worldometers_data()

        assert len(world_data) >= 100, (
            f"Expected at least 100 data rows from worldometers, "
            f"got {len(world_data)}"
        )

        tables_page.switch_to_tab(0)

        assert tables_page.is_available, (
            "Failed to return to the tables page after fetching source of truth"
        )

        tables_page.set_entries_per_page("25")
        return world_data

    def test_sortable_table_column_names(self, tables_page: TablesPage):
        """Column headers must contain 'Rank', 'Country', and 'Population' substrings.
        
        Note: the tested table uses 'Rank' while the source uses '#' — this is expected.
        """
        headers = tables_page.get_sortable_table_headers()
        assert len(headers) >= 3, f"Expected at least 3 columns, got {len(headers)}"

        assert "Rank" in headers[0], (
            f"Column 1 expected to contain 'Rank', got '{headers[0]}'"
        )
        assert "Country" in headers[1], (
            f"Column 2 expected to contain 'Country', got '{headers[1]}'"
        )
        assert "Population" in headers[2], (
            f"Column 3 expected to contain 'Population', got '{headers[2]}'"
        )

    def test_compare_column1_rank(self, tables_page: TablesPage, source_data: list[dict]):
        """Every Rank value in the tested table must exist in the source # column (set membership).
        
        The source contains ranks 1..100; the tested table shows only the first 25.
        This test does not check order — only that no unexpected rank values appear.
        """
        tested_data = tables_page.get_sortable_table_data()
        assert len(tested_data) == 25, (
            f"Expected 25 rows in Sortable Table, got {len(tested_data)}"
        )

        source_ranks: set[str] = {row["#"] for row in source_data}

        errors: list[str] = []
        for row_idx, row in enumerate(tested_data, start=1):
            rank = row.get("Rank", "")
            if rank not in source_ranks:
                errors.append(
                    f"Row {row_idx}: Rank '{rank}' not found in source-of-truth # values"
                )

        if errors:
            pytest.fail(
                f"Column 1 (Rank) comparison failed:\n  " + "\n  ".join(errors)
            )

    def test_compare_column2_country(self, tables_page: TablesPage, source_data: list[dict]):
        """Every Country value in the tested table must appear in the source data.
        
        Two checks:
        1. Set membership — every tested country (normalized) exists in the source set.
        2. Pairwise — row N tested matches row N source (expected to fail with outdated data).
        
        Special mapping: 'D.R. Congo' (tested) normalises to 'DR Congo' (source).
        """
        tested_data = tables_page.get_sortable_table_data()
        assert len(tested_data) == 25

        source_countries: dict[str, str] = {}
        for row in source_data:
            norm = tables_page.normalize_country(row["Country"])
            source_countries[norm] = row["Country"]

        tested_countries: dict[str, str] = {}
        for row_idx, row in enumerate(tested_data, start=1):
            norm = tables_page.normalize_country(row.get("Country", ""))
            tested_countries[f"row{row_idx}"] = {
                "original": row.get("Country", ""),
                "normalized": norm,
            }

        membership_errors: list[str] = []
        pairwise_errors: list[str] = []

        for key, info in tested_countries.items():
            norm = info["normalized"]
            if norm not in source_countries:
                membership_errors.append(
                    f"{key} ('{info['original']}', normalized '{norm}'): "
                    f"not found in source-of-truth countries"
                )

        if membership_errors:
            pytest.fail(
                f"Column 2 (Country) set-membership errors:\n  "
                + "\n  ".join(membership_errors)
            )

        for idx, tested_row in enumerate(tested_data):
            tested_country = tables_page.normalize_country(
                tested_row.get("Country", "")
            )
            if idx < len(source_data):
                source_country = tables_page.normalize_country(
                    source_data[idx]["Country"]
                )
                if tested_country != source_country:
                    pairwise_errors.append(
                        f"Row {idx + 1}: tested '{tested_row.get('Country', '')}' "
                        f"(normalized '{tested_country}') vs "
                        f"source '{source_data[idx]['Country']}' "
                        f"(normalized '{source_country}')"
                    )

        if pairwise_errors:
            pytest.fail(
                f"Column 2 (Country) pairwise comparison found mismatches "
                f"(expected with outdated data):\n  "
                + "\n  ".join(pairwise_errors)
            )

    def test_compare_column3_population(self, tables_page: TablesPage, source_data: list[dict]):
        """Population values in millions must match source data divided by 1 million.
        
        Source values are raw integer counts (e.g. 1429000000 for India).
        Tested values are already in millions as floats (e.g. 1429.0).
        
        Known bugs that are detected but not failed here:
        - Comma-as-decimal bug (rows 1,2): '1,429' instead of '1.429'
        - Integer-bug (rows 3,8,15,16,18): '340' instead of '340.0'
        
        This comparison is expected to fail because the tested table data is outdated.
        """
        tested_data = tables_page.get_sortable_table_data()
        assert len(tested_data) == 25

        source_pops: list[float] = []
        source_pop_set: set[float] = set()
        for row in source_data:
            val = tables_page.parse_population_source(row["Population 2026"])
            if val is not None:
                rounded = round(val, 1)
                source_pops.append(rounded)
                source_pop_set.add(rounded)

        tested_pops: list[dict] = []
        comma_bug_rows: list[int] = []
        int_bug_rows: list[int] = []

        for idx, row in enumerate(tested_data):
            raw_value = row.get("Population (million)", "")

            if tables_page.has_comma_bug(raw_value):
                comma_bug_rows.append(idx + 1)

            if tables_page.has_integer_bug(raw_value):
                int_bug_rows.append(idx + 1)

            cleaned = tables_page.replace_comma_with_dot(raw_value)
            parsed = tables_page.parse_population_million(cleaned)

            tested_pops.append({
                "row": idx + 1,
                "raw": raw_value,
                "parsed": parsed,
                "has_comma_bug": "," in raw_value and "." not in raw_value,
                "has_int_bug": raw_value.replace(",", "").isdigit(),
            })

        membership_errors: list[str] = []
        for item in tested_pops:
            if item["parsed"] is not None:
                rounded = round(item["parsed"], 1)
                if rounded not in source_pop_set:
                    membership_errors.append(
                        f"Row {item['row']}: value '{item['raw']}' (parsed {item['parsed']}, "
                        f"rounded {rounded}) not in source-of-truth population set"
                    )

        pairwise_errors: list[str] = []
        for item in tested_pops:
            idx = item["row"] - 1
            if idx < len(source_pops) and item["parsed"] is not None:
                tested_rounded = round(item["parsed"], 1)
                source_rounded = source_pops[idx]
                if tested_rounded != source_rounded:
                    pairwise_errors.append(
                        f"Row {item['row']}: tested '{item['raw']}' ({tested_rounded}) vs "
                        f"source {source_data[idx]['Population 2026']} "
                        f"(-> {source_rounded} million)"
                    )

        result_lines = []
        if comma_bug_rows:
            result_lines.append(
                f"NOTE — Comma-bug detected in rows: {comma_bug_rows} "
                f"(tested separately in TestCommaBug)"
            )
        if int_bug_rows:
            result_lines.append(
                f"NOTE — Integer-bug detected in rows: {int_bug_rows} "
                f"(tested separately in TestIntegerBug)"
            )
        if membership_errors:
            result_lines.append(
                "Set-membership errors:\n  " + "\n  ".join(membership_errors)
            )
        if pairwise_errors:
            result_lines.append(
                "Pairwise comparison errors (expected with outdated data):\n  "
                + "\n  ".join(pairwise_errors)
            )

        if result_lines:
            pytest.fail("\n".join(result_lines))


class TestCommaBug:
    """Detects rows where a comma is used instead of a dot as the decimal separator.
    
    The Population column is expected to use dot as decimal separator (e.g. '1429.0').
    Rows 1 (India, '1,429') and 2 (China, '1,426') incorrectly use a comma.
    """

    def test_comma_as_decimal_separator_bug(self, tables_page: TablesPage):
        """Rows 1 (India) and 2 (China) should show '1,429' and '1,426' (comma-bug).
        
        The comma here acts as a thousands separator in human-readable format,
        but this column uses millions-as-float notation, so a dot is expected.
        Any row matching the comma pattern is flagged regardless of position.
        """
        tables_page.set_entries_per_page("100")
        data = tables_page.get_sortable_table_data()
        assert len(data) >= 25, f"Expected at least 25 rows, got {len(data)}"

        expected_buggy_rows = [0, 1]

        comma_rows_found: list[dict] = []
        for idx, row in enumerate(data):
            pop_value = row.get("Population (million)", "")
            if "," in pop_value and "." not in pop_value:
                parts = pop_value.split(",")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    comma_rows_found.append({
                        "row": idx + 1,
                        "country": row.get("Country", ""),
                        "value": pop_value,
                    })

        bug_report: list[str] = []
        missing_bugs: list[str] = []

        for expected_idx in expected_buggy_rows:
            found = any(
                item["row"] == expected_idx + 1 for item in comma_rows_found
            )
            if found:
                matched = [item for item in comma_rows_found if item["row"] == expected_idx + 1]
                bug_report.append(
                    f"  ✓ Row {matched[0]['row']} ({matched[0]['country']}): "
                    f"value '{matched[0]['value']}' uses comma (bug)"
                )
            else:
                missing_bugs.append(
                    f"  ✗ Row {expected_idx + 1}: expected comma-bug but value "
                    f"'{data[expected_idx].get('Population (million)', '')}' "
                    f"does not contain the expected comma pattern"
                )

        if bug_report:
            print("\n=== Comma Bug Report ===")
            for line in bug_report:
                print(line)

        if missing_bugs:
            print("\n=== Expected bugs not found ===")
            for line in missing_bugs:
                print(line)

        result_msg = ""
        if bug_report:
            result_msg += "Comma-bug rows detected:\n" + "\n".join(bug_report)
        if missing_bugs:
            result_msg += "\n\nExpected but not found:\n" + "\n".join(missing_bugs)

        if len(comma_rows_found) < 2:
            pytest.fail(
                f"Expected at least 2 rows with comma-bug, found {len(comma_rows_found)}. "
                + result_msg
            )

        pytest.fail(
            "BUG DETECTED: The following rows use comma instead of dot as "
            "decimal separator in the Population column:\n" + "\n".join(
                f"  Row {item['row']} ({item['country']}): '{item['value']}'"
                for item in comma_rows_found
            )
        )


class TestIntegerBug:
    """Detects rows where the Population value is an integer instead of a float.
    
    The column uses millions-as-float notation, so '340' should be '340.0'.
    Expected buggy rows: 3 (United States), 8 (Bangladesh), 15 (D.R. Congo),
    16 (Vietnam), 18 (Iran).
    """

    def test_integer_not_float_bug(self, tables_page: TablesPage):
        """Integer values in the Population column should be flagged as bugs.
        
        Only values without a decimal point (and without a comma — those are
        comma-bug rows) are considered integer-bug rows.
        """
        tables_page.set_entries_per_page("100")
        data = tables_page.get_sortable_table_data()
        assert len(data) >= 25, f"Expected at least 25 rows, got {len(data)}"

        expected_buggy_indices = [2, 7, 14, 15, 17]

        int_bug_rows: list[dict] = []
        for idx, row in enumerate(data):
            pop_value = row.get("Population (million)", "")
            cleaned = pop_value.strip().replace(",", "")
            if cleaned.isdigit():
                int_bug_rows.append({
                    "row": idx + 1,
                    "country": row.get("Country", ""),
                    "value": pop_value,
                })

        bug_report: list[str] = []
        for item in int_bug_rows:
            bug_report.append(
                f"  Row {item['row']} ({item['country']}): '{item['value']}' "
                f"is integer, expected float format (e.g. '{item['value']}.0')"
            )

        found_indices = {item["row"] for item in int_bug_rows}
        missing = [
            f"Row {idx + 1} ('{data[idx].get('Country', '')}', "
            f"'{data[idx].get('Population (million)', '')}')"
            for idx in expected_buggy_indices
            if (idx + 1) not in found_indices
        ]

        if bug_report:
            print("\n=== Integer Bug Report ===")
            for line in bug_report:
                print(line)

        if missing:
            print("\n=== Expected integer bugs not found ===")
            for line in missing:
                print(line)

        if not bug_report:
            pytest.fail(
                "No integer-bug rows found. Expected rows 3, 8, 15, 16, 18 "
                "to have integer values in Population column."
            )

        pytest.fail(
            "BUG DETECTED: The following rows use integer instead of float "
            "in the Population column:\n" + "\n".join(bug_report)
        )


class TestEntriesPerPage:
    """Verifies the entries-per-page dropdown options and that the info text
    correctly reflects the displayed row count.
    
    With only 25 rows in the table, any page size option ≥ 25 should show
    'Showing 1 to 25 of 25 entries' with a single pagination page.
    """

    def test_entries_dropdown_has_correct_options(self, tables_page: TablesPage):
        """The entries dropdown must contain options 10, 25, 50, 100."""
        options = tables_page.get_entries_per_page_options()
        expected_options = ["10", "25", "50", "100"]
        for opt in expected_options:
            assert opt in options, (
                f"Expected option '{opt}' not found in entries dropdown: {options}"
            )

    def test_entries_25_shows_correct_info(self, tables_page: TablesPage):
        """Set to 25 entries: info text must say 'Showing 1 to 25 of 25 entries'."""
        tables_page.set_entries_per_page("25")
        info_text = tables_page.get_sortable_table_info_text()
        assert info_text == "Showing 1 to 25 of 25 entries", (
            f"Expected 'Showing 1 to 25 of 25 entries', got '{info_text}'"
        )

        data = tables_page.get_sortable_table_data()
        assert len(data) == 25, (
            f"Expected 25 rows displayed, got {len(data)}"
        )

        pages = tables_page.get_pagination_page_numbers()
        assert len(pages) <= 1, (
            f"Expected 0 or 1 pagination page, got {len(pages)}: {pages}"
        )

    def test_entries_50_shows_correct_info(self, tables_page: TablesPage):
        """Set to 50 entries: still shows all 25 rows, info text unchanged."""
        tables_page.set_entries_per_page("50")
        info_text = tables_page.get_sortable_table_info_text()
        assert info_text == "Showing 1 to 25 of 25 entries", (
            f"Expected 'Showing 1 to 25 of 25 entries', got '{info_text}'"
        )

        data = tables_page.get_sortable_table_data()
        assert len(data) == 25, (
            f"Expected 25 rows displayed, got {len(data)}"
        )

    def test_entries_100_shows_correct_info(self, tables_page: TablesPage):
        """Set to 100 entries: still shows all 25 rows, info text unchanged."""
        tables_page.set_entries_per_page("100")
        info_text = tables_page.get_sortable_table_info_text()
        assert info_text == "Showing 1 to 25 of 25 entries", (
            f"Expected 'Showing 1 to 25 of 25 entries', got '{info_text}'"
        )

        data = tables_page.get_sortable_table_data()
        assert len(data) == 25, (
            f"Expected 25 rows displayed, got {len(data)}"
        )


class TestSorting:
    """Verifies that clicking each column header sorts the table data correctly.
    
    DataTables 2.x uses a 3-state sort cycle for columns: clicking an already-sorted
    column re-applies ascending (no data change), then descending, then ascending again.
    Columns that start unordered go directly to ascending on first click.
    """

    def _extract_column_values(self, data: list[dict], header: str) -> list[str]:
        """Extract values for a given column header from table data."""
        return [row.get(header, "") for row in data]

    def test_sort_by_rank(self, tables_page: TablesPage):
        """Click Rank header twice to toggle from ascending to descending, then back.
        
        Rank starts as the default-sorted column (ascending). The first click
        re-applies ascending (no visible data change, only the arrow icon changes).
        The second click switches to descending (25..1). The third click returns
        to ascending (1..25). This 3-state cycle is a DataTables 2.x behaviour
        and is arguably a UX flaw (documented in reports/sort_ux_flaw_ranking_column.md).
        
        Numeric comparison is used because string comparison of ranks
        ('25' < '9') would give wrong results.
        """
        tables_page.set_entries_per_page("100")

        data_before = tables_page.get_sortable_table_data()
        ranks_before = self._extract_column_values(data_before, "Rank")

        tables_page.click_column_header("Rank")
        tables_page.click_column_header("Rank")

        data_after_two_clicks = tables_page.get_sortable_table_data()
        ranks_after = self._extract_column_values(data_after_two_clicks, "Rank")

        assert ranks_after != ranks_before, (
            "Rank order did not change after two clicks (should become descending)"
        )

        ranks_ints = [int(r) for r in ranks_after]
        assert ranks_ints == sorted(ranks_ints, reverse=True), (
            f"Rank not sorted descending: {ranks_after[:5]}"
        )

        tables_page.click_column_header("Rank")
        data_after_third_click = tables_page.get_sortable_table_data()
        ranks_after_third = self._extract_column_values(
            data_after_third_click, "Rank"
        )

        ranks_third_ints = [int(r) for r in ranks_after_third]
        assert ranks_third_ints == sorted(ranks_third_ints), (
            f"Rank not sorted ascending after third click: {ranks_after_third[:5]}"
        )

    def test_sort_by_country(self, tables_page: TablesPage):
        """Click Country header to sort ascending (A→Z), verify all columns update.
        
        Country starts unsorted, so a single click sorts ascending.
        After sorting, ranks must still be unique (no duplicate rows).
        """
        tables_page.set_entries_per_page("100")

        data_before = tables_page.get_sortable_table_data()
        countries_before = self._extract_column_values(data_before, "Country")

        tables_page.click_column_header("Country")
        data_after = tables_page.get_sortable_table_data()
        countries_after = self._extract_column_values(data_after, "Country")

        assert countries_after != countries_before, (
            "Country order did not change after clicking header"
        )

        assert countries_after == sorted(countries_after), (
            f"Countries not sorted ascending: {countries_after[:5]}"
        )

        ranks_after = self._extract_column_values(data_after, "Rank")
        assert len(ranks_after) == len(set(ranks_after)), (
            "Ranks are not unique after sorting by Country"
        )

    def test_sort_by_population(self, tables_page: TablesPage):
        """Click Population header to sort ascending, verify data integrity.
        
        Population starts unsorted, so a single click sorts ascending.
        The set of population values must be preserved after sorting
        (no rows added or removed).
        """
        tables_page.set_entries_per_page("100")

        data_before = tables_page.get_sortable_table_data()
        pop_before = self._extract_column_values(data_before, "Population (million)")

        tables_page.click_column_header("Population (million)")
        data_after = tables_page.get_sortable_table_data()
        pop_after = self._extract_column_values(data_after, "Population (million)")

        assert pop_after != pop_before, (
            "Population order did not change after clicking header"
        )

        assert set(pop_after) == set(pop_before), (
            "Population values changed after sorting (different values appeared)"
        )


class TestPagination:
    """Verifies pagination behaviour when set to 10 entries per page.
    
    With 25 rows and 10 per page: 3 pages (10 + 10 + 5 rows).
    Tests info text, page navigation, and data uniqueness across pages.
    """

    def test_pagination_with_10_entries(self, tables_page: TablesPage):
        """Set to 10 entries: navigate pages 1→2→3, verify info text and row counts."""
        tables_page.set_entries_per_page("10")

        info_text = tables_page.get_sortable_table_info_text()
        assert "Showing 1 to 10 of 25 entries" in info_text, (
            f"Expected info text containing 'Showing 1 to 10 of 25 entries', "
            f"got '{info_text}'"
        )

        pages = tables_page.get_pagination_page_numbers()
        assert len(pages) >= 3, (
            f"Expected at least 3 pagination pages, got {len(pages)}: {pages}"
        )

        data_page1 = tables_page.get_sortable_table_data()
        assert len(data_page1) == 10, (
            f"Expected 10 rows on page 1, got {len(data_page1)}"
        )

        tables_page.click_pagination_page("2")
        info_page2 = tables_page.get_sortable_table_info_text()
        assert "Showing 11 to 20 of 25 entries" in info_page2, (
            f"Expected page 2 info, got '{info_page2}'"
        )
        data_page2 = tables_page.get_sortable_table_data()
        assert len(data_page2) == 10, (
            f"Expected 10 rows on page 2, got {len(data_page2)}"
        )

        ranks_p1 = [r.get("Rank", "") for r in data_page1]
        ranks_p2 = [r.get("Rank", "") for r in data_page2]
        assert set(ranks_p1).isdisjoint(set(ranks_p2)), (
            "Page 1 and page 2 contain overlapping Rank values"
        )

        tables_page.click_pagination_page("3")
        info_page3 = tables_page.get_sortable_table_info_text()
        assert "Showing 21 to 25 of 25 entries" in info_page3, (
            f"Expected page 3 info, got '{info_page3}'"
        )
        data_page3 = tables_page.get_sortable_table_data()
        assert len(data_page3) == 5, (
            f"Expected 5 rows on page 3, got {len(data_page3)}"
        )


class TestSearch:
    """Verifies the DataTable search field filters rows correctly.
    
    Tests: label presence, uppercase/lowercase letter search (case-insensitive),
    and numeric search. Each search returns a specific expected result count.
    """

    def test_search_label_present(self, tables_page: TablesPage):
        """The text 'Search:' must be visible next to the search input."""
        label_text = tables_page.get_search_label_text()
        assert "Search:" in label_text, (
            f"Expected 'Search:' in label, got '{label_text}'"
        )

    def test_search_uppercase_L(self, tables_page: TablesPage):
        """Search for uppercase 'L' must return exactly 5 rows.
        
        Each returned row must contain 'L' or 'l' in some column.
        """
        tables_page.set_entries_per_page("100")
        tables_page.search("L")

        data = tables_page.get_sortable_table_data()
        assert len(data) == 5, (
            f"Expected 5 results for search 'L', got {len(data)}"
        )

        for row in data:
            all_values = " ".join(row.values())
            assert "L" in all_values or "l" in all_values, (
                f"Row '{row}' does not contain 'L' or 'l'"
            )

    def test_search_lowercase_l(self, tables_page: TablesPage):
        """Search for lowercase 'l' must return the same rows as uppercase 'L'.
        
        This confirms DataTables search is case-insensitive by default.
        """
        tables_page.set_entries_per_page("100")

        tables_page.search("L")
        data_upper = tables_page.get_sortable_table_data()
        upper_ranks = {r.get("Rank", "") for r in data_upper}

        tables_page.clear_search()
        tables_page.search("l")
        data_lower = tables_page.get_sortable_table_data()
        lower_ranks = {r.get("Rank", "") for r in data_lower}

        assert len(data_upper) == len(data_lower), (
            f"Search 'L' returned {len(data_upper)} results, "
            f"but search 'l' returned {len(data_lower)} results — "
            f"expected same count (case-insensitive search)"
        )

        assert upper_ranks == lower_ranks, (
            f"Search 'L' and 'l' returned different result sets: "
            f"upper ranks {upper_ranks} vs lower ranks {lower_ranks}"
        )

    def test_search_number_17(self, tables_page: TablesPage):
        """Search for the number '17' must return exactly 3 rows.
        
        Each returned row must contain '17' in some column.
        """
        tables_page.set_entries_per_page("100")
        tables_page.search("17")

        data = tables_page.get_sortable_table_data()
        assert len(data) == 3, (
            f"Expected 3 results for search '17', got {len(data)}"
        )

        for row in data:
            all_values = " ".join(row.values())
            assert "17" in all_values, f"Row '{row}' does not contain '17'"
