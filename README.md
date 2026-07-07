# Practice Automation Test Framework

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-43B02A?logo=selenium)](https://selenium.dev/)
[![pytest](https://img.shields.io/badge/pytest-9.0+-0A9EDC?logo=pytest)](https://docs.pytest.org/)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Cross-browser UI test framework for **[practice-automation.com](https://practice-automation.com/)** — a demo site with interactive elements for practising web automation. Built with **Selenium + pytest + pytest-xdist** for parallel cross-browser regression detection.

146 test cases · 4 browsers · 20 page objects · 7 bug reports · 1 UX flaw report · Functional pass rate: 93.8% (137/146) · 9 expected failures (all bug-confirmed)

---

## ☕ Support the Project

If this project saves you time or helps you learn, consider tossing a coin my way. I expect donations of a **random value somewhere between your minimum and your maximum** — no pressure, no expectations, just good karma. 😊

<table>
  <tr>
    <td align="center">
      <img src="references/bitcoin.png" width="140" alt="Bitcoin QR" /><br />
      <strong>Bitcoin</strong><br />
      <code>bc1qxh5fu8m7wufgnjsuccp85l7gnrd5udq4lux3x8</code>
    </td>
    <td align="center">
      <img src="references/ethereum.png" width="140" alt="Ethereum QR" /><br />
      <strong>Ethereum</strong><br />
      <code>0xed1b82d666058e984f2f7c71b75306d68314e426</code>
    </td>
    <td align="center">
      <img src="references/solana.png" width="140" alt="Solana QR" /><br />
      <strong>Solana</strong><br />
      <code>8hjdfPEGuA5tDKfgxsRnMw9QZrxEiMBttTHybcqYqTNL</code>
    </td>
  </tr>
</table>

---

## 📚 Bug & Flaw Reports

| Document                                                                                              | Type       | Area                                             | Status    |
| ----------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------ | --------- |
| [`bug-popup-maker-modals-unreachable.md`](references/bug-popup-maker-modals-unreachable.md)           | 🐞 Bug     | Popup Maker modals have no visible trigger       | Confirmed |
| [`bug_calendar_date_range.md`](references/bug_calendar_date_range.md)                                 | 🐞 Bug     | Date input accepts values outside 1926–2126      | Confirmed |
| [`bug_comma_as_decimal_separator.md`](references/bug_comma_as_decimal_separator.md)                   | 🐞 Bug     | Population column uses comma instead of dot      | Confirmed |
| [`bug_integer_instead_of_float_population.md`](references/bug_integer_instead_of_float_population.md) | 🐞 Bug     | Population column missing decimal places         | Confirmed |
| [`bug_outdated_source_data_comparison.md`](references/bug_outdated_source_data_comparison.md)         | 🐞 Bug     | Sortable Table data outdated vs worldometers     | Confirmed |
| [`bug_required_indicator_static.md`](references/bug_required_indicator_static.md)                     | 🐞 Bug     | Required indicator never disappears after typing | Confirmed |
| [`bug_special_chars_in_visible_text.md`](references/bug_special_chars_in_visible_text.md)             | 🐞 Bug     | Literal `#` character in radio button label      | Confirmed |
| [`sort_ux_flaw_ranking_column.md`](references/sort_ux_flaw_ranking_column.md)                         | ⚠️ UX Flaw | DataTables 2.x 3-state sort cycle on Rank column | Confirmed |

---

## 🧰 Tech Stack

| Tool                                                                       | Purpose                            |
| -------------------------------------------------------------------------- | ---------------------------------- |
| [Selenium](https://selenium.dev/)                                          | Web browser automation             |
| [pytest](https://docs.pytest.org/)                                         | Test runner & assertions           |
| [pytest-xdist](https://github.com/pytest-dev/pytest-xdist)                 | Parallel test execution            |
| [pytest-rerunfailures](https://github.com/pytest-dev/pytest-rerunfailures) | Flaky test auto-retry              |
| [pytest-html](https://github.com/pytest-dev/pytest-html)                   | HTML test reports                  |
| [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager)    | Automatic driver binary management |
| [GitHub Actions](https://github.com/features/actions)                      | CI/CD pipeline                     |

---

## 📁 Project Structure

```text
.
├── pages/                          # Page Object Models
│   ├── base_page.py                #   Shared WebDriver utilities
│   ├── main_page.py                #   Navigation hub
│   ├── accordions_page.py
│   ├── ads_page.py
│   ├── broken_images_page.py
│   ├── broken_links_page.py
│   ├── calendar_page.py
│   ├── click_events_page.py
│   ├── file_download_page.py
│   ├── file_upload_page.py
│   ├── form_fields_page.py
│   ├── gestures_page.py
│   ├── hover_page.py
│   ├── iframes_page.py
│   ├── js_delays_page.py
│   ├── modals_page.py
│   ├── popups_page.py
│   ├── slider_page.py
│   ├── spinners_page.py
│   ├── tables_page.py
│   └── window_operations_page.py
├── tests/                          # Test specs
│   ├── conftest.py                 #   Fixtures, browser setup, page navigation
│   ├── test_accordions.py
│   ├── test_ads.py
│   ├── test_broken_images.py
│   ├── test_broken_links.py
│   ├── test_calendars.py
│   ├── test_click_events.py
│   ├── test_file_download.py
│   ├── test_file_upload.py
│   ├── test_form_fields.py
│   ├── test_gestures.py
│   ├── test_hover.py
│   ├── test_iframes.py
│   ├── test_js_delays.py
│   ├── test_modals.py
│   ├── test_popups.py
│   ├── test_slider.py
│   ├── test_spinners.py
│   ├── test_tables.py
│   └── test_window_operations.py
├── references/                     # Bug reports & documentation
│   ├── bug-popup-maker-modals-unreachable.md
│   ├── bug_calendar_date_range.md
│   ├── bug_comma_as_decimal_separator.md
│   ├── bug_integer_instead_of_float_population.md
│   ├── bug_outdated_source_data_comparison.md
│   ├── bug_required_indicator_static.md
│   ├── bug_special_chars_in_visible_text.md
│   ├── sort_ux_flaw_ranking_column.md
│   ├── wallets.md
│   ├── bitcoin.png
│   ├── ethereum.png
│   └── solana.png
├── upload_test_data/               # Test files for upload tests
│   ├── test.txt
│   ├── test.docx
│   ├── test.pdf
│   ├── test.jpeg
│   ├── test.jpg
│   ├── test.png
│   └── test.gif
├── reports/                        # HTML test reports (gitignored)
├── config.py                       # Shared configuration
├── run_tests.py                    # Interactive cross-browser runner
├── pyproject.toml                  # Project metadata & pytest config
├── requirements.txt                # Python dependencies
└── .github/workflows/
    └── ci.yml                      # CI/CD pipeline
```

---

## 🎯 Coverage Map

| Page          | Tests | Features Covered                                                                                                                                                                                   |
| ------------- | :---: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Accordions    |   3   | Expand/collapse, initial state                                                                                                                                                                     |
| Ads           |   4   | Ad modal visibility, title, content, close                                                                                                                                                         |
| Broken Images |   6   | Image detection, natural dimensions, valid/invalid src, order                                                                                                                                      |
| Broken Links  |   7   | Link scraping, text/URL validation, 404 via browser, HTTP status, full scan                                                                                                                        |
| Calendars     |  28   | Direct date input (valid + out-of-range), interactive picker (months, years, navigation, boundary), cross-method validation, bug detection                                                         |
| Click Events  |   7   | Page load, initial empty demo text, 4 animal button clicks, click replacement                                                                                                                      |
| File Download |   6   | Normal download button & URL, locked download iframe, wrong/correct password, full unlock flow                                                                                                     |
| File Upload   |   8   | 7 supported file formats, unsupported file rejection                                                                                                                                               |
| Form Fields   |   8   | Input fill, checkboxes, radio buttons, dropdown, required-field validation, successful submission, 2 bug-detection tests                                                                           |
| Gestures      |   4   | ActionChains drag, HTML5 DnD JavaScript dispatch, map pan                                                                                                                                          |
| Hover         |   2   | Text change on hover, colour change, revert on mouse out                                                                                                                                           |
| Iframes       |   7   | Both iframes load, contain expected text, page titles, body text retrieval                                                                                                                         |
| JS Delays     |   1   | Async rendering after JS execution, liftoff detection                                                                                                                                              |
| Modals        |   5   | Hidden on load, simple modal open/close, form modal open/close, email validation, form fill & submit                                                                                               |
| Popups        |  10   | JS alert, confirm accept/dismiss, prompt with text/dismiss/empty, tooltip toggle, 3 modal bug-detection tests                                                                                      |
| Slider        |   9   | Initial value, click increment/decrement, JS-set boundaries, drag increment/decrement, drag boundaries                                                                                             |
| Spinners      |   4   | Page load, visible initially, class-based hide, invisibility wait                                                                                                                                  |
| Tables        |  24   | Simple table (heading, columns, format), sortable table (heading, source link, source-of-truth comparison, comma-bug, integer-bug, entries per page, 3-column sorting, pagination, 4 search tests) |
| Window Ops    |   3   | New tab, replace window (URL + back), new window                                                                                                                                                   |

---

## ⚙️ Prerequisites

- **Python** 3.12+
- **pip**
- One or more installed browsers: **Firefox**, **Edge**, **Opera**, or **Safari** (macOS only)
- webdriver-manager handles driver binary downloads automatically

---

## 🔧 Setup

### 1) Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

- **Windows:** `.venv\Scripts\activate`
- **macOS/Linux:** `source .venv/bin/activate`

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Verify

```bash
pytest tests/ --browser=firefox -n=2 --tb=short -x
```

---

## 🚀 Run Tests

### Interactive runner (recommended)

```bash
python run_tests.py
```

Presents a menu to select one or more browsers, then runs all tests in parallel across them.

### Direct pytest commands

```bash
# All tests, Firefox, 2 workers
pytest tests/ --browser=firefox -n=2

# Single test file
pytest tests/test_calendars.py --browser=firefox -n=2 -v

# Specific test with keyword filter
pytest tests/ --browser=edge -n=2 -k "test_sort"

# HTML report
pytest tests/ --browser=firefox -n=2 --html=reports/report.html --self-contained-html

# Single worker (no xdist, easier debugging)
pytest tests/test_form_fields.py --browser=firefox -n=0 -v -s
```

### Available browsers

| Flag                | Browser             | Auto-detected |
| ------------------- | ------------------- | :-----------: |
| `--browser=firefox` | Mozilla Firefox     |      ✅       |
| `--browser=edge`    | Microsoft Edge      |      ✅       |
| `--browser=opera`   | Opera (Chromium)    |      ✅       |
| `--browser=webkit`  | Safari (macOS only) |      ✅       |

---

## 🧪 Test Design

### Page Object Model

Each page is represented by a class in `pages/` that encapsulates:

- Locators (By tuples)
- Interaction methods (click, type, select, etc.)
- State queries (is_displayed, get_text, etc.)

```python
# Example: pages/slider_page.py
class SliderPage(BasePage):
    SLIDER = (By.ID, "slide")
    VALUE_DISPLAY = (By.ID, "value")

    def get_slider_value(self) -> str:
        return self.find_element(self.VALUE_DISPLAY).text
```

### Conftest fixtures

`tests/conftest.py` provides:

- Browser session management (session-scoped for Firefox/Edge/WebKit, function-scoped for Opera)
- Page navigation fixtures (`calendar_page`, `tables_page`, etc.)
- Parallel-safe document-ready waits

### Bug detection pattern

Tests for known bugs use explicit assertions that document the expected failure:

```python
def test_simple_modal_visible_on_page_load(popups_page):
    """BUG: Popup Maker Simple Modal has no trigger element."""
    assert popups_page.is_simple_modal_accessible(), (
        "FAILED AS PLANNED: Simple Modal is defined in the DOM but has no "
        "trigger element — the overlay stays hidden (display: none)."
    )
```

---

## 📊 Test Results Summary

### Cross-browser verification (July 2026)

| Browser | Tests | Passed | Failed | Bug-Confirmed Failures | Clean Passes |
| ------- | :---: | :----: | :----: | :--------------------: | :----------: |
| Firefox |  146  |  137   |   9    |          9/9           |   137/137    |
| Edge    |  146  |  137   |   9    |          9/9           |   137/137    |
| Opera   |  146  |  137   |   9    |          9/9           |   137/137    |

**All 9 failures are expected** — each corresponds to a documented bug in `references/`. Zero failures without a matching bug report.

### Bug → Test mapping

| Report                                                                                                | Failing Tests                                                                                                           |
| ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| [`bug-popup-maker-modals-unreachable.md`](references/bug-popup-maker-modals-unreachable.md)           | `test_simple_modal_visible_on_page_load`, `test_form_modal_visible_on_page_load`, `test_form_modal_fields_interactable` |
| [`bug_required_indicator_static.md`](references/bug_required_indicator_static.md)                     | `test_required_indicator_disappears_after_typing`                                                                       |
| [`bug_special_chars_in_visible_text.md`](references/bug_special_chars_in_visible_text.md)             | `test_no_special_chars_in_page_text`                                                                                    |
| [`bug_outdated_source_data_comparison.md`](references/bug_outdated_source_data_comparison.md)         | `TestSourceOfTruth::test_compare_column2_country`, `TestSourceOfTruth::test_compare_column3_population`                 |
| [`bug_comma_as_decimal_separator.md`](references/bug_comma_as_decimal_separator.md)                   | `TestCommaBug::test_comma_as_decimal_separator_bug`                                                                     |
| [`bug_integer_instead_of_float_population.md`](references/bug_integer_instead_of_float_population.md) | `TestIntegerBug::test_integer_not_float_bug`                                                                            |

### Reports without failing tests (by design)

- **`bug_calendar_date_range.md`** — All parametrized `test_direct_input_accepts_out_of_range` tests pass, confirming the bug exists (asserting the form accepts bad input).
- **`sort_ux_flaw_ranking_column.md`** — `test_sort_by_rank` was adapted in code (double-click pattern) and passes, documenting the UX flaw while verifying sorting still works.

---

## 🤖 CI/CD (GitHub Actions)

**Workflow:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

The CI pipeline runs the full test suite across **4 browsers** in parallel — Firefox, Edge, Opera (Linux), and WebKit/Safari (macOS) — publishing HTML dashboard reports with run history as build artifacts.

**Trigger:** push (all branches), pull requests, manual dispatch.

### Pipeline stages

1. **Setup** — checkout, Python 3.12, install dependencies (cached via pip)
2. **Test (Firefox)** — `pytest tests/ --browser=firefox -n=2` on `ubuntu-latest`
3. **Test (Edge)** — `pytest tests/ --browser=edge -n=2` on `ubuntu-latest`
4. **Test (Opera)** — `pytest tests/ --browser=opera -n=1` on `ubuntu-latest` (Opera installed via apt)
5. **Test (WebKit)** — `pytest tests/ --browser=webkit -n=2` on `macos-latest` (SafariDriver enabled)
6. **Report** — upload `reports/` directory per browser as workflow artifact (HTML dashboard with history)

---

## 🔍 Troubleshooting

| Problem                                         | Likely Cause                     | Fix                                                                          |
| ----------------------------------------------- | -------------------------------- | ---------------------------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'config'` | Running outside project root     | Run from the project root directory or use `python -m pytest`                |
| `WebDriverException`                            | Browser driver version mismatch  | `pip install --upgrade webdriver-manager`                                    |
| Tests hang on worldometers page                 | Network / rate limiting          | The source-of-truth test fetches 100 rows; retry or set `DEFAULT_TIMEOUT=30` |
| Opera session gets stuck                        | Opera/chromedriver compatibility | Opera uses a function-scoped fixture with auto-retry; just rerun             |

---

## 🏗 Design Principles

- **Page Object Model** — one class per page, encapsulating locators and interactions
- **Session-scoped drivers** — Firefox, Edge, and WebKit share one browser session across all tests for speed
- **Function-scoped Opera** — fresh session per test to avoid degradation under parallel load
- **No implicit waits** — explicit `WebDriverWait` with per-page timeouts
- **Self-healing drivers** — `webdriver-manager` auto-detects and downloads the correct driver binary
- **Known-bug tests are explicit** — failures clearly labelled as expected, with the bug report referenced in the assertion message
- **Parallel-safe** — `_wait_for_document_ready` guards against race conditions in xdist workers

---

## 📄 License

**MIT** — This project is licensed under the MIT License. See `LICENSE` for details.

---

_Built with ❤️ using Selenium & pytest — because the best QA framework is the one you can trust to tell you what's broken._
