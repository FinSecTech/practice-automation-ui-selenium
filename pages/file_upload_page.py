"""
Page object for the File Upload page
(https://practice-automation.com/file-upload/).

The page provides a Contact Form 7 form with a file input that accepts
.txt, .docx, .pdf, .jpeg, .png, .jpg, .gif (max 1 MB) and a submit
button.  After upload the form shows a success or error response message.
"""

import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
import config


class FileUploadPage(BasePage):
    # ── Locators ──────────────────────────────────────────────────────
    # File input element (hidden by default, but Selenium can send_keys to it)
    FILE_INPUT = (By.ID, "file-upload")

    # Submit button
    SUBMIT_BUTTON = (By.ID, "upload-btn")

    # CF7 response output div
    RESPONSE_OUTPUT = (By.CSS_SELECTOR, "div.wpcf7-response-output")

    # Validation error tip (appears below the file input for invalid files)
    VALIDATION_ERROR = (By.CSS_SELECTOR, ".wpcf7-not-valid-tip")

    # ── Properties ────────────────────────────────────────────────────

    @property
    def is_available(self) -> bool:
        """The page is considered loaded when the file input is present."""
        return self.is_element_available(self.FILE_INPUT)

    # ── State helpers ─────────────────────────────────────────────────

    @property
    def response_text(self) -> str:
        """Return the text of the CF7 response output div."""
        return self.find_element(self.RESPONSE_OUTPUT).text

    def is_response_success(self) -> bool:
        """Return *True* if the response message indicates a successful
        upload (form class becomes 'failed' after CF7 processes the
        upload successfully)."""
        form = self.driver.find_element(By.CSS_SELECTOR, "form.wpcf7-form")
        cls = form.get_attribute("class")
        return "failed" in cls and "invalid" not in cls

    def is_response_error(self) -> bool:
        """Return *True* if the response message indicates a validation
        error."""
        form = self.driver.find_element(By.CSS_SELECTOR, "form.wpcf7-form")
        cls = form.get_attribute("class")
        return "invalid" in cls

    def get_validation_error_text(self) -> str:
        """Return the validation error tip text, or empty string if none."""
        try:
            el = self.driver.find_element(*self.VALIDATION_ERROR)
            return el.text
        except Exception:
            return ""

    # ── Actions ───────────────────────────────────────────────────────

    def select_file(self, file_path: str) -> None:
        """Set the file input to the given absolute file path."""
        file_input = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
        file_input.send_keys(file_path)

    def click_upload(self) -> None:
        """Click the Upload button and wait briefly for the AJAX
        response to appear."""
        btn = self.find_clickable(self.SUBMIT_BUTTON)
        btn.click()

    def wait_for_response(self, timeout: int | None = None) -> bool:
        """Wait until the CF7 response output becomes visible (AJAX
        submission completed).

        Returns *True* if it appeared within the timeout.
        """
        wait = WebDriverWait(self.driver, timeout or config.DEFAULT_TIMEOUT)
        try:
            wait.until(
                lambda d: d.find_element(*self.RESPONSE_OUTPUT).is_displayed()
            )
            return True
        except TimeoutException:
            return False

    # ── Convenience: full upload flow ─────────────────────────────────

    def upload_file(self, file_path: str) -> None:
        """High-level helper: select a file, click Upload, and wait for
        the AJAX response.

        *file_path* should be an absolute path to a valid test file.
        """
        self.select_file(file_path)
        self.click_upload()
        self.wait_for_response()
