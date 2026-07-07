"""
Tests for the Accordions page
(https://practice-automation.com/accordions/).

Verifies the behavior of the single native HTML5 ``<details><summary>``
accordion:
- Initial state: summary text is shown, content is hidden
- After clicking the summary: content becomes visible with expected text
"""

from pages.accordions_page import AccordionsPage


class TestAccordions:
    """Test suite for the Accordions page."""

    def test_initial_state(self, accordions_page: AccordionsPage):
        """Before clicking, the summary shows the expected text and the
        content panel is hidden."""
        page = accordions_page

        assert page.summary_text == page.SUMMARY_TEXT, (
            f"Expected summary text '{page.SUMMARY_TEXT}', "
            f"got '{page.summary_text}'"
        )
        assert not page.is_content_visible(), (
            "Content should be hidden when accordion is collapsed"
        )

    def test_click_expands_accordion(self, accordions_page: AccordionsPage):
        """Clicking the summary expands the accordion and reveals the
        content with the expected text."""
        page = accordions_page

        page.click_summary()

        assert page.is_content_visible(), (
            "Content should be visible after clicking the summary"
        )
        assert page.content_text == page.CONTENT_TEXT, (
            f"Expected content text '{page.CONTENT_TEXT}', "
            f"got '{page.content_text}'"
        )

    def test_click_twice_collapses_accordion(self, accordions_page: AccordionsPage):
        """Clicking the summary a second time collapses the accordion
        and hides the content panel."""
        page = accordions_page

        page.click_summary()
        assert page.is_content_visible(), "Content should be visible after first click"

        page.click_summary()
        assert not page.is_content_visible(), (
            "Content should be hidden after clicking the summary again"
        )
