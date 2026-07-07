from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.remote.webelement import WebElement
from typing import Tuple, Union
import config


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.DEFAULT_TIMEOUT)
        self.long_wait = WebDriverWait(driver, config.LONG_TIMEOUT)

    def open(self, url: str):
        self.driver.get(url)

    def find_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_for_text_present(self, locator, text: str):
        return self.long_wait.until(
            EC.text_to_be_present_in_element(locator, text)
        )

    def is_element_available(self, locator, timeout: int | None = None) -> bool:
        """Check if an element is present on the page within the given timeout."""
        wait = WebDriverWait(self.driver, timeout or config.DEFAULT_TIMEOUT)
        try:
            wait.until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def wait_until_invisible(self, locator, timeout: int | None = None) -> bool:
        """Wait until an element is not displayed (hidden or removed).

        Returns True if the element becomes invisible within the timeout,
        False otherwise.
        """
        wait = WebDriverWait(self.driver, timeout or config.DEFAULT_TIMEOUT)
        try:
            wait.until(EC.invisibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    # ── Robust clicking ──────────────────────────────────────────

    def _resolve_element(self, locator_or_element: Union[Tuple, WebElement]) -> WebElement:
        """Return a WebElement from either a locator tuple or a WebElement."""
        if isinstance(locator_or_element, Tuple):
            return self.find_clickable(locator_or_element)
        return locator_or_element

    def _js_click(self, locator_or_element: Union[Tuple, WebElement]) -> None:
        """Scroll an element into view and click via JavaScript.

        This bypasses overlay interception (e.g. Popup Maker modals,
        sticky headers, ad overlays, cookie banners) that can block
        native Selenium clicks, particularly in Chromium-based browsers
        (Edge, Opera) and with Popup Maker's event system (Firefox).

        Accepts either a locator (tuple) or a WebElement.
        """
        el = self._resolve_element(locator_or_element)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)

    def _safe_click(self, locator_or_element: Union[Tuple, WebElement]) -> None:
        """Click an element, falling back to JS click if native click
        is intercepted (e.g. by an overlay or fixed-position element).

        Strategy:
          1. Wait for the element to be clickable (visible + enabled).
          2. Scroll it into view (centered).
          3. Try Selenium's native click.
          4. If ElementClickInterceptedException → retry via JS click.

        Accepts either a locator (tuple) or a WebElement.
        """
        el = self._resolve_element(locator_or_element)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        try:
            el.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", el)
