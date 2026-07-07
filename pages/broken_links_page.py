"""
Page object for https://practice-automation.com/broken-links/

The page contains a paragraph with links, one of which intentionally points to
a missing page (missing-page.html) that returns HTTP 404.  This class collects
all <a> elements from the main content area and checks their HTTP response
status codes.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from pages.base_page import BasePage
import config


class BrokenLinksPage(BasePage):
    """
    Page object for the Broken Links page.

    Provides methods to scrape all links from the page content area and
    verify their HTTP response codes to identify broken (non-200) links.

    Link data is collected via a single JavaScript evaluation to avoid
    stale-element exceptions caused by dynamic DOM updates on the page.

    HTTP requests use config.SHORT_TIMEOUT for timeouts, with minimal retries.
    """

    PAGE_URL = "https://practice-automation.com/broken-links/"
    MISSING_PAGE_URL = "https://practice-automation.com/broken-links/missing-page.html"

    # Only target <a> inside <p> within .entry-content to avoid picking up
    # sidebar, header, footer, or widget links (the original .entry-content a[href]
    # selector returned 20+ links on a loaded page).
    LINK_SELECTOR = ".entry-content p a[href]"
    FIRST_LINK = (By.CSS_SELECTOR, LINK_SELECTOR)
    # Unique element only present on the Broken Links page (the <figure> table
    # showing missing-page.html HTTP status). Used by is_available to avoid false
    # positives when navigation from the main page fails.
    UNIQUE_INDICATOR = (By.CSS_SELECTOR, ".wp-block-table")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self._links_cache: list[dict] | None = None
        self._status_cache: list[dict] | None = None
        self._session: requests.Session | None = None

    def _http_session(self) -> requests.Session:
        """Return a requests.Session with a retry adapter for rate limiting.

        Uses config.SHORT_TIMEOUT for request timeouts. 5 retries with
        4.0s backoff factor handle the server's aggressive rate limiting (429)
        under parallel xdist load where multiple workers hit the same origin.

        The exponential backoff sequence: 4s, 8s, 16s, 32s, 64s — totalling
        ~124s before giving up. This is long enough to pass through most
        rate-limiting windows on practice-automation.com.
        """
        if self._session is None:
            self._session = requests.Session()
            retries = Retry(
                total=5,
                backoff_factor=4.0,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"],
                raise_on_status=False,
            )
            adapter = HTTPAdapter(max_retries=retries)
            self._session.mount("https://", adapter)
            self._session.mount("http://", adapter)
            self._session.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            })
        return self._session

    @property
    def is_available(self) -> bool:
        """Check we're on the real Broken Links page (table element unique to this page).

        Uses UNIQUE_INDICATOR (a <figure class="wp-block-table"> present only on
        /broken-links/) to avoid false positives when navigation from the main
        page fails (the main page has .entry-content p a[href] links too).
        """
        from selenium.common.exceptions import TimeoutException
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        try:
            WebDriverWait(self.driver, config.SHORT_TIMEOUT).until(
                EC.presence_of_element_located(self.UNIQUE_INDICATOR)
            )
            return True
        except TimeoutException:
            return False

    def _fetch_all_links_js(self) -> list[dict]:
        """Collect anchors from the page content area via a single
        JavaScript evaluation, avoiding stale-element references.

        The page has dynamic content (modals, related posts, comments) that
        can refresh the DOM, making Selenium element references stale.
        """
        result = self.driver.execute_script("""
            const anchors = document.querySelectorAll('%s');
            const links = [];
            for (let i = 0; i < anchors.length; i++) {
                const href = anchors[i].getAttribute('href') || '';
                if (href) {
                    links.push({
                        href: href,
                        text: (anchors[i].textContent || '').trim(),
                    });
                }
            }
            return links;
        """ % self.LINK_SELECTOR)
        return result if result is not None else []

    def get_all_links(self) -> list[dict]:
        """Collect every anchor tag from the page content area via JS.

        Returns a list of dicts with keys:
          - href: the absolute URL the link points to
          - text: the visible link text (stripped)
        """
        if self._links_cache is not None:
            return list(self._links_cache)
        self._links_cache = self._fetch_all_links_js()
        return list(self._links_cache)

    def check_link_status(self, url: str) -> int | None:
        """Send a GET request to *url* and return the HTTP status code.

        Uses config.SHORT_TIMEOUT for connect/read timeouts.

        Returns ``None`` if the request failed (network error, timeout, etc.).
        """
        try:
            resp = self._http_session().get(
                url,
                timeout=config.SHORT_TIMEOUT,
                allow_redirects=True,
            )
            return resp.status_code
        except requests.RequestException:
            return None

    def verify_all_links(self) -> list[dict]:
        """Scrape all content-area links and check each one's HTTP status.

        Returns a list of dicts with keys:
          - href:         the absolute URL
          - text:         the visible link text
          - status_code:  HTTP status code (int) or ``None`` on failure
          - is_broken:    ``True`` if not a 2xx response
        """
        links = self.get_all_links()
        results = []
        for link in links:
            status = self.check_link_status(link["href"])
            results.append({
                "href": link["href"],
                "text": link["text"],
                "status_code": status,
                "is_broken": status is None or status < 200 or status >= 300,
            })
        self._status_cache = results
        return results

    @property
    def broken_links(self) -> list[dict]:
        """Return only the links whose HTTP status is non-2xx."""
        results = self._status_cache if self._status_cache is not None else self.verify_all_links()
        return [r for r in results if r["is_broken"]]

    @property
    def working_links(self) -> list[dict]:
        """Return only the links whose HTTP status is 2xx."""
        results = self._status_cache if self._status_cache is not None else self.verify_all_links()
        return [r for r in results if not r["is_broken"]]

    def invalidate_caches(self) -> None:
        """Discard cached scrape and status results."""
        self._links_cache = None
        self._status_cache = None
