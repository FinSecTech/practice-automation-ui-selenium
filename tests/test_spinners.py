"""Tests for the Spinners page (https://practice-automation.com/spinners/).

Verifies that the spinner on page load eventually becomes hidden, using
both the invisibility check and the ``spinner-hidden`` CSS class
approach recommended in the exercise hint.
"""

import pytest
from pages.spinners_page import SpinnersPage


SPINNER_TIMEOUT = 15


class TestSpinners:
    """Test suite for the Spinners page."""

    def test_spinners_page_loads(self, spinners_page: SpinnersPage):
        """The Spinners page loads and the spinner element is present."""
        assert spinners_page.is_available

    def test_spinner_is_visible_initially(self, spinners_page: SpinnersPage):
        """The spinner is displayed on page load before it disappears."""
        assert spinners_page.is_spinner_visible(), (
            "Expected spinner to be visible on page load"
        )

    def test_spinner_becomes_hidden_via_class(self, spinners_page: SpinnersPage):
        """Spinner gets the ``spinner-hidden`` class when background
        processing finishes.

        This uses the exact approach from the exercise hint: wait for
        an element with class ``spinner-hidden`` to appear, which
        indicates the spinner is no longer spinning.
        """
        hidden = spinners_page.wait_for_spinner_hidden(timeout=SPINNER_TIMEOUT)
        assert hidden, (
            f"Spinner did not acquire the 'spinner-hidden' class within "
            f"{SPINNER_TIMEOUT}s"
        )

    def test_spinner_becomes_invisible(self, spinners_page: SpinnersPage):
        """Spinner eventually becomes invisible (alternate check)."""
        hidden = spinners_page.wait_for_spinner_to_hide(timeout=SPINNER_TIMEOUT)
        assert hidden, (
            f"Spinner did not become invisible within {SPINNER_TIMEOUT}s"
        )
