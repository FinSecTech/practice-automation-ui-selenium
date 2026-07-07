"""Tests for the Window Operations page.

Verifies three distinct window/tab behaviours:
1. **New Tab** — opens a new browser tab (increases window handle count)
2. **Replace Window** — navigates current tab to a new URL; Back returns
3. **New Window** — opens a new browser window (increases window handle count)
"""

from pages.window_operations_page import WindowOperationsPage, TARGET_URL


class TestWindowOperations:
    """Test suite for Window Operations page."""

    def test_new_tab(self, window_operations_page: WindowOperationsPage):
        """Click 'New Tab', verify a new tab opens at the target URL.

        Expectations:
        - A new window handle appears.
        - The new tab navigates to ``TARGET_URL``.
        - After closing the tab and switching back, we are on the
          Window Operations page.
        """
        old_handles = window_operations_page.get_window_handles()

        # Click and switch to the new tab
        new_handle = window_operations_page.open_new_tab()

        try:
            # We are now on the new tab
            assert window_operations_page.driver.current_url == TARGET_URL, (
                f"Expected new tab URL to be {TARGET_URL}, "
                f"got {window_operations_page.driver.current_url}"
            )
        finally:
            # Cleanup: close the new tab and switch back to the original
            window_operations_page.close_current_handle()
            window_operations_page.switch_to_window(old_handles[0])

        # Verify we are back on the Window Operations page
        assert window_operations_page.is_available, (
            "Should be back on the Window Operations page after closing the tab"
        )

    def test_replace_window(self, window_operations_page: WindowOperationsPage):
        """Click 'Replace Window', verify URL changes and Back works.

        Expectations:
        - The URL changes to ``TARGET_URL`` (no new tab/window).
        - Window handle count remains the same.
        - Browser Back returns to the original Window Operations page.
        """
        original_url = window_operations_page.current_url
        old_handles = window_operations_page.get_window_handles()

        # Click — this navigates the *current* tab
        window_operations_page.replace_window()

        # The URL should now be the target
        assert TARGET_URL in window_operations_page.current_url, (
            f"Expected URL containing {TARGET_URL}, "
            f"got {window_operations_page.current_url}"
        )

        # No new tab/window should have been opened
        assert len(window_operations_page.get_window_handles()) == len(old_handles), (
            "Replace Window should not open a new tab or window"
        )

        # Navigate back — we should return to the original page
        assert window_operations_page.is_back_possible(original_url), (
            "Back navigation did not return to the original Window Operations URL"
        )

    def test_new_window(self, window_operations_page: WindowOperationsPage):
        """Click 'New Window', verify a new window opens at the target URL.

        Expectations:
        - A new window handle appears.
        - The new window navigates to ``TARGET_URL``.
        - After closing the new window and switching back, we are on the
          Window Operations page.
        """
        old_handles = window_operations_page.get_window_handles()

        # Click and switch to the new window
        new_handle = window_operations_page.open_new_window()

        try:
            # We are now on the new window
            assert window_operations_page.driver.current_url == TARGET_URL, (
                f"Expected new window URL to be {TARGET_URL}, "
                f"got {window_operations_page.driver.current_url}"
            )
        finally:
            # Cleanup: close the new window and switch back
            window_operations_page.close_current_handle()
            window_operations_page.switch_to_window(old_handles[0])

        # Verify we are back on the Window Operations page
        assert window_operations_page.is_available, (
            "Should be back on the Window Operations page after closing the window"
        )
