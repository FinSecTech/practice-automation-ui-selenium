"""
Tests for the Popups page (https://practice-automation.com/popups/).

Verifies:
1. Alert popup: button click shows an alert, text is "Hi there, pal!"
2. Confirm popup: OK → shows "OK it is!", Cancel → shows "Cancel it is!"
3. Prompt popup: entering text → "...", Cancel/dismiss → "Fine, be that way...",
   empty accept → same as cancel "Fine, be that way..."
4. Tooltip: click to show, click again to hide
"""


# ──────────────────────────────────────────────────────────────────────
# JS Alert popup
# ──────────────────────────────────────────────────────────────────────


def test_alert_popup_text(popups_page):
    """Clicking Alert Popup shows 'Hi there, pal!'."""
    text = popups_page.get_alert_text_and_accept()
    assert text == "Hi there, pal!"


# ──────────────────────────────────────────────────────────────────────
# Confirm popup
# ──────────────────────────────────────────────────────────────────────


def test_confirm_accept(popups_page):
    """Accepting the confirm dialog shows 'OK it is!'."""
    result = popups_page.accept_confirm()
    assert result == "OK it is!"


def test_confirm_dismiss(popups_page):
    """Dismissing the confirm dialog shows 'Cancel it is!'."""
    result = popups_page.dismiss_confirm()
    assert result == "Cancel it is!"


# ──────────────────────────────────────────────────────────────────────
# Prompt popup
# ──────────────────────────────────────────────────────────────────────


def test_prompt_with_text(popups_page):
    """Entering text into the prompt shows 'Nice to meet you, <text>!'."""
    result = popups_page.fill_and_accept_prompt("Alice")
    assert result == "Nice to meet you, Alice!"


def test_prompt_dismiss(popups_page):
    """Dismissing (Cancel) the prompt shows 'Fine, be that way...'."""
    result = popups_page.dismiss_prompt()
    assert result == "Fine, be that way..."


def test_prompt_accept_empty(popups_page):
    """Accepting the prompt with no text shows 'Fine, be that way...'.

    The JS code treats an empty string the same as a null (Cancel):
    ``if (person == null || person == "")`` → same fallback message.
    """
    result = popups_page.accept_empty_prompt()
    assert result == "Fine, be that way..."


# ──────────────────────────────────────────────────────────────────────
# Tooltip
# ──────────────────────────────────────────────────────────────────────


def test_tooltip_show_hide(popups_page):
    """Clicking the tooltip trigger toggles the tooltip visibility."""
    assert not popups_page.is_tooltip_visible(), (
        "Tooltip should be hidden initially"
    )

    popups_page.show_tooltip()
    assert popups_page.is_tooltip_visible(), (
        "Tooltip should be visible after first click"
    )

    popups_page.show_tooltip()
    assert not popups_page.is_tooltip_visible(), (
        "Tooltip should be hidden after second click"
    )


# ──────────────────────────────────────────────────────────────────────
# Popup Maker modals (expected failures — no visible triggers on page)
# ──────────────────────────────────────────────────────────────────────


def test_simple_modal_visible_on_page_load(popups_page):
    """The Simple Modal overlay should be accessible (visible) on page load.

    The modal is defined in the DOM via Popup Maker but has NO trigger
    button wired up in the page content.  It remains hidden.
    """
    assert popups_page.is_simple_modal_accessible(), (
        "FAILED AS PLANNED: Simple Modal is defined in the DOM but has no "
        "trigger element — the overlay stays hidden (display: none)."
    )


def test_form_modal_visible_on_page_load(popups_page):
    """The Form Modal overlay should be accessible (visible) on page load.

    Same root cause as the Simple Modal — the Popup Maker trigger was
    never attached to any visible element on the page.
    """
    assert popups_page.is_form_modal_accessible(), (
        "FAILED AS PLANNED: Form Modal is defined in the DOM but has no "
        "trigger element — the overlay stays hidden (display: none)."
    )


def test_form_modal_fields_interactable(popups_page):
    """The form inside the Form Modal should be fillable and submit-able.

    Since the modal overlay is hidden, Selenium cannot interact with
    the form fields inside it.
    """
    name_input = popups_page.find_element(popups_page.FORM_MODAL_NAME)
    assert name_input.is_displayed(), (
        "FAILED AS PLANNED: Form Modal is hidden — fields are not displayed."
    )
