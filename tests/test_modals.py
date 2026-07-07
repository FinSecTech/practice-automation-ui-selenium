"""
Tests for the Modals page (https://practice-automation.com/modals/).

Verifies:
1. Both modals are hidden on initial page load
2. Simple Modal: open → verify title + content → close
3. Form Modal: open → verify title + close
4. Form Modal — email validation: invalid email shows browser validation message
5. Form Modal — fill form + submit → success message
"""


# ──────────────────────────────────────────────────────────────────────
# Initial state
# ──────────────────────────────────────────────────────────────────────


def test_modals_hidden_on_page_load(modals_page):
    """Both modals should be hidden when the page first loads."""
    assert not modals_page.is_simple_modal_visible(), (
        "Simple Modal should be hidden on page load"
    )
    assert not modals_page.is_form_modal_visible(), (
        "Form Modal should be hidden on page load"
    )


# ──────────────────────────────────────────────────────────────────────
# Simple Modal
# ──────────────────────────────────────────────────────────────────────


def test_simple_modal_open_and_close(modals_page):
    """Opening the Simple Modal shows its title and content; close hides it."""
    modals_page.open_simple_modal()

    assert modals_page.is_simple_modal_visible(), (
        "Simple Modal should be visible after clicking trigger"
    )
    assert modals_page.get_simple_modal_title() == "Simple Modal", (
        "Simple Modal title should match"
    )

    content = modals_page.get_simple_modal_content()
    assert "simple modal" in content.lower(), (
        f"Simple Modal content should contain greeting, got: {content}"
    )

    modals_page.close_simple_modal()

    assert modals_page.wait_for_simple_modal_closed(), (
        "Simple Modal should be hidden after close"
    )


# ──────────────────────────────────────────────────────────────────────
# Form Modal — basic open/close
# ──────────────────────────────────────────────────────────────────────


def test_form_modal_open_and_title(modals_page):
    """Opening the Form Modal shows its title."""
    modals_page.open_form_modal()

    assert modals_page.is_form_modal_visible(), (
        "Form Modal should be visible after clicking trigger"
    )
    assert modals_page.get_form_modal_title() == "Modal Containing A Form", (
        "Form Modal title should match"
    )

    modals_page.close_form_modal()
    assert modals_page.wait_for_form_modal_closed(), (
        "Form Modal should be hidden after close"
    )


# ──────────────────────────────────────────────────────────────────────
# Form Modal — email validation (negative test)
# ──────────────────────────────────────────────────────────────────────


def test_form_modal_email_invalid_shows_validation_message(modals_page):
    """Entering an invalid email and moving to another field triggers the
    browser's native HTML5 email validation message.
    """
    modals_page.open_form_modal()
    assert modals_page.is_form_modal_visible(), (
        "Form Modal should be visible for validation test"
    )

    # Intentionally enter text that is not a valid email address
    modals_page.fill_form_email("not-an-email-address")

    # Click another field to trigger the browser's HTML5 validation
    modals_page.click_form_modal_message()

    # The browser should report a validation error
    msg = modals_page.get_email_validation_message()
    assert msg is not None, (
        "Email field should show a validation message for invalid input"
    )
    # Cross-browser: Firefox says "Please enter an email address.",
    # Chrome says "Please include an '@' in the email address." etc.
    assert "email" in msg.lower(), (
        f"Validation message should mention 'email', got: {msg}"
    )

    modals_page.close_form_modal()
    assert modals_page.wait_for_form_modal_closed(), (
        "Form Modal should close after validation test"
    )


# ──────────────────────────────────────────────────────────────────────
# Form Modal — fill and submit
# ──────────────────────────────────────────────────────────────────────


def test_form_modal_fill_and_submit(modals_page):
    """Filling and submitting the form inside the Form Modal shows success."""
    modals_page.open_form_modal()
    assert modals_page.is_form_modal_visible(), (
        "Form Modal should be visible for form interaction"
    )

    modals_page.fill_form_name("Test User")
    modals_page.fill_form_email("test@example.com")
    modals_page.fill_form_message("This is a test message.")

    modals_page.submit_form()

    assert modals_page.is_form_submission_successful(), (
        "Thank-you message should appear after form submission"
    )
