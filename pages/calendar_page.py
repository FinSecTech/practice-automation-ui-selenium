"""Page Object for the Calendars page (https://practice-automation.com/calendars/).

The page uses Jetpack's interactive date picker (date-picker.js) with the
following structure:

- Date input: <input> with class ``jp-contact-form-date`` and
  ``data-format="yy-mm-dd"``.
- Submit button: <button class="pushbutton-wide">.
- Success header: <h4> containing "Thank you for your response."
- Submitted field label: <div class="field-name"> with "Select or enter a date:".
- Submitted field value: <div class="field-value"> with the date string.

Date picker DOM (shown after clicking the input):
  div.dp-below.dp-is-below
    div.dp
      div.dp-cal
        header.dp-cal-header
          button.dp-cal-month    – opens month overlay
          button.dp-cal-year     – opens year overlay
          button.dp-prev         – previous month
          button.dp-next         – next month
        div.dp-days
          span.dp-col-header ×7  – Mo Tu We Th Fr Sa Su
          button.dp-day ×42      – day cells (dp-edge-day for adjacent months)

Month overlay: div.dp-months > button.dp-month (January … December)
Year overlay:  button.dp-year from 1926 up to 2126 (201 buttons)
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.base_page import BasePage


class CalendarPage(BasePage):
    # ── Page elements ────────────────────────────────────────────────
    DATE_INPUT = (By.CSS_SELECTOR, "input.date.jp-contact-form-date")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button.pushbutton-wide")

    # Success / submission display
    SUCCESS_HEADER = (
        By.CSS_SELECTOR,
        "h4[id^='contact-form-success-header']",
    )
    FIELD_NAME = (By.CSS_SELECTOR, "div.field-name")
    FIELD_VALUE = (By.CSS_SELECTOR, "div.field-value")

    # ── Date picker (appears on click) ───────────────────────────────
    DATE_PICKER = (By.CSS_SELECTOR, "div.dp-below")

    MONTH_BUTTON = (By.CSS_SELECTOR, "button.dp-cal-month")
    YEAR_BUTTON = (By.CSS_SELECTOR, "button.dp-cal-year")
    PREV_MONTH = (By.CSS_SELECTOR, "button.dp-prev")
    NEXT_MONTH = (By.CSS_SELECTOR, "button.dp-next")

    # Month overlay
    MONTH_OVERLAY = (By.CSS_SELECTOR, "div.dp-months")
    MONTH_ITEMS = (By.CSS_SELECTOR, "button.dp-month")

    # Year overlay
    YEAR_ITEMS = (By.CSS_SELECTOR, "button.dp-year")

    # Day headers (Mo Tu We Th Fr Sa Su)
    DAY_HEADERS = (By.CSS_SELECTOR, "span.dp-col-header")

    # Day cells
    DAYS = (By.CSS_SELECTOR, "button.dp-day")
    OTHER_MONTH_DAYS = (By.CSS_SELECTOR, "button.dp-edge-day")

    # ── Availability ─────────────────────────────────────────────────
    @property
    def is_available(self) -> bool:
        return self.is_element_available(self.DATE_INPUT)

    def open_page(self) -> None:
        import config

        self.open(f"{config.BASE_URL}calendars/")
        assert self.is_available, "Calendar page did not load"

    # ── Direct input ─────────────────────────────────────────────────
    def enter_date_directly(self, date_str: str) -> None:
        """Clear the input and type ``date_str`` in YYYY-MM-DD format."""
        el = self.find_element(self.DATE_INPUT)
        el.clear()
        el.send_keys(date_str)

    def get_input_value(self) -> str:
        return self.find_element(self.DATE_INPUT).get_attribute("value") or ""

    # ── Submit ───────────────────────────────────────────────────────
    def click_submit(self) -> None:
        self.find_clickable(self.SUBMIT_BUTTON).click()

    # ── Success message ──────────────────────────────────────────────
    @property
    def success_header_text(self) -> str:
        return self.find_element(self.SUCCESS_HEADER).text

    @property
    def is_success_displayed(self) -> bool:
        """Wait for the success header to become visible."""
        try:
            self.long_wait.until(EC.visibility_of_element_located(self.SUCCESS_HEADER))
            return True
        except TimeoutException:
            return False

    @property
    def submitted_date_value(self) -> str:
        """Return the date string shown in the success field-value div."""
        return self.find_element(self.FIELD_VALUE).text

    @property
    def submitted_field_name(self) -> str:
        return self.find_element(self.FIELD_NAME).text

    # ── Date picker visibility ───────────────────────────────────────
    def open_date_picker(self) -> None:
        """Click the date input to open the interactive date picker."""
        inp = self.find_clickable(self.DATE_INPUT)
        inp.click()
        self.wait.until(EC.visibility_of_element_located(self.DATE_PICKER))

    def is_date_picker_open(self) -> bool:
        return self.is_element_available(self.DATE_PICKER, timeout=3)

    def close_date_picker(self) -> None:
        """Press Escape to close the date picker if it's open."""
        try:
            dp = self.find_element(self.DATE_PICKER)
            dp.send_keys(Keys.ESCAPE)
        except (TimeoutException, NoSuchElementException):
            pass

    # ── Month navigation ─────────────────────────────────────────────
    def get_current_month_display(self) -> str:
        """Return the displayed month name."""
        return self.find_element(self.MONTH_BUTTON).text

    def get_current_year_display(self) -> str:
        """Return the displayed year string."""
        return self.find_element(self.YEAR_BUTTON).text

    def click_prev_month(self) -> None:
        self.find_clickable(self.PREV_MONTH).click()

    def click_next_month(self) -> None:
        self.find_clickable(self.NEXT_MONTH).click()

    def select_month(self, month_name: str) -> None:
        """Open the month overlay and click the given month name.

        ``month_name`` must be the full English name, e.g. "January".
        """
        self.find_clickable(self.MONTH_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located(self.MONTH_OVERLAY))

        months = self.find_elements(self.MONTH_ITEMS)
        for m in months:
            if m.text.strip() == month_name:
                m.click()
                return
        raise ValueError(f"Month '{month_name}' not found in the picker")

    def get_available_months(self) -> list[str]:
        """Return all 12 month names from the month overlay."""
        self.find_clickable(self.MONTH_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located(self.MONTH_OVERLAY))
        months = self.find_elements(self.MONTH_ITEMS)
        names = [m.text.strip() for m in months]
        # Close the overlay by clicking the page body
        self.driver.find_element(By.TAG_NAME, "h1").click()
        return names

    # ── Year selection ───────────────────────────────────────────────
    def select_year(self, year: int) -> None:
        """Open the year overlay and click the given year button."""
        self.find_clickable(self.YEAR_BUTTON).click()
        # Wait until the year overlay appears – it replaces the month/year
        # header content with a scrollable year grid.
        self.wait.until(
            EC.presence_of_element_located(self.YEAR_ITEMS)
        )

        years = self.find_elements(self.YEAR_ITEMS)
        for y in years:
            if y.text.strip() == str(year):
                y.click()
                return
        raise ValueError(f"Year {year} not found in the picker")

    def get_available_years(self) -> list[int]:
        """Return the list of selectable years from the picker."""
        self.find_clickable(self.YEAR_BUTTON).click()
        self.wait.until(
            EC.presence_of_element_located(self.YEAR_ITEMS)
        )
        years = self.find_elements(self.YEAR_ITEMS)
        values = [int(y.text.strip()) for y in years]
        # Close overlay by clicking the page body
        self.driver.find_element(By.TAG_NAME, "h1").click()
        return values

    # ── Day selection ────────────────────────────────────────────────
    def get_day_headers(self) -> list[str]:
        """Return the list of weekday abbreviations shown at the top."""
        headers = self.find_elements(self.DAY_HEADERS)
        return [h.text.strip() for h in headers]

    def get_all_days(self) -> list[dict]:
        """Return all visible day buttons with their attributes.

        Each dict: {"number": str, "is_other_month": bool, "element": WebElement}
        """
        days = self.find_elements(self.DAYS)
        result = []
        for d in days:
            classes = d.get_attribute("class") or ""
            result.append(
                {
                    "number": d.text.strip(),
                    "is_other_month": "dp-edge-day" in classes,
                    "element": d,
                }
            )
        return result

    def select_day(self, day_number: int) -> None:
        """Click the day button with the given number (current month only).

        Raises ValueError if the day isn't found among current-month days.
        """
        days = self.find_elements(self.DAYS)
        for d in days:
            if d.text.strip() == str(day_number):
                classes = d.get_attribute("class") or ""
                if "dp-edge-day" not in classes:
                    d.click()
                    return
        raise ValueError(
            f"Day {day_number} not found among current-month days in the picker"
        )

    # ── High-level interaction ───────────────────────────────────────
    def select_date_via_picker(self, year: int, month_name: str, day: int) -> None:
        """Use the interactive date picker to select a date.

        1. Opens the picker.
        2. Selects the month (via the month overlay).
        3. Selects the year (via the year overlay).
        4. Clicks the day.
        The picker closes automatically after a day is selected.
        """
        if not self.is_date_picker_open():
            self.open_date_picker()

        self.select_month(month_name)
        self.select_year(year)
        self.select_day(day)

    # ── Helpers ──────────────────────────────────────────────────────
    def find_elements(self, locator):
        """Shortcut to avoid writing ``self.driver.find_elements`` everywhere."""
        return self.driver.find_elements(*locator)

    def submit_date_directly(self, date_str: str) -> None:
        """Convenience: enter a date via direct input and submit the form."""
        self.enter_date_directly(date_str)
        self.click_submit()

    def submit_date_via_picker(self, year: int, month_name: str, day: int) -> None:
        """Convenience: select a date via the interactive picker and submit."""
        self.select_date_via_picker(year, month_name, day)
        self.click_submit()
