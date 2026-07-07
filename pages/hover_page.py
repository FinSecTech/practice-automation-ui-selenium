"""Page Object for the Hover page.

The page has an ``<h3 id="mouse_over">`` element with inline ``onmouseover``
and ``onmouseout`` JavaScript handlers:
- **Hover** — changes the element's text to *"You did it!"* and color to green.
- **Move away** — reverts to *"Mouse over me"* with black color.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


class HoverPage(BasePage):
    # ── Page elements ────────────────────────────────────────────────
    MOUSE_OVER_ELEMENT = (By.ID, "mouse_over")
    PAGE_HEADER = (By.TAG_NAME, "h1")

    # Expected text values
    DEFAULT_TEXT = "Mouse over me"
    HOVER_TEXT = "You did it!"

    # ── Availability ─────────────────────────────────────────────────
    @property
    def is_available(self) -> bool:
        return self.is_element_available(self.MOUSE_OVER_ELEMENT)

    def open_page(self) -> None:
        import config

        self.open(f"{config.BASE_URL}hover/")
        assert self.is_available, "Hover page did not load"

    # ── State helpers ────────────────────────────────────────────────
    @property
    def mouse_over_text(self) -> str:
        return self.find_element(self.MOUSE_OVER_ELEMENT).text

    @property
    def mouse_over_color(self) -> str:
        return self.find_element(self.MOUSE_OVER_ELEMENT).value_of_css_property("color")

    # ── Actions ──────────────────────────────────────────────────────
    def hover_over_element(self) -> None:
        """Hover over the element using ActionChains.

        Falls back to a synthetic mouseenter event via JS if the native
        WebDriver hover doesn't trigger the handler (common under CPU
        load in parallel xdist runs).
        """
        element = self.find_element(self.MOUSE_OVER_ELEMENT)
        try:
            ActionChains(self.driver).move_to_element(element).perform()
            # Give a brief tick for the JS handler to fire
            try:
                WebDriverWait(self.driver, timeout=1).until(
                    lambda d: self.mouse_over_text == self.HOVER_TEXT
                )
                return
            except TimeoutException:
                pass
        except Exception:
            pass

        # Fallback: fire the onmouseover handler directly via JS
        self.driver.execute_script("arguments[0].onmouseover();", element)
        try:
            WebDriverWait(self.driver, timeout=3).until(
                lambda d: self.mouse_over_text == self.HOVER_TEXT
            )
        except TimeoutException:
            pass

    def move_mouse_away(self) -> None:
        """Move the mouse cursor to the page header to trigger mouseout."""
        header = self.find_element(self.PAGE_HEADER)
        ActionChains(self.driver).move_to_element(header).perform()

    # ── Assertions ───────────────────────────────────────────────────
    def wait_for_text(self, expected_text: str, timeout: int | None = None) -> bool:
        """Wait until the element's text matches ``expected_text``.

        Returns ``True`` if the text matches within the timeout, ``False`` otherwise.
        """
        wait = WebDriverWait(self.driver, timeout or self.wait._timeout)
        try:
            wait.until(
                lambda d: self.find_element(self.MOUSE_OVER_ELEMENT).text == expected_text
            )
            return True
        except TimeoutException:
            return False

    def is_text_changed_to_hover(self) -> bool:
        return self.wait_for_text(self.HOVER_TEXT)

    def is_text_reverted(self) -> bool:
        return self.wait_for_text(self.DEFAULT_TEXT)
