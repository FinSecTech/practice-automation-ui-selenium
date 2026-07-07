from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from pages.base_page import BasePage


class BrokenImagesPage(BasePage):
    """
    Page object for https://practice-automation.com/broken-images/

    The page has 3 images in the main content area:
      1. Working JavaScript logo (https … javascript-logo.jpg)
      2. Broken 1.jpg
      3. Broken 2.jpg

    These images live inside ``div.entry-content`` (the WordPress post body).
    The page has dynamic content loading (comments, related posts) that
    injects additional <img> elements over time.  ``_fetch_all_images``
    waits for the working image's naturalWidth to be > 0 before querying
    the DOM, ensuring the page is settled and we get a clean snapshot.

    All image data is collected via a single JavaScript evaluation to:
      - Get the raw HTML src/alt attributes (not resolved absolute URLs)
      - Read naturalWidth/naturalHeight for every image at once
      - Avoid stale-element / MoveTargetOutOfBounds exceptions
    """

    IMG_SELECTOR = "#post-1218 .wp-block-columns .wp-block-column img"
    FIRST_IMG = (By.CSS_SELECTOR, "#post-1218 .wp-block-columns .wp-block-column img")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self._image_cache: list[dict] | None = None

    @property
    def is_available(self) -> bool:
        return self.is_element_available(self.FIRST_IMG)

    def _fetch_all_images(self) -> list[dict]:
        """Wait for the working image to load (naturalWidth > 0) so the page
        is in a settled state, then collect all image data in one JS call."""
        # Wait until at least one img with non-zero natural dimensions is present
        # in the entry content.  This gives dynamic content time to load.
        self.wait.until(
            lambda d: d.execute_script(
                """return Array.from(document.querySelectorAll('%s'))
                             .some(i => i.naturalWidth > 0);"""
                % self.IMG_SELECTOR
            )
        )

        result = self.driver.execute_script("""
            return Array.from(document.querySelectorAll('%s')).map(img => {
                const natW = img.naturalWidth;
                const natH = img.naturalHeight;
                const isBroken = natW === 0 && natH === 0;
                return {
                    src: img.getAttribute('src') || '',
                    alt: img.getAttribute('alt') || '',
                    natural_width: natW,
                    natural_height: natH,
                    is_broken: isBroken,
                };
            }) || [];
        """ % self.IMG_SELECTOR)
        return result if result is not None else []

    def get_all_images(self) -> list[dict]:
        """Return a list of dicts with src, alt, and natural-dimension info
        for every <img> inside .entry-content.

        Results are cached so that multiple calls within the same test
        return a consistent snapshot.  Call invalidate_cache() to force
        a fresh query.
        """
        if self._image_cache is None:
            self._image_cache = self._fetch_all_images()
        return list(self._image_cache)

    def invalidate_cache(self) -> None:
        """Discard the cached image list so the next call re-queries the DOM."""
        self._image_cache = None

    @property
    def broken_images(self) -> list[dict]:
        return [img for img in self.get_all_images() if img["is_broken"]]

    @property
    def working_images(self) -> list[dict]:
        return [img for img in self.get_all_images() if not img["is_broken"]]
