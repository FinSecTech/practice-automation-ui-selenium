"""Page Object for the Window Operations page.

The page has three buttons that demonstrate different window/tab behaviours:
1. **New Tab** — opens a new browser tab (increases window handle count).
2. **Replace Window** — navigates the current tab to a new URL; the "Back"
   button in the browser becomes available to return to the original page.
3. **New Window** — opens a new browser window (increases window handle count).
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


# Target URL that each button navigates to
TARGET_URL = "https://automatenow.io/"


class WindowOperationsPage(BasePage):
    # ── Page elements ────────────────────────────────────────────────
    NEW_TAB_BUTTON = (
        By.XPATH,
        "//button[@class='custom_btn btn_hover']/b[text()='New Tab']/..",
    )
    REPLACE_WINDOW_BUTTON = (
        By.XPATH,
        "//button[@class='custom_btn btn_hover']/b[text()='Replace Window']/..",
    )
    NEW_WINDOW_BUTTON = (
        By.XPATH,
        "//button[@class='custom_btn btn_hover']/b[text()='New Window']/..",
    )

    # ── Availability ─────────────────────────────────────────────────
    @property
    def is_available(self) -> bool:
        return self.is_element_available(self.NEW_TAB_BUTTON)

    def open_page(self) -> None:
        import config

        self.open(f"{config.BASE_URL}window-operations/")
        assert self.is_available, "Window Operations page did not load"

    # ── Helpers ──────────────────────────────────────────────────────
    def get_window_handles(self) -> list[str]:
        return self.driver.window_handles

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    def navigate_back(self) -> None:
        self.driver.back()

    def switch_to_window(self, handle: str) -> None:
        self.driver.switch_to.window(handle)

    def switch_to_new_handle(self, old_handles: list[str]) -> str:
        """Switch to the handle that is new (present now but not in old_handles).

        Returns the new handle.
        """
        current = self.get_window_handles()
        for h in current:
            if h not in old_handles:
                self.driver.switch_to.window(h)
                return h
        raise RuntimeError("No new window handle found")

    def close_current_handle(self) -> None:
        self.driver.close()

    # ── New Tab ──────────────────────────────────────────────────────
    def click_new_tab(self) -> None:
        self.find_clickable(self.NEW_TAB_BUTTON).click()

    def open_new_tab(self) -> str:
        """Click 'New Tab', switch to the new tab, wait for navigation.

        Returns the new handle.
        """
        old = self.get_window_handles()
        self.click_new_tab()
        self.wait.until(lambda d: len(d.window_handles) > len(old))
        handle = self.switch_to_new_handle(old)
        self.long_wait.until(
            lambda d: d.current_url != "about:blank"
        )
        return handle

    def is_new_tab_opened(self, old_count: int) -> bool:
        try:
            self.wait.until(lambda d: len(d.window_handles) > old_count)
            return True
        except TimeoutException:
            return False

    # ── Replace Window ───────────────────────────────────────────────
    def click_replace_window(self) -> None:
        self.find_clickable(self.REPLACE_WINDOW_BUTTON).click()

    def replace_window(self) -> None:
        """Click 'Replace Window' and wait for URL to change."""
        self.click_replace_window()
        self.long_wait.until(
            lambda d: d.current_url != self.driver.current_url
            or TARGET_URL in d.current_url
        )

    def is_url_changed(self, original_url: str) -> bool:
        try:
            self.wait.until(lambda d: d.current_url != original_url)
            return True
        except TimeoutException:
            return False

    def is_back_possible(self, original_url: str) -> bool:
        """Navigate back and check we return to the original URL."""
        self.navigate_back()
        try:
            self.wait.until(lambda d: d.current_url == original_url)
            return True
        except TimeoutException:
            return False

    # ── New Window ───────────────────────────────────────────────────
    def click_new_window(self) -> None:
        self.find_clickable(self.NEW_WINDOW_BUTTON).click()

    def open_new_window(self) -> str:
        """Click 'New Window', switch to the new window, wait for navigation.

        Returns the new handle.
        """
        old = self.get_window_handles()
        self.click_new_window()
        self.wait.until(lambda d: len(d.window_handles) > len(old))
        handle = self.switch_to_new_handle(old)
        self.long_wait.until(
            lambda d: d.current_url != "about:blank"
        )
        return handle

    def is_new_window_opened(self, old_count: int) -> bool:
        try:
            self.wait.until(lambda d: len(d.window_handles) > old_count)
            return True
        except TimeoutException:
            return False
