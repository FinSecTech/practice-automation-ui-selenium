"""Tests for the Iframes page (https://practice-automation.com/iframes/).

The page embeds two external iframes:
  - Top iframe (#iframe-1)  → Playwright documentation (playwright.dev)
  - Bottom iframe (#iframe-2) → Selenium documentation (selenium.dev)

Tests verify that Selenium can switch context into each iframe, read
content from them, and confirm expected text.
"""

from pages.iframes_page import IframesPage


IFRAME_TIMEOUT = 15


class TestIframes:
    """Test suite for the Iframes page."""

    def test_iframes_page_loads(self, iframes_page: IframesPage):
        """Both iframes are present on the page."""
        assert iframes_page.is_available

    def test_top_iframe_contains_playwright(self, iframes_page: IframesPage):
        """The top iframe loads Playwright documentation."""
        assert iframes_page.top_iframe_contains_text(
            "Playwright", timeout=IFRAME_TIMEOUT
        ), "Top iframe should contain 'Playwright' text"

    def test_bottom_iframe_contains_selenium(self, iframes_page: IframesPage):
        """The bottom iframe loads Selenium documentation."""
        assert iframes_page.bottom_iframe_contains_text(
            "Selenium", timeout=IFRAME_TIMEOUT
        ), "Bottom iframe should contain 'Selenium' text"

    def test_top_iframe_title(self, iframes_page: IframesPage):
        """The top iframe has a Playwright page title."""
        title = iframes_page.get_top_iframe_title()
        assert "Playwright" in title, (
            f"Expected top iframe title to contain 'Playwright', got {title!r}"
        )

    def test_bottom_iframe_title(self, iframes_page: IframesPage):
        """The bottom iframe has 'Selenium' as its page title."""
        title = iframes_page.get_bottom_iframe_title()
        assert title == "Selenium", (
            f"Expected bottom iframe title to be 'Selenium', got {title!r}"
        )

    def test_top_iframe_returns_body_text(self, iframes_page: IframesPage):
        """get_top_iframe_text() returns non-empty text."""
        text = iframes_page.get_top_iframe_text()
        assert len(text) > 0, "Top iframe body text should not be empty"

    def test_bottom_iframe_returns_body_text(self, iframes_page: IframesPage):
        """get_bottom_iframe_text() returns non-empty text."""
        text = iframes_page.get_bottom_iframe_text()
        assert len(text) > 0, "Bottom iframe body text should not be empty"
