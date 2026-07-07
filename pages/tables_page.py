"""
Page object for the Tables page (https://practice-automation.com/tables/).

Covers both the Simple Table and the Sortable Table (TablePress / DataTable).
"""

import re
from typing import Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.base_page import BasePage
import config


class TablesPage(BasePage):
    # ── Locators ─────────────────────────────────────────────────
    # Page heading for verification
    PAGE_HEADING = (By.TAG_NAME, "h1")

    # Simple Table: heading id and rows (the <figure> contains a basic HTML table)
    SIMPLE_TABLE_HEADING = (By.ID, "simple-table-item-prices")
    SIMPLE_TABLE_ALL_ROWS = (
        By.XPATH, "//h4[@id='simple-table-item-prices']/following-sibling::figure//table/tbody/tr"
    )

    # Sortable Table heading (outside the DataTable wrapper)
    SORTABLE_TABLE_HEADING = (By.ID, "sortable-table-countries-by-population")

    # Sortable Table (DataTables 2.x enhanced table)
    SORTABLE_TABLE = (By.ID, "tablepress-1")
    SORTABLE_TABLE_HEADERS = (By.CSS_SELECTOR, "#tablepress-1 thead th")
    SORTABLE_TABLE_ROWS = (By.CSS_SELECTOR, "#tablepress-1 tbody tr")

    # DataTable 2.x controls — the search input, entries dropdown, info text,
    # and pagination use DataTables-specific CSS classes / structure
    SEARCH_LABEL = (By.XPATH, "//label[contains(., 'Search:')]")
    SEARCH_INPUT = (By.CSS_SELECTOR, "div.dt-search input.dt-input[type='search']")
    ENTRIES_DROPDOWN = (By.CSS_SELECTOR, "div.dt-length select.dt-input")
    INFO_TEXT = (By.ID, "tablepress-1_info")
    PAGINATION_BUTTONS = (By.CSS_SELECTOR, "div.dt-paging button.dt-paging-button")

    # Source link below the Sortable Table that opens worldometers
    SOURCE_LINK = (By.XPATH, "//a[text()='Source']")

    # Worldometers source-of-truth table (standard datatable class)
    WORLDOMETERS_TABLE = (By.CSS_SELECTOR, "table.datatable")
    WORLDOMETERS_ROWS = (By.CSS_SELECTOR, "table.datatable tbody tr")

    # ══════════════════════════════════════════════════════════════
    # Availability check
    # ══════════════════════════════════════════════════════════════

    @property
    def is_available(self) -> bool:
        """Return True if the Simple Table heading is present on the page."""
        return self.is_element_available(self.SIMPLE_TABLE_HEADING)

    # ══════════════════════════════════════════════════════════════
    # Simple Table helpers
    # ══════════════════════════════════════════════════════════════

    def get_simple_table_heading_text(self) -> str:
        """Return the text of the Simple Table heading element."""
        return self.find_element(self.SIMPLE_TABLE_HEADING).text.strip()

    def get_simple_table_headers(self) -> list[str]:
        """Extract header labels from the first <tr> of the Simple Table.
        
        The Simple Table uses <td><strong> elements in the first data row
        as column headers, rather than <th> elements.
        """
        rows = self.driver.find_elements(*self.SIMPLE_TABLE_ALL_ROWS)
        if not rows:
            return []
        header_cells = rows[0].find_elements(By.TAG_NAME, "td")
        return [c.text.strip() for c in header_cells]

    def get_simple_table_data(self) -> list[dict[str, str]]:
        """Return Simple Table rows as [{header: value, ...}], skipping the header row.
        
        The first <tr> contains column labels; subsequent rows contain data.
        """
        rows = self.driver.find_elements(*self.SIMPLE_TABLE_ALL_ROWS)
        headers = self.get_simple_table_headers()
        data = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = {}
            for i, cell in enumerate(cells):
                if i < len(headers):
                    row_data[headers[i]] = cell.text.strip()
            if row_data:
                data.append(row_data)
        return data

    # ══════════════════════════════════════════════════════════════
    # Sortable Table helpers
    # ══════════════════════════════════════════════════════════════

    def get_sortable_table_heading_text(self) -> str:
        """Return the text of the Sortable Table heading element."""
        return self.find_element(self.SORTABLE_TABLE_HEADING).text.strip()

    def get_sortable_table_headers(self) -> list[str]:
        """Return the column header texts from the DataTable <thead>."""
        cells = self.driver.find_elements(*self.SORTABLE_TABLE_HEADERS)
        return [c.text.strip() for c in cells]

    def get_sortable_table_data(self) -> list[dict[str, str]]:
        """Return currently visible DataTable rows as [{header: value, ...}].
        
        Only returns rows that are currently rendered in the DOM (respecting
        pagination, search filtering, and entries-per-page settings).
        """
        rows = self.driver.find_elements(*self.SORTABLE_TABLE_ROWS)
        headers = self.get_sortable_table_headers()
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = {}
            for i, cell in enumerate(cells):
                if i < len(headers):
                    row_data[headers[i]] = cell.text.strip()
            if row_data:
                data.append(row_data)
        return data

    def get_sortable_table_info_text(self) -> str:
        """Return the DataTable info text, e.g. 'Showing 1 to 10 of 25 entries'."""
        return self.find_element(self.INFO_TEXT).text.strip()

    def get_pagination_page_numbers(self) -> list[str]:
        """Return the numeric page buttons currently shown in the pagination control."""
        try:
            buttons = self.driver.find_elements(*self.PAGINATION_BUTTONS)
            pages = []
            for btn in buttons:
                text = btn.text.strip()
                if text.isdigit():
                    pages.append(text)
            return pages
        except Exception:
            return []

    def click_pagination_page(self, page_number: str | int) -> None:
        """Click a specific pagination button by its visible page number.

        Uses _safe_click (JS-fallback) to handle overlay interception
        that can occur for elements at the bottom of the page in
        Chromium-based browsers (Edge, Opera).
        """
        locator = (By.XPATH, f"//button[contains(@class, 'dt-paging-button') and text()='{page_number}']")
        self._safe_click(locator)
        self._wait_for_table_ready()

    def _wait_for_table_ready(self) -> None:
        """Wait for DataTables to finish its asynchronous re-draw cycle.
        
        DataTables 2.x updates the DOM asynchronously after sort, filter,
        pagination, or page-length changes. This method polls the info text
        element (which DataTables updates after each re-draw) and returns
        once the text stabilises or a short timeout elapses.
        """
        try:
            info_loc = self.INFO_TEXT
            info_el = self.driver.find_element(*info_loc)
            old_text = info_el.text.strip()
            WebDriverWait(self.driver, config.SHORT_TIMEOUT).until(
                lambda d: d.find_element(*info_loc).text.strip() != old_text
            )
        except (TimeoutException, NoSuchElementException):
            try:
                WebDriverWait(self.driver, config.SHORT_TIMEOUT).until(
                    EC.presence_of_element_located(self.SORTABLE_TABLE_ROWS)
                )
            except TimeoutException:
                pass

    # ── Source link ──────────────────────────────────────────────

    def get_source_link_href(self) -> str:
        """Return the href attribute of the 'Source' link."""
        return self.find_element(self.SOURCE_LINK).get_attribute("href")

    def get_source_link_target(self) -> str:
        """Return the target attribute of the 'Source' link (should be '_blank')."""
        return self.find_element(self.SOURCE_LINK).get_attribute("target")

    def click_source_link(self) -> None:
        """Click the 'Source' link to open worldometers in a new tab.

        Uses _safe_click (JS-fallback) to handle overlay interception.
        """
        self._safe_click(self.SOURCE_LINK)

    # ── Entries per page ─────────────────────────────────────────

    def set_entries_per_page(self, value: str) -> None:
        """Set the DataTable page length via the entries dropdown.
        
        Valid values: '10', '25', '50', '100'. Triggers a re-draw and waits
        for the table to stabilise before returning.
        """
        select_el = self.find_element(self.ENTRIES_DROPDOWN)
        Select(select_el).select_by_value(value)
        self._wait_for_table_ready()

    def get_entries_per_page_value(self) -> str:
        """Return the currently selected entries-per-page value."""
        select_el = self.find_element(self.ENTRIES_DROPDOWN)
        return Select(select_el).first_selected_option.get_attribute("value")

    def get_entries_per_page_options(self) -> list[str]:
        """Return all option values from the entries-per-page dropdown."""
        select_el = self.find_element(self.ENTRIES_DROPDOWN)
        options = Select(select_el).options
        return [opt.get_attribute("value") for opt in options]

    # ── Search ───────────────────────────────────────────────────

    def get_search_label_text(self) -> str:
        """Return the text of the label element adjacent to the search input."""
        return self.find_element(self.SEARCH_LABEL).text.strip()

    def search(self, query: str) -> None:
        """Type a search query into the DataTable search field.
        
        DataTables filters all visible rows on each keystroke. After sending
        the full query, this method waits for the table to finish filtering.
        """
        inp = self.find_element(self.SEARCH_INPUT)
        inp.clear()
        inp.send_keys(query)
        self._wait_for_table_ready()

    def clear_search(self) -> None:
        """Clear the search input to restore all rows."""
        inp = self.find_element(self.SEARCH_INPUT)
        inp.clear()
        self._wait_for_table_ready()

    def get_search_input_value(self) -> str:
        """Return the current text in the search input."""
        return self.find_element(self.SEARCH_INPUT).get_attribute("value")

    # ── Sorting ──────────────────────────────────────────────────

    def click_column_header(self, column_name: str) -> None:
        """Click a column header to toggle its sort direction.
        
        Uses JavaScript dispatchEvent on the <th> element because DataTables 2.x
        intercepts native MouseEvents on header cells for sorting, and Selenium's
        ActionChains click does not reliably trigger DataTable's listener for
        `dt-type-numeric` columns (e.g. Rank).
        
        After dispatching the event, waits for the first data cell to change
        as confirmation that the sort completed. If the sort direction didn't
        change the row order (3-state cycle issue), the wait times out silently
        and the caller must handle it.
        """
        xpath = (
            f"//table[@id='tablepress-1']//th[.//span[@class='dt-column-title']"
            f" and contains(., '{column_name}')]"
        )
        header = self.find_element((By.XPATH, xpath))

        first_cell = self.driver.find_element(
            By.CSS_SELECTOR, "#tablepress-1 tbody tr:first-child td:first-child"
        )
        old_text = first_cell.text.strip()

        self.driver.execute_script("""
            arguments[0].dispatchEvent(new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window
            }));
        """, header)

        try:
            WebDriverWait(self.driver, config.SHORT_TIMEOUT).until(
                lambda d: d.find_element(
                    By.CSS_SELECTOR, "#tablepress-1 tbody tr:first-child td:first-child"
                ).text.strip() != old_text
            )
        except TimeoutException:
            pass

    def get_sorting_classes(self, column_name: str) -> list[str]:
        """Return the CSS classes of a column header (includes sort-direction indicators)."""
        xpath = (
            f"//table[@id='tablepress-1']//th[contains(., '{column_name}')]"
        )
        el = self.find_element((By.XPATH, xpath))
        return el.get_attribute("class").split()

    # ══════════════════════════════════════════════════════════════
    # Worldometers Source-of-Truth
    # ══════════════════════════════════════════════════════════════

    def extract_worldometers_data(self) -> list[dict[str, Any]]:
        """Extract the first 100 data rows from the worldometers population table.
        
        Returns a list of dicts with keys '#', 'Country', 'Population 2026'.
        Only the first three columns are extracted; the rest are ignored.
        """
        WebDriverWait(self.driver, config.LONG_TIMEOUT).until(
            EC.presence_of_element_located(self.WORLDOMETERS_ROWS)
        )

        rows = self.driver.find_elements(*self.WORLDOMETERS_ROWS)
        data = []
        for row in rows[:100]:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                row_data = {
                    "#": cells[0].text.strip(),
                    "Country": cells[1].text.strip(),
                    "Population 2026": cells[2].text.strip(),
                }
                data.append(row_data)
        return data

    def verify_worldometers_table_loaded(self) -> bool:
        """Check that the worldometers table has rendered at least 100 data rows.
        
        Returns False if the table isn't present or has fewer than 100 rows,
        which would make the source-of-truth comparison unreliable.
        """
        try:
            WebDriverWait(self.driver, config.LONG_TIMEOUT).until(
                EC.presence_of_element_located(self.WORLDOMETERS_ROWS)
            )
            rows = self.driver.find_elements(*self.WORLDOMETERS_ROWS)
            return len(rows) >= 100
        except TimeoutException:
            return False

    # ══════════════════════════════════════════════════════════════
    # Tab management
    # ══════════════════════════════════════════════════════════════

    def switch_to_new_tab(self, timeout: int = 10) -> None:
        """Wait for a new browser tab to open, then switch focus to it."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: len(d.window_handles) > 1
        )
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def switch_to_tab(self, index: int = 0) -> None:
        """Switch focus to the tab at the given index (0 = first/original)."""
        self.driver.switch_to.window(self.driver.window_handles[index])

    def close_current_tab(self) -> None:
        """Close the currently focused tab and switch back to the first tab."""
        self.driver.close()
        self.switch_to_tab(0)

    @property
    def tab_count(self) -> int:
        """Return the number of open browser tabs."""
        return len(self.driver.window_handles)

    # ══════════════════════════════════════════════════════════════
    # Normalize / compare helpers
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def normalize_country(name: str) -> str:
        """Normalise country names for comparison between tested table and source.
        
        Handles the 'D.R. Congo' → 'DR Congo' mapping, where the tested
        table uses a different abbreviation than the source.
        """
        mapping = {
            "D.R. Congo": "DR Congo",
            "D.R.Congo": "DR Congo",
            "DR Congo": "DR Congo",
        }
        return mapping.get(name, name)

    @staticmethod
    def parse_population_million(value: str) -> float | None:
        """Parse a population value from the tested table (in millions).
        
        Handles known formatting bugs:
        - '1,429' (comma as thousands separator instead of decimal dot)
        - '340' (integer instead of '340.0')
        - '277.5' (normal float)
        
        Returns the numeric value in millions, or None if unparseable.
        """
        if not value:
            return None
        cleaned = value.strip().replace(",", "").replace("$", "")
        try:
            return float(cleaned)
        except ValueError:
            return None

    @staticmethod
    def parse_population_source(value: str) -> float | None:
        """Parse a raw population value from worldometers and convert to millions.
        
        Source values are natural numbers (e.g. '1429000000' for India).
        Returns the value divided by 1 million as a float, or None if unparseable.
        Also handles commas within source values (e.g. '1,429,000,000').
        """
        if not value:
            return None
        cleaned = value.strip().replace(",", "")
        try:
            return float(cleaned) / 1_000_000
        except ValueError:
            return None

    @staticmethod
    def has_comma_bug(value: str) -> bool:
        """Check if a population value uses a comma instead of a dot as decimal separator.
        
        Detects patterns like '1,429' (comma where dot is expected).
        Values containing both comma and dot are not flagged (e.g. valid thousands format).
        """
        if not value:
            return False
        if "," in value:
            if "." in value:
                return False
            parts = value.split(",")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return True
        return False

    @staticmethod
    def has_integer_bug(value: str) -> bool:
        """Check if a population value is an integer where a float is expected.
        
        The column uses millions-as-float notation, so '340' should be '340.0'.
        Values that already contain a comma are skipped (they belong to the comma-bug category).
        """
        if not value:
            return False
        if "," in value:
            return False
        cleaned = value.strip()
        if cleaned.isdigit():
            return True
        return False

    @staticmethod
    def replace_comma_with_dot(value: str) -> str:
        """Replace comma with dot for parsing comparison values.
        
        This is a workaround for the comma-bug rows to allow parsing
        '1,429' as the float 1429.0 instead of failing on the comma.
        """
        return value.replace(",", ".")
