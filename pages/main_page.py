import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
import config


class MainPage(BasePage):
    ACCORDIONS_LINK = (By.LINK_TEXT, "Accordions")
    JAVASCRIPT_DELAYS_LINK = (By.LINK_TEXT, "JavaScript Delays")
    FORM_FIELDS_LINK = (By.LINK_TEXT, "Form Fields")
    POPUPS_LINK = (By.LINK_TEXT, "Popups")
    MODALS_LINK = (By.LINK_TEXT, "Modals")
    SLIDERS_LINK = (By.LINK_TEXT, "Sliders")
    TABLES_LINK = (By.LINK_TEXT, "Tables")
    CALENDARS_LINK = (By.LINK_TEXT, "Calendars")
    WINDOW_OPERATIONS_LINK = (By.LINK_TEXT, "Window Operations")
    HOVER_LINK = (By.LINK_TEXT, "Hover")
    ADS_LINK = (By.LINK_TEXT, "Ads")
    GESTURES_LINK = (By.LINK_TEXT, "Gestures")
    FILE_DOWNLOAD_LINK = (By.LINK_TEXT, "File Download")
    FILE_UPLOAD_LINK = (By.LINK_TEXT, "File Upload")
    CLICK_EVENTS_LINK = (By.LINK_TEXT, "Click Events")
    SPINNERS_LINK = (By.LINK_TEXT, "Spinners")
    IFRAMES_LINK = (By.LINK_TEXT, "Iframes")
    BROKEN_IMAGES_LINK = (By.LINK_TEXT, "Broken Images")
    BROKEN_LINKS_LINK = (By.LINK_TEXT, "Broken Links")

    # URL slugs for direct navigation fallback.
    # Safari on macOS CI cannot reliably render the main page's link-text
    # elements — navigate directly to the sub-page instead.
    _SUB_PAGE_SLUGS = {
        "go_to_accordions": "/accordions/",
        "go_to_form_fields": "/form-fields/",
        "go_to_popups": "/popups/",
        "go_to_modals": "/modals/",
        "go_to_sliders": "/sliders/",
        "go_to_tables": "/tables/",
        "go_to_calendars": "/calendars/",
        "go_to_window_operations": "/window-operations/",
        "go_to_hover": "/hover/",
        "go_to_ads": "/ads/",
        "go_to_gestures": "/gestures/",
        "go_to_file_download": "/file-download/",
        "go_to_file_upload": "/file-upload/",
        "go_to_click_events": "/click-events/",
        "go_to_spinners": "/spinners/",
        "go_to_iframes": "/iframes/",
        "go_to_broken_images": "/broken-images/",
        "go_to_broken_links": "/broken-links/",
        "go_to_js_delays": "/javascript-delays/",
    }

    def open_page(self):
        self.open(config.BASE_URL)

    def is_loaded(self, timeout: int | None = None) -> bool:
        """Check if the main page has loaded within the given timeout."""
        return self.is_element_available(self.ACCORDIONS_LINK, timeout=timeout)

    def _is_webkit_ci(self) -> bool:
        """Return True if running WebKit (Safari) on CI.

        Checks ``_browser_name`` set on the driver instance in conftest.py
        and the ``CI`` / ``GITHUB_ACTIONS`` environment variable.
        """
        browser = getattr(self.driver, "_browser_name", None)
        is_ci = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"
        return browser == "webkit" and is_ci

    def _js_click(self, locator, caller_name: str | None = None):
        """Wait for the element to be clickable, scroll it into view,
        then click via JavaScript.

        JS click bypasses overlay interception (e.g. popups/modals/ads) that
        can block the native click in Chromium-based browsers (Edge, Opera).
        Waiting for *element_to_be_clickable* first ensures the element is
        visible and enabled before the JS click executes.

        For Safari on CI, the navigation links often fail to render.  When
        *caller_name* is provided and matches a known slug, fall back to
        navigating directly to the sub-page URL via ``driver.get()``.
        """
        # Safari-on-CI short-circuit: skip the clickable wait entirely
        # and navigate directly.
        if self._is_webkit_ci() and caller_name:
            slug = self._SUB_PAGE_SLUGS.get(caller_name)
            if slug:
                self.driver.get(config.BASE_URL.rstrip("/") + slug)
                return

        link = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
        self.driver.execute_script("arguments[0].click();", link)

    def go_to_js_delays(self):
        self._js_click(self.JAVASCRIPT_DELAYS_LINK, "go_to_js_delays")

    def go_to_form_fields(self):
        self._js_click(self.FORM_FIELDS_LINK, "go_to_form_fields")

    def go_to_popups(self):
        self._js_click(self.POPUPS_LINK, "go_to_popups")

    def go_to_modals(self):
        self._js_click(self.MODALS_LINK, "go_to_modals")

    def go_to_sliders(self):
        self._js_click(self.SLIDERS_LINK, "go_to_sliders")

    def go_to_tables(self):
        self._js_click(self.TABLES_LINK, "go_to_tables")

    def go_to_calendars(self):
        self._js_click(self.CALENDARS_LINK, "go_to_calendars")

    def go_to_window_operations(self):
        self._js_click(self.WINDOW_OPERATIONS_LINK, "go_to_window_operations")

    def go_to_hover(self):
        self._js_click(self.HOVER_LINK, "go_to_hover")

    def go_to_ads(self):
        self._js_click(self.ADS_LINK, "go_to_ads")

    def go_to_gestures(self):
        self._js_click(self.GESTURES_LINK, "go_to_gestures")

    def go_to_file_download(self):
        self._js_click(self.FILE_DOWNLOAD_LINK, "go_to_file_download")

    def go_to_accordions(self):
        self._js_click(self.ACCORDIONS_LINK, "go_to_accordions")

    def go_to_file_upload(self):
        self._js_click(self.FILE_UPLOAD_LINK, "go_to_file_upload")

    def go_to_click_events(self):
        self._js_click(self.CLICK_EVENTS_LINK, "go_to_click_events")

    def go_to_spinners(self):
        self._js_click(self.SPINNERS_LINK, "go_to_spinners")

    def go_to_iframes(self):
        self._js_click(self.IFRAMES_LINK, "go_to_iframes")

    def go_to_broken_images(self):
        self._js_click(self.BROKEN_IMAGES_LINK, "go_to_broken_images")

    def go_to_broken_links(self):
        self._js_click(self.BROKEN_LINKS_LINK, "go_to_broken_links")
