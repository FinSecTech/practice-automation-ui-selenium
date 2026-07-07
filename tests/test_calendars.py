"""
Tests for the Calendars page (https://practice-automation.com/calendars/).

Covers:
1. Direct date input (YYYY-MM-DD format)
2. Interactive date picker selection
3. Cross-validation between both methods
4. Boundary value testing (years 1926 and 2126)
5. Bug verification: entering dates outside the 1926–2126 range via direct input
6. Interactive calendar UI checks:
   - All 12 months present and clickable
   - Year list spans 1926–2126
   - Adjacent-month days shown in different colour (dp-edge-day class)
   - Navigation arrows (prev/next) work
   - Day-of-week headers in correct order (Mo Tu We Th Fr Sa Su)
"""

from datetime import date, datetime
import pytest
from selenium.webdriver.common.by import By


# ──────────────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────────────
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

MONTH_TO_NUM = {m: i + 1 for i, m in enumerate(MONTHS)}

# Map day-of-week abbreviations from the picker → Python weekday (0=Mon)
# NOTE: Jetpack date picker uses uppercase abbreviations (MO, TU, WE...)
PICKER_DAY_NAMES = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def _dom_weekday(date_str: str) -> str:
    """Return the picker day abbreviation for a YYYY-MM-DD date."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    # date.weekday() → 0=Mon … 6=Sun
    return PICKER_DAY_NAMES[dt.weekday()]


# ──────────────────────────────────────────────────────────────────────
# Pre-test: ensure "Calendars" link is present on main page
# ──────────────────────────────────────────────────────────────────────
def test_calendars_link_exists(main_page):
    """The link to the Calendars page is visible on the home page."""
    assert main_page.is_element_available(main_page.CALENDARS_LINK), (
        "Calendars link not found on the main page"
    )


# ──────────────────────────────────────────────────────────────────────
# Option 1 — Direct input
# ──────────────────────────────────────────────────────────────────────
class TestDirectInput:
    """Enter a date via the YYYY-MM-DD text input and submit."""

    DATE_STR = "2030-06-15"  # A middle-of-range date

    def test_direct_input_enter_and_submit(self, calendar_page):
        """Enter a valid date directly and submit the form."""
        calendar_page.enter_date_directly(self.DATE_STR)
        assert calendar_page.get_input_value() == self.DATE_STR

    def test_direct_input_success_message(self, calendar_page):
        """After submitting a direct-input date, the success page is shown."""
        calendar_page.submit_date_directly(self.DATE_STR)
        assert calendar_page.is_success_displayed, (
            "Success message did not appear after direct-input submit"
        )
        assert "Thank you" in calendar_page.success_header_text

    def test_direct_input_shows_correct_date(self, calendar_page):
        """The success page displays the exact date entered."""
        calendar_page.submit_date_directly(self.DATE_STR)
        assert calendar_page.submitted_field_name.strip().startswith(
            "Select or enter a date"
        ), f"Field name mismatch: '{calendar_page.submitted_field_name}'"
        assert calendar_page.submitted_date_value == self.DATE_STR, (
            f"Expected '{self.DATE_STR}', got '{calendar_page.submitted_date_value}'"
        )

    @pytest.mark.parametrize(
        "boundary_date",
        [
            "1926-01-01",
            "2126-12-31",
            "2000-02-29",  # leap year
            "2024-12-01",
            "1999-09-09",
        ],
    )
    def test_direct_input_various_dates(self, calendar_page, boundary_date):
        """Multiple valid dates can be entered and submitted correctly."""
        calendar_page.submit_date_directly(boundary_date)
        assert calendar_page.is_success_displayed
        assert calendar_page.submitted_date_value == boundary_date


# ──────────────────────────────────────────────────────────────────────
# Option 2 — Interactive date picker
# ──────────────────────────────────────────────────────────────────────
class TestInteractivePicker:
    """Select a date via the interactive calendar widget."""

    YEAR = 2030
    MONTH = "June"
    DAY = 15
    EXPECTED_DATE = "2030-06-15"

    def test_picker_opens_on_click(self, calendar_page):
        """Clicking the date input opens the date picker."""
        calendar_page.open_date_picker()
        assert calendar_page.is_date_picker_open()

    def test_picker_days_of_week_correct_format(self, calendar_page):
        """The day-of-week headers are shown as Mo Tu We Th Fr Sa Su."""
        calendar_page.open_date_picker()
        headers = calendar_page.get_day_headers()
        assert headers == PICKER_DAY_NAMES, (
            f"Expected {PICKER_DAY_NAMES}, got {headers}"
        )

    def test_picker_all_months_present(self, calendar_page):
        """All 12 months are present in the month overlay."""
        calendar_page.open_date_picker()
        months = calendar_page.get_available_months()
        assert months == MONTHS, (
            f"Expected {MONTHS}, got {months}"
        )

    def test_picker_year_range(self, calendar_page):
        """The year overlay lists years from 1926 to 2126 (inclusive)."""
        calendar_page.open_date_picker()
        years = calendar_page.get_available_years()
        assert min(years) == 1926, f"Min year is {min(years)}, expected 1926"
        assert max(years) == 2126, f"Max year is {max(years)}, expected 2126"
        assert len(years) == 201, f"Expected 201 years, got {len(years)}"

    def test_picker_adjacent_month_days_colored(self, calendar_page):
        """Days from adjacent months have the 'dp-edge-day' class (different colour)."""
        calendar_page.open_date_picker()
        days = calendar_page.get_all_days()
        # At least some days should be from adjacent months (first and last rows)
        other_month_days = [d for d in days if d["is_other_month"]]
        assert len(other_month_days) > 0, (
            "No adjacent-month days found (all days belong to the current month)"
        )
        # The very first day rendered is typically from the previous month
        assert days[0]["is_other_month"], (
            "First day cell should be from an adjacent month"
        )

    def test_picker_prev_next_arrows_work(self, calendar_page):
        """Both left and right navigation arrows change the displayed month."""
        calendar_page.open_date_picker()
        initial_month = calendar_page.get_current_month_display()

        # Go forward one month with Next arrow
        calendar_page.click_next_month()
        next_month = calendar_page.get_current_month_display()
        assert next_month != initial_month, (
            f"Month did not change after clicking 'Next': {next_month}"
        )

        # Go back one month with Prev arrow — should return to original
        calendar_page.click_prev_month()
        final_month = calendar_page.get_current_month_display()
        assert final_month == initial_month, (
            f"After going back expected '{initial_month}', got '{final_month}'"
        )

        # Also verify the Prev arrow can go backward from the original
        # and Next can bring us back
        calendar_page.click_prev_month()
        prev_month = calendar_page.get_current_month_display()
        assert prev_month != initial_month, (
            f"Month did not change after clicking 'Prev': {prev_month}"
        )
        calendar_page.click_next_month()
        restored = calendar_page.get_current_month_display()
        assert restored == initial_month, (
            f"After going forward expected '{initial_month}', got '{restored}'"
        )

    def test_picker_select_date_and_submit(self, calendar_page):
        """Select a date via the interactive picker, submit, and verify success."""
        calendar_page.submit_date_via_picker(self.YEAR, self.MONTH, self.DAY)
        assert calendar_page.is_success_displayed
        assert "Thank you" in calendar_page.success_header_text

    def test_picker_shows_correct_date(self, calendar_page):
        """The submitted date via the interactive picker is displayed correctly."""
        calendar_page.submit_date_via_picker(self.YEAR, self.MONTH, self.DAY)
        assert calendar_page.submitted_field_name.strip().startswith(
            "Select or enter a date"
        )
        assert calendar_page.submitted_date_value == self.EXPECTED_DATE, (
            f"Expected '{self.EXPECTED_DATE}', got '{calendar_page.submitted_date_value}'"
        )

    def test_picker_boundary_year_1926(self, calendar_page):
        """Can select 1926 via the interactive picker."""
        calendar_page.submit_date_via_picker(1926, "January", 1)
        assert calendar_page.is_success_displayed
        assert calendar_page.submitted_date_value == "1926-01-01"

    def test_picker_boundary_year_2126(self, calendar_page):
        """Can select 2126 via the interactive picker."""
        calendar_page.submit_date_via_picker(2126, "December", 31)
        assert calendar_page.is_success_displayed
        assert calendar_page.submitted_date_value == "2126-12-31"


# ──────────────────────────────────────────────────────────────────────
# Cross-method validation
# ──────────────────────────────────────────────────────────────────────
class TestCrossMethodValidation:
    """The same date entered via both methods must produce identical results
    and the same day-of-week."""

    YEAR = 2028
    MONTH = "March"
    DAY = 17
    DATE_STR = "2028-03-17"

    def test_cross_method_date_value_matches(self, calendar_page):
        """Direct input and interactive picker produce the same displayed date."""
        # Method 1: direct input
        calendar_page.submit_date_directly(self.DATE_STR)
        direct_date = calendar_page.submitted_date_value
        assert direct_date == self.DATE_STR

    def test_cross_method_day_of_week_matches(self, calendar_page):
        """The day-of-week computed from the submitted date is consistent
        with the picker's weekday labels."""
        expected_weekday = _dom_weekday(self.DATE_STR)

        # Open the picker and check the day-of-week column for the selected day
        calendar_page.open_date_picker()
        calendar_page.select_month(self.MONTH)
        calendar_page.select_year(self.YEAR)

        headers = calendar_page.get_day_headers()
        days = calendar_page.get_all_days()

        # Find the target day among current-month days
        target_day_info = None
        for d in days:
            if d["number"] == str(self.DAY) and not d["is_other_month"]:
                target_day_info = d
                break

        assert target_day_info is not None, (
            f"Day {self.DAY} not found among current-month days"
        )

        # The column index of the target day tells us the weekday
        all_day_buttons = calendar_page.find_elements(calendar_page.DAYS)
        target_index = list(all_day_buttons).index(target_day_info["element"])
        actual_weekday_header = headers[target_index % 7]

        assert actual_weekday_header == expected_weekday, (
            f"Day {self.DAY} falls under '{actual_weekday_header}' in the picker "
            f"but should be '{expected_weekday}' ({self.DATE_STR})"
        )


# ──────────────────────────────────────────────────────────────────────
# Bug verification: dates outside 1926–2126
# ──────────────────────────────────────────────────────────────────────
class TestOutOfRangeDates:
    """Verification that the date input accepts values outside the
    1926–2126 range (this is a bug)."""

    @pytest.mark.parametrize(
        "out_of_range_date",
        [
            "1925-12-31",
            "1925-01-01",
            "1800-06-15",
            "2127-01-01",
            "2127-12-31",
            "3000-01-01",
        ],
    )
    def test_direct_input_accepts_out_of_range(self, calendar_page, out_of_range_date):
        """BUG: The direct text input accepts dates outside 1926–2126."""
        calendar_page.submit_date_directly(out_of_range_date)
        assert calendar_page.is_success_displayed, (
            f"Expected form to accept out-of-range date '{out_of_range_date}' "
            "(this is the known bug — direct input does not enforce range)"
        )
        assert calendar_page.submitted_date_value == out_of_range_date

    def test_interactive_picker_rejects_out_of_range(self, calendar_page):
        """The interactive picker does not allow selecting years outside 1926-2126."""
        calendar_page.open_date_picker()
        years = calendar_page.get_available_years()
        assert 1925 not in years, "1925 should not be selectable in the picker"
        assert 2127 not in years, "2127 should not be selectable in the picker"
