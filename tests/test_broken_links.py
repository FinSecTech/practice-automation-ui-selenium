"""Tests for the Broken Links page — identify working vs. broken links."""

from pages.broken_links_page import BrokenLinksPage


class TestBrokenLinks:
    """Verify the page identifies all links and correctly finds the broken one.

    The server rate-limits rapid requests (HTTP 429), so external HTTP checks
    are kept to a minimum. The broken-link 404 is confirmed via browser
    navigation (reliable, not rate-limited).
    """

    # ------------------------------------------------------------------
    # Link scraping (no external HTTP)
    # ------------------------------------------------------------------

    def test_page_has_two_content_links(self, broken_links_page: BrokenLinksPage):
        """The page should contain exactly 2 links in the entry-content:
        the broken link and the 'HTTP response code' link."""
        links = broken_links_page.get_all_links()
        assert len(links) == 2, (
            f"Expected exactly 2 links in .entry-content, found {len(links)}"
        )

    def test_broken_link_has_correct_text_and_url(self, broken_links_page: BrokenLinksPage):
        """The first link should be 'broken link' pointing to missing-page.html."""
        links = broken_links_page.get_all_links()
        missing = [l for l in links if "missing-page" in l["href"]]
        assert len(missing) == 1
        assert missing[0]["text"] == "broken link"
        assert missing[0]["href"] == broken_links_page.MISSING_PAGE_URL

    def test_working_link_has_correct_text_and_url(self, broken_links_page: BrokenLinksPage):
        """The second link should be 'HTTP response code' to automatenow.io."""
        links = broken_links_page.get_all_links()
        external = [l for l in links if "automatenow" in l["href"] or "http" in l["href"] and "missing" not in l["href"]]
        assert len(external) == 1
        assert external[0]["text"] == "HTTP response code"
        assert "automatenow.io" in external[0]["href"]

    # ------------------------------------------------------------------
    # Broken link 404 verification via browser (immune to rate limiting)
    # ------------------------------------------------------------------

    def test_broken_link_returns_404_in_browser(self, broken_links_page: BrokenLinksPage):
        """Navigating the browser to missing-page.html should show a 404 / Not Found page.

        Catches TimeoutException from driver.get() — under parallel xdist load
        the server can be slow enough to exceed set_page_load_timeout (20s).
        The driver still has a usable partial page in that case.
        """
        from selenium.common.exceptions import TimeoutException
        from selenium.webdriver.support.ui import WebDriverWait
        import config as cfg

        try:
            broken_links_page.driver.get(broken_links_page.MISSING_PAGE_URL)
        except TimeoutException:
            pass

        try:
            WebDriverWait(broken_links_page.driver, cfg.DEFAULT_TIMEOUT).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            pass

        # Wait for body text to contain a 404 indicator
        try:
            WebDriverWait(broken_links_page.driver, cfg.DEFAULT_TIMEOUT).until(
                lambda d: "not found" in d.find_element("tag name", "body").text.lower()
                or "404" in d.find_element("tag name", "body").text.lower()
                or "could not find" in d.find_element("tag name", "body").text.lower()
            )
        except TimeoutException:
            pass

        page_text = broken_links_page.driver.find_element("tag name", "body").text.lower()
        assert "could not find" in page_text or "404" in page_text or "not found" in page_text, (
            f"Expected 404/Not Found, got title='{broken_links_page.driver.title}' "
            f"text='{page_text[:200]}'"
        )

        # Reload the proper page so future tests in session are not affected
        try:
            broken_links_page.open(broken_links_page.PAGE_URL)
        except TimeoutException:
            pass
        broken_links_page.invalidate_caches()

    # ------------------------------------------------------------------
    # Individual HTTP status checks (single requests — less likely to rate-limit)
    # ------------------------------------------------------------------

    def test_working_link_returns_200(self, broken_links_page: BrokenLinksPage):
        """The external link to automatenow.io should return HTTP 200."""
        status = broken_links_page.check_link_status(
            "https://automatenow.io/http-response-codes-in-api-testing/"
        )
        assert status == 200, (
            f"Expected 200 for working link, got {status}"
        )

    def test_missing_page_returns_404(self, broken_links_page: BrokenLinksPage):
        """The missing-page.html URL should return HTTP 404.

        Uses browser navigation (immune to HTTP rate limiting) with a
        retry loop and explicit readyState wait.

        Under parallel xdist load the server can be slow enough that
        driver.get() exceeds set_page_load_timeout (20s), throwing a
        TimeoutException. The retry loop re-issues the navigation.

        The HTTP-based check (check_link_status) is avoided here because
        practice-automation.com aggressively rate-limits HTTP requests in
        parallel runs (HTTP 429). Browser navigation is not subject to
        this limit and works reliably cross-browser.
        """
        from selenium.common.exceptions import TimeoutException
        from selenium.webdriver.support.ui import WebDriverWait
        import config as cfg

        # Retry navigation up to 3 times — page-load timeout under load
        for attempt in range(3):
            try:
                broken_links_page.driver.get(broken_links_page.MISSING_PAGE_URL)
                break
            except TimeoutException:
                if attempt == 2:
                    # Last attempt: proceed with whatever page was loaded
                    pass

        try:
            WebDriverWait(broken_links_page.driver, cfg.DEFAULT_TIMEOUT).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            pass

        # Wait for body text to contain a 404 indicator
        try:
            WebDriverWait(broken_links_page.driver, cfg.DEFAULT_TIMEOUT).until(
                lambda d: "not found" in d.find_element("tag name", "body").text.lower()
                or "404" in d.find_element("tag name", "body").text.lower()
                or "could not find" in d.find_element("tag name", "body").text.lower()
            )
        except TimeoutException:
            pass

        title = broken_links_page.driver.title
        current_url = broken_links_page.driver.current_url
        page_text = broken_links_page.driver.find_element("tag name", "body").text.lower()
        assert "could not find" in page_text or "404" in page_text or "not found" in page_text, (
            f"Expected 404/Not Found for missing-page.html. "
            f"URL='{current_url}', title='{title}', "
            f"text='{page_text[:200]}'"
        )

        # Reload the proper page so future tests in session are not affected
        broken_links_page.open(broken_links_page.PAGE_URL)
        broken_links_page.invalidate_caches()

    # ------------------------------------------------------------------
    # Full scan detection
    # ------------------------------------------------------------------

    def test_broken_link_detected_in_full_scan(self, broken_links_page: BrokenLinksPage):
        """The missing-page.html link should be flagged as broken during a
        full scan. Working links may be rate-limited (429) but the broken
        link must always be detected.

        We refresh the page first so the DOM is in a clean state.
        """
        broken_links_page.open(broken_links_page.PAGE_URL)
        broken_links_page.invalidate_caches()

        results = broken_links_page.verify_all_links()
        broken = broken_links_page.broken_links
        assert len(broken) >= 1, (
            f"Expected at least 1 broken link, found {len(broken)}. "
            f"Results: {[(r['href'], r['status_code']) for r in results]}"
        )
        # At least one broken link should point to missing-page
        assert any("missing-page" in b["href"] for b in broken), (
            f"No broken link points to missing-page. Broken: {[b['href'] for b in broken]}"
        )
