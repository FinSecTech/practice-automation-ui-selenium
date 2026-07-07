"""
Page object for the Accordions page
(https://practice-automation.com/accordions/).

The page contains a single native HTML5 ``<details><summary>`` accordion.
Clicking the summary expands the content, which contains the text
"This is an accordion item."
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
import config


class AccordionsPage(BasePage):
    # ── Locators ──────────────────────────────────────────────────────
    # The outer container wrapping the accordion
    ACCORDION_CONTAINER = (By.CSS_SELECTOR, "div.wp-block-coblocks-accordion")

    # The clickable summary (always visible)
    ACCORDION_SUMMARY = (By.CSS_SELECTOR, "summary.wp-block-coblocks-accordion-item__title")

    # The content panel (always in DOM but only displayed when expanded)
    ACCORDION_CONTENT = (By.CSS_SELECTOR, "div.wp-block-coblocks-accordion-item__content")

    # Expected text values
    SUMMARY_TEXT = "Click to see more"
    CONTENT_TEXT = "This is an accordion item."

    # ── Properties ────────────────────────────────────────────────────

    @property
    def is_available(self) -> bool:
        """The page is considered loaded when the accordion container is
        present on the page."""
        return self.is_element_available(self.ACCORDION_CONTAINER)

    # ── State helpers ─────────────────────────────────────────────────

    @property
    def summary_text(self) -> str:
        return self.find_element(self.ACCORDION_SUMMARY).text

    @property
    def content_text(self) -> str:
        """Return the visible content text, stripped of surrounding whitespace.

        Safari renders the native ``<details>`` content element with extra
        surrounding newlines that other browsers omit.  Stripping normalises
        the result across all browsers so assertions like
        ``page.content_text == page.CONTENT_TEXT`` work consistently.
        """
        return self.find_element(self.ACCORDION_CONTENT).text.strip()

    def is_content_visible(self) -> bool:
        """Return *True* if the content panel is currently visible.

        Uses a visibility check because the content div is always in the
        DOM (native ``<details>``) but hidden when the accordion is
        collapsed.
        """
        wait = WebDriverWait(self.driver, config.SHORT_TIMEOUT)
        try:
            wait.until(EC.visibility_of_element_located(self.ACCORDION_CONTENT))
            return True
        except TimeoutException:
            return False

    # ── Actions ───────────────────────────────────────────────────────

    def click_summary(self) -> None:
        """Click the accordion summary to toggle the content panel."""
        summary = self.find_clickable(self.ACCORDION_SUMMARY)
        summary.click()
