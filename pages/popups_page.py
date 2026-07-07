from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class PopupsPage(BasePage):
    # JS Alert / Confirm / Prompt buttons
    ALERT_BUTTON = (By.ID, "alert")
    CONFIRM_BUTTON = (By.ID, "confirm")
    PROMPT_BUTTON = (By.ID, "prompt")

    # Result paragraphs where JS-popup outcomes are written
    CONFIRM_RESULT = (By.ID, "confirmResult")
    PROMPT_RESULT = (By.ID, "promptResult")

    # Tooltip
    TOOLTIP_TRIGGER = (By.CLASS_NAME, "tooltip_1")
    TOOLTIP_TEXT = (By.ID, "myTooltip")

    # Popup Maker modals (defined in the DOM but have NO visible trigger on the page)
    SIMPLE_MODAL_OVERLAY = (By.ID, "pum-1318")
    SIMPLE_MODAL_TITLE = (By.XPATH, "//div[@id='pum_popup_title_1318']")
    SIMPLE_MODAL_CONTENT = (By.XPATH, "//div[@id='pum-1318']//div[@class='pum-content popmake-content']")
    SIMPLE_MODAL_CLOSE = (By.XPATH, "//div[@id='pum-1318']//button[contains(@class, 'pum-close')]")
    FORM_MODAL_OVERLAY = (By.ID, "pum-674")
    FORM_MODAL_TITLE = (By.XPATH, "//div[@id='pum_popup_title_674']")
    FORM_MODAL_CLOSE = (By.XPATH, "//div[@id='pum-674']//button[contains(@class, 'pum-close')]")
    FORM_MODAL_FORM = (By.XPATH, "//div[@id='pum-674']//form")
    FORM_MODAL_NAME = (By.XPATH, "//div[@id='pum-674']//input[@type='text']")
    FORM_MODAL_EMAIL = (By.XPATH, "//div[@id='pum-674']//input[@type='email']")
    FORM_MODAL_MESSAGE = (By.XPATH, "//div[@id='pum-674']//textarea")
    FORM_MODAL_SUBMIT = (By.XPATH, "//div[@id='pum-674']//button[@type='submit']")
    FORM_MODAL_SUCCESS = (By.XPATH, "//div[@id='pum-674']//h4[contains(text(), 'Thank you')]")

    @property
    def is_available(self) -> bool:
        return self.is_element_available(self.ALERT_BUTTON)

    # ── Alert popup ────────────────────────────────────────────────

    def _trigger_alert(self) -> None:
        """Click the Alert Popup button (safe-click for overlay resilience)."""
        self._safe_click(self.ALERT_BUTTON)

    def get_alert_text_and_accept(self) -> str:
        """Trigger the alert, fetch its text, accept it, return the text."""
        self._trigger_alert()
        alert = self.long_wait.until(EC.alert_is_present())
        text = alert.text
        alert.accept()
        return text

    # ── Confirm popup ──────────────────────────────────────────────

    def _trigger_confirm(self) -> None:
        """Click the Confirm Popup button (safe-click for overlay resilience)."""
        self._safe_click(self.CONFIRM_BUTTON)

    def accept_confirm(self) -> str:
        """Accept the confirm dialog and return the result text."""
        self._trigger_confirm()
        alert = self.long_wait.until(EC.alert_is_present())
        alert.accept()
        return self.wait.until(
            EC.visibility_of_element_located(self.CONFIRM_RESULT)
        ).text

    def dismiss_confirm(self) -> str:
        """Dismiss (cancel) the confirm dialog and return the result text."""
        self._trigger_confirm()
        alert = self.long_wait.until(EC.alert_is_present())
        alert.dismiss()
        return self.wait.until(
            EC.visibility_of_element_located(self.CONFIRM_RESULT)
        ).text

    # ── Prompt popup ───────────────────────────────────────────────

    def _trigger_prompt(self) -> None:
        """Click the Prompt Popup button (safe-click for overlay resilience)."""
        self._safe_click(self.PROMPT_BUTTON)

    def fill_and_accept_prompt(self, text: str) -> str:
        """Enter text into the prompt and accept; return the result."""
        self._trigger_prompt()
        alert = self.long_wait.until(EC.alert_is_present())
        alert.send_keys(text)
        alert.accept()
        return self.wait.until(
            EC.visibility_of_element_located(self.PROMPT_RESULT)
        ).text

    def dismiss_prompt(self) -> str:
        """Dismiss (cancel) the prompt dialog; return the result."""
        self._trigger_prompt()
        alert = self.long_wait.until(EC.alert_is_present())
        alert.dismiss()
        return self.wait.until(
            EC.visibility_of_element_located(self.PROMPT_RESULT)
        ).text

    def accept_empty_prompt(self) -> str:
        """Accept the prompt with no text entered; return the result."""
        self._trigger_prompt()
        alert = self.long_wait.until(EC.alert_is_present())
        alert.accept()
        return self.wait.until(
            EC.visibility_of_element_located(self.PROMPT_RESULT)
        ).text

    # ── Popup Maker modals (expected failures — no visible triggers) ──

    def _verify_modal_overlay_shown(self, overlay_locator) -> None:
        """Check if a Popup Maker overlay is visible.

        When no trigger is present on the page the overlay should remain
        hidden (display: none), so this is expected to raise a timeout /
        return a closed state.
        """
        overlay = self.find_element(overlay_locator)
        return overlay.is_displayed()

    def is_simple_modal_accessible(self) -> bool:
        """Return True if the Simple Modal overlay is visible in the DOM.

        Expected to return False — the modal has no trigger on the page.
        """
        return self._verify_modal_overlay_shown(self.SIMPLE_MODAL_OVERLAY)

    def is_form_modal_accessible(self) -> bool:
        """Return True if the Form Modal overlay is visible in the DOM.

        Expected to return False — the modal has no trigger on the page.
        """
        return self._verify_modal_overlay_shown(self.FORM_MODAL_OVERLAY)

    # ── Tooltip ────────────────────────────────────────────────────

    def show_tooltip(self) -> None:
        """Click the tooltip trigger and wait for the state transition to complete.

        Without the explicit ``WebDriverWait`` after the click, there is a
        race condition between Selenium returning control and the browser's
        event loop dispatching the click handler that toggles the CSS class.
        Under xdist parallel load this window widens significantly, causing
        ``is_tooltip_visible()`` called immediately after ``show_tooltip()``
        to observe the *previous* state and fail the assertion.
        """
        el = self.find_element(self.TOOLTIP_TEXT)
        currently_visible = "show" in el.get_attribute("class")
        self._safe_click(self.TOOLTIP_TRIGGER)
        if currently_visible:
            self.wait.until(
                lambda d: "show" not in
                d.find_element(*self.TOOLTIP_TEXT).get_attribute("class")
            )
        else:
            self.wait.until(
                lambda d: "show" in
                d.find_element(*self.TOOLTIP_TEXT).get_attribute("class")
            )

    def is_tooltip_visible(self) -> bool:
        """Check whether the tooltip has the 'show' class (is visible)."""
        el = self.find_element(self.TOOLTIP_TEXT)
        return "show" in el.get_attribute("class")
