"""Tests for the Click Events page (https://practice-automation.com/click-events/).

Verifies that clicking each animal button displays the expected text
in the demo element.
"""

import pytest
from pages.click_events_page import ClickEventsPage


class TestClickEvents:
    """Test suite for the Click Events page."""

    # Each animal button and the expected text that appears on click
    ANIMALS = [
        ("cat", "Meow!"),
        ("dog", "Woof!"),
        ("pig", "Oink!"),
        ("cow", "Moo!"),
    ]

    def test_click_events_page_loads(self, click_events_page: ClickEventsPage):
        """The Click Events page loads and the demo element is present."""
        assert click_events_page.is_available

    def test_demo_text_empty_initially(self, click_events_page: ClickEventsPage):
        """The demo text element is empty before any button is clicked."""
        text = click_events_page.demo_text
        assert text == "", (
            f"Expected empty demo text before clicking, got: {text!r}"
        )

    @pytest.mark.parametrize("animal,expected_text", ANIMALS)
    def test_button_click_shows_text(
        self, click_events_page: ClickEventsPage, animal: str, expected_text: str
    ):
        """Clicking an animal button displays the corresponding text."""
        text = click_events_page.click_animal(animal)
        assert text == expected_text, (
            f"Expected {expected_text!r} after clicking {animal}, got {text!r}"
        )

    def test_click_replaces_previous_text(self, click_events_page: ClickEventsPage):
        """Clicking a new button replaces the text from the previous click."""
        assert click_events_page.click_animal("cat") == "Meow!"
        assert click_events_page.click_animal("dog") == "Woof!"
        assert click_events_page.click_animal("pig") == "Oink!"
        assert click_events_page.click_animal("cow") == "Moo!"
