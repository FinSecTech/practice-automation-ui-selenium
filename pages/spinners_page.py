from selenium.webdriver.common.by import By
from pages.base_page import BasePage
import config


class SpinnersPage(BasePage):
    SPINNER = (By.CLASS_NAME, "spinner")
    SPINNER_HIDDEN = (By.CLASS_NAME, "spinner-hidden")

    @property
    def is_available(self) -> bool:
        """The spinner element is present on the page."""
        return self.is_element_available(self.SPINNER)

    def wait_for_spinner_hidden(self, timeout: int | None = None) -> bool:
        """Wait until the spinner-hidden class is present (spinner done).

        The exercise hint indicates the page adds a ``spinner-hidden``
        CSS class to the spinner element once background processing
        finishes, at which point the spinner is no longer visible.

        Returns True if the class appears within *timeout* seconds,
        False otherwise.
        """
        return self.is_element_available(
            self.SPINNER_HIDDEN, timeout or config.DEFAULT_TIMEOUT
        )

    def wait_for_spinner_to_hide(self, timeout: int | None = None) -> bool:
        """Wait until the spinner element is no longer displayed.

        Returns True if it becomes hidden within *timeout* seconds,
        False otherwise.
        """
        return self.wait_until_invisible(self.SPINNER, timeout or config.DEFAULT_TIMEOUT)

    def is_spinner_visible(self) -> bool:
        """Check whether the spinner is currently displayed."""
        return self.find_element(self.SPINNER).is_displayed()
