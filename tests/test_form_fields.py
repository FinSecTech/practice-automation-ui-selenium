"""
Tests for the Form Fields page (https://practice-automation.com/form-fields/).

Verifies:
1. All form fields can be filled in
2. Checkboxes can be selected and radio buttons clicked
3. Drop-down menu selection works
4. The "Required" indicator disappears after typing into the name field (EXPECTED FAILURE)
5. No special characters (#, &, etc.) in visible page text (EXPECTED FAILURE)
6. Form is NOT submitted when the "Required" field is empty (browser validation)
7. Form IS submitted when the required field is filled → alert "Message received!"
"""

import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import config


# ──────────────────────────────────────────────────────────────────────
# Tests that are expected to fail (known issues on the practice site)
# ──────────────────────────────────────────────────────────────────────


def test_required_indicator_disappears_after_typing(form_fields_page):
    """
    The red ' * Required' text should disappear as soon as the user starts
    typing into the Name field.  On this site the indicator is a static
    <p> element that never hides — the test therefore fails as planned.
    """
    # Confirm the indicator is visible before typing
    assert form_fields_page.is_required_indicator_visible()
    assert "Required" in form_fields_page.get_required_indicator_text()

    # Type a single character into the name field
    form_fields_page.fill_name("T")

    # The indicator SHOULD have disappeared — in reality it stays visible.
    # This assertion will fail (expected).
    assert not form_fields_page.is_required_indicator_visible(), (
        "FAILED AS PLANNED: The Required indicator is static and does not "
        "disappear after typing."
    )


def test_no_special_chars_in_page_text(form_fields_page):
    """
    Visible page text must not contain raw '#' or '&' characters that
    indicate HTML-entity rendering bugs.  The radio button label
    '#FFC0CB' contains a literal '#' — so this test fails as planned.
    """
    body_text = form_fields_page.get_page_body_text()

    # Check for characters that signal broken HTML entities
    problematic = re.findall(r'[#&]', body_text)
    assert len(problematic) == 0, (
        f"FAILED AS PLANNED: Found {len(problematic)} problematic character(s) "
        f"({', '.join(repr(c) for c in problematic)}) in visible page text. "
        "This likely comes from the '#FFC0CB' radio label or similar content."
    )


# ──────────────────────────────────────────────────────────────────────
# Tests that are expected to PASS
# ──────────────────────────────────────────────────────────────────────


def test_form_fields_can_be_filled(form_fields_page):
    """All form fields accept input values."""
    form_fields_page.fill_name("John Doe")
    assert form_fields_page.get_name_value() == "John Doe"

    form_fields_page.fill_password("s3cret")
    form_fields_page.fill_email("john@example.com")
    form_fields_page.fill_message("Hello, this is a test message.")


def test_checkboxes_can_be_selected(form_fields_page):
    """All drink checkboxes can be checked."""
    drink_locators = [
        (form_fields_page.DRINK_WATER, "Water"),
        (form_fields_page.DRINK_MILK, "Milk"),
        (form_fields_page.DRINK_COFFEE, "Coffee"),
        (form_fields_page.DRINK_WINE, "Wine"),
        (form_fields_page.DRINK_CTRL_ALT_DELIGHT, "Ctrl-Alt-Delight"),
    ]
    for locator, label in drink_locators:
        cb = form_fields_page.find_clickable(locator)
        assert not cb.is_selected(), f"'{label}' should not be selected initially"
        form_fields_page.select_drink(locator)
        assert cb.is_selected(), f"'{label}' should be selected after click"
        # Uncheck for the next iteration to keep state clean
        cb.click()

    # Verify multiple selections work
    form_fields_page.select_drink(form_fields_page.DRINK_COFFEE)
    form_fields_page.select_drink(form_fields_page.DRINK_WINE)
    assert form_fields_page.driver.find_element(*form_fields_page.DRINK_COFFEE).is_selected()
    assert form_fields_page.driver.find_element(*form_fields_page.DRINK_WINE).is_selected()


def test_radio_buttons_can_be_clicked(form_fields_page):
    """Each color radio button can be selected (only one at a time)."""
    color_locators = [
        (form_fields_page.COLOR_RED, "Red"),
        (form_fields_page.COLOR_BLUE, "Blue"),
        (form_fields_page.COLOR_YELLOW, "Yellow"),
        (form_fields_page.COLOR_GREEN, "Green"),
        (form_fields_page.COLOR_PINK, "Pink"),
    ]
    for locator, label in color_locators:
        radio = form_fields_page.find_clickable(locator)
        assert not radio.is_selected(), f"'{label}' should not be selected initially"
        form_fields_page.select_color(locator)
        assert radio.is_selected(), f"'{label}' should be selected after click"


def test_dropdown_selection(form_fields_page):
    """A value can be selected from the Automation drop-down."""
    select_el = Select(form_fields_page.find_element(form_fields_page.AUTOMATION_SELECT))

    # Default should be the empty option
    assert select_el.first_selected_option.get_attribute("value") == "default"

    # Select "Yes"
    form_fields_page.select_automation_option("yes")
    assert select_el.first_selected_option.get_attribute("value") == "yes"

    # Select "No"
    form_fields_page.select_automation_option("no")
    assert select_el.first_selected_option.get_attribute("value") == "no"

    # Select "Undecided"
    form_fields_page.select_automation_option("undecided")
    assert select_el.first_selected_option.get_attribute("value") == "undecided"


def test_submit_fails_when_required_field_empty(form_fields_page):
    """
    Clicking Submit with an empty required Name field should NOT submit
    the form.  The browser's HTML5 validation focuses the empty field and
    the page stays at the same URL.
    """
    current_url = form_fields_page.driver.current_url

    # Fill in everything except the Name field
    form_fields_page.fill_password("s3cret")
    form_fields_page.select_drink(form_fields_page.DRINK_COFFEE)
    form_fields_page.select_color(form_fields_page.COLOR_BLUE)
    form_fields_page.select_automation_option("yes")
    form_fields_page.fill_email("test@example.com")
    form_fields_page.fill_message("Optional message.")

    form_fields_page.click_submit()

    # Wait for HTML5 validation to focus the required field (browser-native)
    form_fields_page.wait.until(
        lambda d: d.switch_to.active_element.get_attribute("id") == "name-input"
    )

    # The URL should not have changed
    assert form_fields_page.driver.current_url == current_url, (
        "Form was submitted despite the required Name field being empty"
    )


def test_successful_form_submission(form_fields_page):
    """
    Filling in the required Name field and clicking Submit fires the
    'Message received!' alert.
    """
    # Fill the required Name field
    form_fields_page.fill_name("Jane Doe")

    # Fill other fields too (for completeness)
    form_fields_page.fill_password("p@ss")
    form_fields_page.select_drink(form_fields_page.DRINK_WATER)
    form_fields_page.select_drink(form_fields_page.DRINK_MILK)
    form_fields_page.select_color(form_fields_page.COLOR_GREEN)
    form_fields_page.select_automation_option("undecided")
    form_fields_page.fill_email("jane@example.com")
    form_fields_page.fill_message("Test submission.")

    form_fields_page.click_submit()

    # Wait for the alert to appear
    WebDriverWait(form_fields_page.driver, config.DEFAULT_TIMEOUT).until(EC.alert_is_present())

    # Verify and accept the alert
    alert = form_fields_page.driver.switch_to.alert
    try:
        assert alert.text == "Message received!", (
            f"Unexpected alert text: '{alert.text}'"
        )
        alert.accept()
    except AssertionError:
        alert.accept()
        raise
