from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage
import config


class IframesPage(BasePage):
    TOP_IFRAME = (By.ID, "iframe-1")
    BOTTOM_IFRAME = (By.ID, "iframe-2")

    @property
    def is_available(self) -> bool:
        """Both target iframes are present on the page."""
        return (
            self.is_element_available(self.TOP_IFRAME)
            and self.is_element_available(self.BOTTOM_IFRAME)
        )

    # --- Context managers ---

    def switch_to_top_iframe(self):
        """Switch context to the top iframe (Playwright documentation)."""
        iframe = self.find_element(self.TOP_IFRAME)
        self.driver.switch_to.frame(iframe)

    def switch_to_bottom_iframe(self):
        """Switch context to the bottom iframe (Selenium documentation)."""
        iframe = self.find_element(self.BOTTOM_IFRAME)
        self.driver.switch_to.frame(iframe)

    def switch_to_default(self):
        """Return context to the parent (top-level) page."""
        self.driver.switch_to.parent_frame()

    # --- Top iframe (Playwright.dev) ---

    def get_top_iframe_text(self) -> str:
        """Return body text from the top iframe."""
        self.switch_to_top_iframe()
        text = self.driver.find_element(By.TAG_NAME, "body").text
        self.switch_to_default()
        return text

    def top_iframe_contains_text(self, text: str, timeout: int | None = None) -> bool:
        """Wait until *text* appears inside the top iframe body."""
        self.switch_to_top_iframe()
        wait = WebDriverWait(self.driver, timeout or config.DEFAULT_TIMEOUT)
        try:
            wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), text))
            return True
        except TimeoutException:
            return False
        finally:
            self.switch_to_default()

    def get_top_iframe_title(self) -> str:
        """Return the <title> of the top iframe's embedded page."""
        self.switch_to_top_iframe()
        title = self.driver.execute_script("return document.title")
        self.switch_to_default()
        return title

    # --- Bottom iframe (Selenium.dev) ---

    def get_bottom_iframe_text(self) -> str:
        """Return body text from the bottom iframe."""
        self.switch_to_bottom_iframe()
        text = self.driver.find_element(By.TAG_NAME, "body").text
        self.switch_to_default()
        return text

    def bottom_iframe_contains_text(self, text: str, timeout: int | None = None) -> bool:
        """Wait until *text* appears inside the bottom iframe body."""
        self.switch_to_bottom_iframe()
        wait = WebDriverWait(self.driver, timeout or config.DEFAULT_TIMEOUT)
        try:
            wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), text))
            return True
        except TimeoutException:
            return False
        finally:
            self.switch_to_default()

    def get_bottom_iframe_title(self) -> str:
        """Return the <title> of the bottom iframe's embedded page."""
        self.switch_to_bottom_iframe()
        title = self.driver.execute_script("return document.title")
        self.switch_to_default()
        return title
