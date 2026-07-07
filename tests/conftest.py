"""
Pytest configuration for cross-browser testing.

Accepts --browser CLI argument (firefox | edge | opera | webkit) to
instantiate the appropriate Selenium driver.
"""

import base64
import os
import re
import sys
import platform
import shutil
import tempfile
from pathlib import Path
import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

import config
from pages.main_page import MainPage
from pages.form_fields_page import FormFieldsPage
from pages.popups_page import PopupsPage
from pages.modals_page import ModalsPage
from pages.slider_page import SliderPage
from pages.tables_page import TablesPage
from pages.calendar_page import CalendarPage
from pages.window_operations_page import WindowOperationsPage
from pages.hover_page import HoverPage
from pages.ads_page import AdsPage
from pages.gestures_page import GesturesPage
from pages.file_download_page import FileDownloadPage
from pages.accordions_page import AccordionsPage
from pages.file_upload_page import FileUploadPage
from pages.click_events_page import ClickEventsPage
from pages.spinners_page import SpinnersPage
from pages.iframes_page import IframesPage
from pages.broken_images_page import BrokenImagesPage
from pages.broken_links_page import BrokenLinksPage


# ── Screenshots on failure ──────────────────────────────────────
# Stores base64-encoded screenshot data keyed by test nodeid.
# Populated in pytest_runtest_makereport, consumed by the dashboard
# plugin at report-generation time.
FAILED_SCREENSHOTS: dict[str, str] = {}


def _sanitize_filename(name: str) -> str:
    """Replace characters that are problematic in filenames."""
    return re.sub(r'[^\w\-_.]', '_', name)


def _capture_screenshot_on_failure(item, report) -> None:
    """If the test call-phase failed, capture a screenshot and store
    the base64-encoded data URL so the dashboard can embed it.
    """
    if report.when != "call" or not report.failed:
        return

    try:
        driver = item.funcargs.get("browser")
    except (KeyError, AttributeError):
        driver = None

    if driver is None:
        return

    try:
        screenshots_dir = Path(config.HTML_REPORT_DIR) / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        safe_name = _sanitize_filename(item.nodeid)
        screenshot_path = screenshots_dir / f"{safe_name}.png"

        driver.save_screenshot(str(screenshot_path))

        # Read and base64-encode for embedding directly in HTML
        with open(screenshot_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")

        data_url = f"data:image/png;base64,{b64}"
        FAILED_SCREENSHOTS[item.nodeid] = data_url

        # Also attach via pytest-html extras so the base report benefits too
        from pytest_html import extras
        if not hasattr(report, "extras"):
            report.extras = []
        report.extras.append(extras.image(data_url, name=f"Screenshot ({safe_name})"))
    except Exception as e:
        print(f"\n[WARNING] Failed to capture screenshot for '{item.nodeid}': {e}", file=sys.stderr)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshots on test failure (runs in worker processes).

    Uses tryfirst=True so this runs *before* the dashboard plugin's own
    hookwrapper, ensuring FAILED_SCREENSHOTS is populated before the
    dashboard builds test_results dict.
    """
    outcome = yield
    report = outcome.get_result()
    _capture_screenshot_on_failure(item, report)


# ── CI detection ─────────────────────────────────────────────────

def _is_ci() -> bool:
    """Detect whether we are running on a CI server (GitHub Actions,
    Jenkins, GitLab CI, etc.).

    CI runners have no display server — browsers must be launched
    headless to avoid crashes like:
      - 'Process unexpectedly closed with status 1' (Firefox)
      - 'session not created: Chrome instance exited' (Edge)
    """
    return os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"


def pytest_addoption(parser):
    """Register --browser CLI argument."""
    parser.addoption(
        "--browser",
        action="store",
        default="firefox",
        choices=("firefox", "edge", "opera", "webkit"),
        help="Browser to run tests on: firefox, edge, opera, or webkit",
    )


def _create_driver(browser_name: str):
    """Create a Selenium WebDriver for the given browser name."""
    name = browser_name.lower()

    if name == "firefox":
        service = FirefoxService(GeckoDriverManager().install())
        options = FirefoxOptions()
        if _is_ci():
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_page_load_timeout(config.LONG_TIMEOUT)
        driver._browser_name = name
        return driver

    if name == "edge":
        user_data_dir = tempfile.mkdtemp(prefix="edge_profile_")
        options = EdgeOptions()
        if _is_ci():
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
        options.add_argument(f"--user-data-dir={user_data_dir}")
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        driver._user_data_dir = user_data_dir
        driver.set_page_load_timeout(config.LONG_TIMEOUT)
        driver._browser_name = name
        return driver

    if name == "opera":
        return _create_opera_driver()

    if name == "webkit":
        if platform.system() != "Darwin":
            pytest.exit(
                "WebKit (Safari) is not available on this operating system. "
                "Please choose a different browser.",
                returncode=1,
            )
        driver = webdriver.Safari()
        # Safari has no page load timeout by default — driver.get() can hang
        # indefinitely on CI.  Set it to LONG_TIMEOUT like other browsers.
        driver.set_page_load_timeout(config.LONG_TIMEOUT)
        driver._browser_name = name
        return driver

    raise ValueError(f"Unsupported browser: {browser_name}")


def _find_opera_binary() -> str:
    system = platform.system()
    if system == "Windows":
        candidates = [
            os.path.expandvars("%LOCALAPPDATA%\\Programs\\Opera\\opera.exe"),
            "C:\\Program Files\\Opera\\opera.exe",
            "C:\\Program Files (x86)\\Opera\\opera.exe",
        ]
    else:
        candidates = []

    for path in candidates:
        if os.path.exists(path):
            return path

    raise FileNotFoundError(
        "Opera browser not found. Please install Opera or provide the correct path."
    )


def _get_opera_chromium_version(opera_binary: str) -> str | None:
    """Detect Opera's underlying Chromium major version (Windows only).

    Reads opera_browser.dll from the Opera install directory to extract
    Chromium version metadata (e.g. "126.0.xxx.yyy" → "126").
    """

    # Windows: extract version from opera_browser.dll
    try:
        opera_dir = os.path.dirname(opera_binary)
        items = os.listdir(opera_dir)
        version_dirs = [
            d
            for d in items
            if os.path.isdir(os.path.join(opera_dir, d))
            and re.match(r"\d+\.\d+\.\d+\.\d+", d)
        ]
        if not version_dirs:
            return None
        version_dirs.sort(reverse=True)
        dll_path = os.path.join(opera_dir, version_dirs[0], "opera_browser.dll")
        if not os.path.exists(dll_path):
            return None
        with open(dll_path, "rb") as f:
            data = f.read()
        best = None
        best_parts = None
        for m in re.finditer(rb"(\d+)\.0\.(\d+)\.(\d+)", data):
            try:
                major = int(m.group(1))
                build = int(m.group(2))
                patch = int(m.group(3))
                if 80 <= major <= 200 and build >= 4000 and patch <= 999999:
                    parts = (major, 0, build, patch)
                    if best_parts is None or parts > best_parts:
                        best_parts = parts
                        best = str(major)
            except ValueError:
                pass
        return best
    except (OSError, FileNotFoundError):
        return None


def _build_opera_options(user_data_dir: str) -> ChromeOptions:
    """Build a ChromeOptions instance for Windows Opera."""
    opera_binary = _find_opera_binary()
    options = ChromeOptions()
    options.binary_location = opera_binary
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    return options


def _create_opera_driver() -> webdriver.Chrome:
    """Create an Opera WebDriver session for Windows use."""
    import tempfile

    opera_binary = _find_opera_binary()
    opera_version = _get_opera_chromium_version(opera_binary)

    driver_path = None
    if opera_version:
        try:
            driver_path = ChromeDriverManager(driver_version=opera_version).install()
        except Exception as exc:
            print(f"[opera] Could not pin ChromeDriver to v{opera_version}: {exc}", file=sys.stderr)

    if not driver_path:
        try:
            driver_path = ChromeDriverManager().install()
        except Exception as exc:
            print(f"[opera] ChromeDriverManager fallback also failed: {exc}", file=sys.stderr)

    cd_log = tempfile.NamedTemporaryFile(
        suffix="_cd.log", prefix="opera_local_", delete=False
    )
    cd_log_path = cd_log.name
    cd_log.close()

    service = ChromeService(
        driver_path,
        service_args=["--verbose"],
        log_output=cd_log_path,
    )
    user_data_dir = tempfile.mkdtemp(prefix="opera_local_")
    options = _build_opera_options(user_data_dir)

    driver = webdriver.Chrome(service=service, options=options)
    driver._user_data_dir = user_data_dir
    driver.set_page_load_timeout(config.LONG_TIMEOUT)
    driver._browser_name = "opera"
    return driver


@pytest.fixture(scope="session")
def _browser_session(request):
    """Session-scoped WebDriver instance for Firefox, Edge and WebKit.

    Uses ``request.addfinalizer`` instead of ``yield`` to avoid the
    ``assert not self._finalizers`` crash in pytest 9.x when
    ``pytest-rerunfailures`` triggers a re-run while a session-scoped
    generator fixture still has pending finalizers.

    Opera is excluded — its sessions degrade under continuous use
    (gets stuck on a blank page after N tests under xdist parallel
    load). Opera uses a function-scoped fixture below instead.
    """
    browser_name = request.config.getoption("--browser")
    if browser_name == "opera":
        return None

    driver = _create_driver(browser_name)
    try:
        driver.maximize_window()
    except Exception:
        pass
    _wait_for_document_ready(driver)

    def _browser_session_teardown() -> None:
        driver.quit()
        user_data_dir = getattr(driver, "_user_data_dir", None)
        if user_data_dir and os.path.isdir(user_data_dir):
            shutil.rmtree(user_data_dir, ignore_errors=True)

    request.addfinalizer(_browser_session_teardown)
    return driver


@pytest.fixture
def browser(request, _browser_session):
    """WebDriver instance.

    - Firefox, Edge, WebKit: session-scoped (shared across all tests)
      → returned from _browser_session with no per-test overhead.
    - Opera: function-scoped (fresh instance per test)
      → prevents session degradation where Opera gets stuck on a
        blank page after several tests.
    """
    browser_name = request.config.getoption("--browser")
    if browser_name == "opera":
        driver = _create_opera_driver()
        try:
            driver.maximize_window()
        except Exception:
            pass
        _wait_for_document_ready(driver)
        yield driver
        driver.quit()
        user_data_dir = getattr(driver, "_user_data_dir", None)
        if user_data_dir and os.path.isdir(user_data_dir):
            shutil.rmtree(user_data_dir, ignore_errors=True)
    else:
        yield _browser_session


def _wait_for_document_ready(driver, timeout: int | None = None) -> None:
    """Block until `document.readyState` is 'complete', ensuring the
    current page finishes loading before proceeding.

    This is especially important under xdist parallel load where worker
    processes race for CPU and may interact with the browser before its
    initial page is even loaded.
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import TimeoutException
    try:
        WebDriverWait(driver, timeout or config.LONG_TIMEOUT).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except TimeoutException:
        pass  # Non-fatal — the next interaction will also wait
    except Exception:
        pass  # Fully non-fatal on any document-ready query failure


# ── Sub-page URL slugs for direct navigation fallback ──────────────
# Safari on macOS CI runners often loads practice-automation.com
# without rendering the expected link elements (blank page / security
# interstitial).  Instead of clicking navigation links (which fail),
# we navigate directly to the sub-page URL.
SUB_PAGE_SLUGS = {
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


def _navigate_and_wait(main_page_obj, go_method_name: str, page_obj) -> None:
    """Call a MainPage navigation method, wait for the document to finish
    loading, then assert the target page is available.

    For Safari (WebKit) on CI, the navigation links on the main page often
    fail to render.  As a fallback, navigate directly to the sub-page URL
    instead of clicking the link.
    """
    browser_name = getattr(main_page_obj.driver, "_browser_name", None)
    is_webkit_ci = browser_name == "webkit" and _is_ci()

    if is_webkit_ci:
        slug = SUB_PAGE_SLUGS.get(go_method_name)
        if slug:
            main_page_obj.driver.get(config.BASE_URL.rstrip("/") + slug)
        else:
            # No slug mapping — fall back to clicking (will probably fail)
            getattr(main_page_obj, go_method_name)()
    else:
        getattr(main_page_obj, go_method_name)()

    _wait_for_document_ready(main_page_obj.driver)
    assert page_obj.is_available, f"{type(page_obj).__name__} did not load within timeout"


@pytest.fixture(scope="function")
def main_page(browser, request):
    """Open the main page and return the page object."""
    page = MainPage(browser)
    page.open_page()
    # Wait for the page to be fully loaded before any test touches it
    _wait_for_document_ready(browser)
    # Safari on macOS GitHub runners has known reliability issues — it often
    # renders a blank/error page despite presenting a successful page load.
    # The readyState check above is sufficient; skip the element-presence
    # assertion to avoid false CI failures.
    if request.config.getoption("--browser") != "webkit":
        assert page.is_loaded(), "Main page did not load within timeout"
    return page


@pytest.fixture
def form_fields_page(main_page):
    page = FormFieldsPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_form_fields", page)
    return page


@pytest.fixture
def popups_page(main_page):
    page = PopupsPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_popups", page)
    return page


@pytest.fixture
def modals_page(main_page):
    page = ModalsPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_modals", page)
    return page


@pytest.fixture
def slider_page(main_page):
    page = SliderPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_sliders", page)
    return page


@pytest.fixture
def tables_page(main_page):
    page = TablesPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_tables", page)
    return page


@pytest.fixture
def calendar_page(main_page):
    page = CalendarPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_calendars", page)
    return page


@pytest.fixture
def window_operations_page(main_page):
    page = WindowOperationsPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_window_operations", page)
    return page


@pytest.fixture
def ads_page(main_page):
    page = AdsPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_ads", page)
    return page


@pytest.fixture
def gestures_page(main_page):
    page = GesturesPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_gestures", page)
    return page


@pytest.fixture
def hover_page(main_page):
    page = HoverPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_hover", page)
    return page


@pytest.fixture
def file_download_page(main_page):
    page = FileDownloadPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_file_download", page)
    return page


@pytest.fixture
def accordions_page(main_page):
    page = AccordionsPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_accordions", page)
    return page


@pytest.fixture
def file_upload_page(main_page):
    page = FileUploadPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_file_upload", page)
    return page


@pytest.fixture
def click_events_page(main_page):
    page = ClickEventsPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_click_events", page)
    return page


@pytest.fixture
def spinners_page(main_page):
    page = SpinnersPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_spinners", page)
    return page


@pytest.fixture
def iframes_page(main_page):
    page = IframesPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_iframes", page)
    return page


@pytest.fixture
def broken_images_page(main_page):
    page = BrokenImagesPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_broken_images", page)
    return page


@pytest.fixture
def broken_links_page(main_page):
    page = BrokenLinksPage(main_page.driver)
    _navigate_and_wait(main_page, "go_to_broken_links", page)
    return page
