from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class ModalsPage(BasePage):
    # Trigger buttons
    SIMPLE_MODAL_TRIGGER = (By.ID, "simpleModal")
    FORM_MODAL_TRIGGER = (By.ID, "formModal")

    # Simple Modal overlay
    SIMPLE_MODAL_OVERLAY = (By.ID, "pum-1318")
    SIMPLE_MODAL_TITLE = (By.ID, "pum_popup_title_1318")
    SIMPLE_MODAL_CONTENT = (
        By.XPATH, "//div[@id='pum-1318']//div[@class='pum-content popmake-content']"
    )
    SIMPLE_MODAL_CLOSE = (
        By.XPATH, "//div[@id='pum-1318']//button[contains(@class, 'pum-close')]"
    )

    # Form Modal overlay
    FORM_MODAL_OVERLAY = (By.ID, "pum-674")
    FORM_MODAL_TITLE = (By.ID, "pum_popup_title_674")
    FORM_MODAL_CLOSE = (
        By.XPATH, "//div[@id='pum-674']//button[contains(@class, 'pum-close')]"
    )
    FORM_MODAL_FORM = (
        By.XPATH, "//div[@id='pum-674']//form"
    )
    FORM_MODAL_NAME = (
        By.XPATH, "//div[@id='pum-674']//input[@type='text']"
    )
    FORM_MODAL_EMAIL = (
        By.XPATH, "//div[@id='pum-674']//input[@type='email']"
    )
    FORM_MODAL_MESSAGE = (
        By.XPATH, "//div[@id='pum-674']//textarea"
    )
    FORM_MODAL_SUBMIT = (
        By.XPATH, "//div[@id='pum-674']//button[@type='submit']"
    )
    FORM_MODAL_SUCCESS = (
        By.XPATH, "//div[@id='pum-674']//h4[contains(text(), 'Thank you')]"
    )

    @property
    def is_available(self) -> bool:
        return self.is_element_available(self.SIMPLE_MODAL_TRIGGER)

    # ── Simple Modal ──────────────────────────────────────────────

    def open_simple_modal(self) -> None:
        """Click the Simple Modal trigger button.

        Uses _safe_click (JS-fallback) because Popup Maker's event system
        in Firefox does not always propagate native Selenium clicks.
        """
        self._safe_click(self.SIMPLE_MODAL_TRIGGER)
        # Wait for the modal animation to finish before proceeding
        self.wait.until(EC.visibility_of_element_located(self.SIMPLE_MODAL_OVERLAY))

    def is_simple_modal_visible(self) -> bool:
        """Return True if the Simple Modal overlay is displayed."""
        return self.is_element_available(self.SIMPLE_MODAL_OVERLAY) and \
            self.find_element(self.SIMPLE_MODAL_OVERLAY).is_displayed()

    def get_simple_modal_title(self) -> str:
        """Return the title text of the Simple Modal."""
        self.wait.until(EC.visibility_of_element_located(self.SIMPLE_MODAL_TITLE))
        return self.find_element(self.SIMPLE_MODAL_TITLE).text

    def get_simple_modal_content(self) -> str:
        """Return the content body text of the Simple Modal."""
        self.wait.until(EC.visibility_of_element_located(self.SIMPLE_MODAL_CONTENT))
        return self.find_element(self.SIMPLE_MODAL_CONTENT).text

    def close_simple_modal(self) -> None:
        """Click the close button on the Simple Modal.

        Uses _safe_click (JS-fallback) for consistency with Popup Maker
        event handling across all browsers.
        """
        self._safe_click(self.SIMPLE_MODAL_CLOSE)

    # ── Form Modal ────────────────────────────────────────────────

    def open_form_modal(self) -> None:
        """Click the Form Modal trigger button.

        Uses _safe_click (JS-fallback) because Popup Maker's event system
        in Firefox does not always propagate native Selenium clicks.
        """
        self._safe_click(self.FORM_MODAL_TRIGGER)
        # Wait for the modal animation to finish before proceeding
        self.wait.until(EC.visibility_of_element_located(self.FORM_MODAL_OVERLAY))

    def is_form_modal_visible(self) -> bool:
        """Return True if the Form Modal overlay is displayed."""
        return self.is_element_available(self.FORM_MODAL_OVERLAY) and \
            self.find_element(self.FORM_MODAL_OVERLAY).is_displayed()

    def get_form_modal_title(self) -> str:
        """Return the title text of the Form Modal."""
        return self.find_element(self.FORM_MODAL_TITLE).text

    def close_form_modal(self) -> None:
        """Click the close button on the Form Modal.

        Uses _safe_click (JS-fallback) for consistency with Popup Maker
        event handling across all browsers.
        """
        self._safe_click(self.FORM_MODAL_CLOSE)

    # ── Form Modal — form interaction ─────────────────────────────

    def fill_form_name(self, name: str) -> None:
        """Type into the Name field inside the Form Modal."""
        el = self.find_element(self.FORM_MODAL_NAME)
        el.clear()
        el.send_keys(name)

    def fill_form_email(self, email: str) -> None:
        """Type into the Email field inside the Form Modal."""
        el = self.find_element(self.FORM_MODAL_EMAIL)
        el.clear()
        el.send_keys(email)

    def fill_form_message(self, message: str) -> None:
        """Type into the Message textarea inside the Form Modal."""
        el = self.find_element(self.FORM_MODAL_MESSAGE)
        el.clear()
        el.send_keys(message)

    def submit_form(self) -> None:
        """Click the Submit button inside the Form Modal.

        Uses _safe_click (JS-fallback) to handle overlay interception.
        """
        self._safe_click(self.FORM_MODAL_SUBMIT)

    def wait_for_simple_modal_closed(self) -> bool:
        """Wait for the Simple Modal overlay to become invisible.

        Returns True if it closes within the default timeout, False otherwise.
        """
        return self.wait_until_invisible(self.SIMPLE_MODAL_OVERLAY)

    def wait_for_form_modal_closed(self) -> bool:
        """Wait for the Form Modal overlay to become invisible.

        Returns True if it closes within the default timeout, False otherwise.
        """
        return self.wait_until_invisible(self.FORM_MODAL_OVERLAY)

    def is_form_submission_successful(self) -> bool:
        """Return True if the success message is visible after submit."""
        return self.is_element_available(self.FORM_MODAL_SUCCESS)

    # ── Email validation ────────────────────────────────────────

    def click_form_modal_message(self) -> None:
        """Click the Message field to trigger HTML5 email validation."""
        self.find_element(self.FORM_MODAL_MESSAGE).click()

    def get_email_validation_message(self) -> str | None:
        """Return the browser's native HTML5 validation message for the email field.

        Returns the validation message string (e.g. "Please enter a valid email address.")
        if the field is invalid, or None if the field is valid.
        """
        el = self.find_element(self.FORM_MODAL_EMAIL)
        return el.get_attribute("validationMessage") or None
