"""
Page object for the File Download page
(https://practice-automation.com/file-download/).

Provides methods to interact with both the normal (unlocked) download
button and the password-protected download flow that uses a WPDM
modal iframe.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
import config


class FileDownloadPage(BasePage):
    # ── Locators ──────────────────────────────────────────────────────
    # Normal (unlocked) download — uses a direct data-downloadurl
    NORMAL_DOWNLOAD_LINK = (By.CSS_SELECTOR, "a.wpdm-download-link.download-on-click")

    # Password-protected download — opens a modal iframe
    LOCKED_DOWNLOAD_LINK = (By.CSS_SELECTOR, "a.wpdm-download-link.wpdm-download-locked")

    # WPDM lock iframe — contains the password form
    LOCK_IFRAME = (By.ID, "wpdm-lock-frame")

    # Elements inside the lock iframe (only reachable after switching to it)
    # The password input and submit button have dynamic IDs but stable
    # selectors based on type/class.
    IFRAME_PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")
    IFRAME_SUBMIT_BUTTON = (By.CSS_SELECTOR, "input.wpdm_submit")
    IFRAME_START_DOWNLOAD_LINK = (By.CSS_SELECTOR, "a.btn-success")

    # The success-message span is always in the DOM (hidden with
    # display: none) and becomes visible only after a correct password.
    IFRAME_SUCCESS_MESSAGE = (
        By.XPATH, "//*[contains(text(), 'Your Download Link is Ready')]"
    )

    # The error message is case-sensitive — "Wrong Password!" not
    # "WRONG PASSWORD".  Use translate() for a case-insensitive match.
    IFRAME_ERROR_MESSAGE = (
        By.XPATH,
        "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'wrong password')]",
    )

    # ── Properties ────────────────────────────────────────────────────

    @property
    def is_available(self) -> bool:
        """The page is considered loaded when the normal download button
        is present."""
        return self.is_element_available(self.NORMAL_DOWNLOAD_LINK)

    # ── Normal download helpers ───────────────────────────────────────

    def get_normal_download_url(self) -> str | None:
        """Return the raw download URL from the data-downloadurl
        attribute (can be used for direct HTTP verification)."""
        link = self.find_element(self.NORMAL_DOWNLOAD_LINK)
        return link.get_attribute("data-downloadurl")

    def click_normal_download(self) -> None:
        """Click the normal (unlocked) Download button."""
        self.find_clickable(self.NORMAL_DOWNLOAD_LINK).click()

    # ── Password-protected download helpers ───────────────────────────

    def click_locked_download(self) -> None:
        """Click the password-protected Download button.

        This triggers a WPDM unlock iframe to appear.
        """
        self.find_clickable(self.LOCKED_DOWNLOAD_LINK).click()

    def is_lock_iframe_present(self, timeout: int | None = None) -> bool:
        """Return True if the WPDM lock iframe becomes present within
        the given timeout."""
        return self.is_element_available(self.LOCK_IFRAME, timeout)

    def switch_to_lock_iframe(self) -> None:
        """Switch the driver context into the WPDM lock iframe."""
        iframe = self.wait.until(EC.presence_of_element_located(self.LOCK_IFRAME))
        self.driver.switch_to.frame(iframe)

    def switch_to_default_content(self) -> None:
        """Switch the driver context back to the main page."""
        self.driver.switch_to.default_content()

    def wait_for_iframe_password_input(self) -> None:
        """Wait until the password input inside the lock iframe becomes
        visible (AJAX-loaded content)."""
        self.wait.until(
            EC.visibility_of_element_located(self.IFRAME_PASSWORD_INPUT)
        )

    def enter_password_in_iframe(self, password: str) -> None:
        """Type *password* into the password input inside the lock
        iframe."""
        pw = self.wait.until(EC.visibility_of_element_located(self.IFRAME_PASSWORD_INPUT))
        pw.clear()
        pw.send_keys(password)

    def submit_password_in_iframe(self) -> None:
        """Click the Submit button inside the lock iframe."""
        btn = self.wait.until(EC.element_to_be_clickable(self.IFRAME_SUBMIT_BUTTON))
        btn.click()

    def is_password_verified_in_iframe(self, timeout: int | None = None) -> bool:
        """Return *True* once the success message becomes **visible**
        inside the iframe (meaning the password was accepted).

        Uses visibility check because the success-message span exists in
        the DOM from the start (hidden with ``display: none``) and is
        only shown after a correct password.
        """
        wait = WebDriverWait(self.driver, timeout or config.DEFAULT_TIMEOUT)
        try:
            wait.until(EC.visibility_of_element_located(self.IFRAME_SUCCESS_MESSAGE))
            return True
        except TimeoutException:
            return False

    def is_wrong_password_error_in_iframe(self, timeout: int | None = None) -> bool:
        """Return *True* if the wrong-password error becomes visible
        inside the iframe."""
        wait = WebDriverWait(self.driver, timeout or config.DEFAULT_TIMEOUT)
        try:
            wait.until(EC.visibility_of_element_located(self.IFRAME_ERROR_MESSAGE))
            return True
        except TimeoutException:
            return False

    def click_start_download_in_iframe(self) -> None:
        """Click the *DOWNLOAD* link that replaces the password form
        after successful verification inside the iframe."""
        link = self.wait.until(EC.element_to_be_clickable(self.IFRAME_START_DOWNLOAD_LINK))
        link.click()

    # ── Convenience: full unlock flow ─────────────────────────────────

    def unlock_password_protected_download(self, password: str) -> None:
        """High-level helper that performs the full unlock flow:
        1. Click the locked download button
        2. Switch into the lock iframe
        3. Wait for the password input to be visible (AJAX load)
        4. Enter the password and submit
        5. Wait for verification and click the start-download link
        6. Switch back to default content

        Raises TimeoutException if any step fails.
        """
        self.click_locked_download()
        self.switch_to_lock_iframe()
        self.wait_for_iframe_password_input()
        self.enter_password_in_iframe(password)
        self.submit_password_in_iframe()
        if not self.is_password_verified_in_iframe():
            raise TimeoutException(
                "Password verification failed — the success message "
                "did not appear inside the lock iframe."
            )
        self.click_start_download_in_iframe()
        self.switch_to_default_content()
