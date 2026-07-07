from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class AdsPage(BasePage):
    # Ad modal (auto-opened on page load by Popup Maker)
    AD_MODAL_OVERLAY = (By.ID, "pum-1272")
    AD_MODAL_CONTAINER = (By.ID, "popmake-1272")
    AD_MODAL_TITLE = (By.ID, "pum_popup_title_1272")
    AD_MODAL_CONTENT = (
        By.XPATH, "//div[@id='pum-1272']//div[@class='pum-content popmake-content']"
    )
    AD_MODAL_CLOSE = (
        By.XPATH, "//div[@id='pum-1272']//button[contains(@class, 'pum-close')]"
    )

    @property
    def is_available(self) -> bool:
        return self.is_element_available(self.AD_MODAL_OVERLAY)

    def wait_for_ad_modal_visible(self) -> None:
        """Wait for the ad modal overlay to become visible (auto-open delay)."""
        self.long_wait.until(
            EC.visibility_of_element_located(self.AD_MODAL_OVERLAY)
        )

    def is_ad_modal_visible(self) -> bool:
        """Return True if the ad modal overlay is currently displayed."""
        try:
            overlay = self.long_wait.until(
                EC.visibility_of_element_located(self.AD_MODAL_OVERLAY)
            )
            return overlay.is_displayed()
        except Exception:
            return False

    def get_ad_modal_title(self) -> str:
        """Return the title text of the ad modal."""
        return self.find_element(self.AD_MODAL_TITLE).text

    def get_ad_modal_content(self) -> str:
        """Return the content body text of the ad modal."""
        el = self.wait.until(EC.visibility_of_element_located(self.AD_MODAL_CONTENT))
        return el.text

    def close_ad_modal(self) -> None:
        """Click the close button on the ad modal.

        Uses _safe_click (JS-fallback) because Popup Maker's event system
        in Firefox does not always propagate native Selenium clicks, and
        overlay elements can intercept in Chromium-based browsers.
        """
        self._safe_click(self.AD_MODAL_CLOSE)

    def wait_for_ad_modal_closed(self) -> bool:
        """Wait for the ad modal overlay to become invisible.

        Returns True if it closes within the default timeout, False otherwise.
        """
        return self.wait_until_invisible(self.AD_MODAL_OVERLAY)
