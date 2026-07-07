from pages.js_delays_page import JsDelaysPage


def test_js_delays(main_page):
    """Navigate to JavaScript Delays via the main page and verify liftoff."""
    main_page.go_to_js_delays()

    # The JsDelays page object checks that its elements are available
    js_delays = JsDelaysPage(main_page.driver)
    js_delays.click_start()

    liftoff = js_delays.wait_for_liftoff()

    assert liftoff
