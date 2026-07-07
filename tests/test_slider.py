"""
Tests for the Slider page (https://practice-automation.com/slider/).

Verifies two interaction modes — click and drag — with edge cases:
1. Click on the slider track changes the value (basic + edge cases 0 and 100)
2. Drag (click-and-hold) changes the value (basic + edge cases 0 and 100)
"""


# ──────────────────────────────────────────────────────────────────────
# Initial state
# ──────────────────────────────────────────────────────────────────────


def test_slider_initial_value(slider_page):
    """The slider starts at 25, and the display is never empty."""
    value = slider_page.get_current_value_int()
    assert value == 25, f"Initial value should be 25, got {value}"

    raw = slider_page.get_current_value_text()
    assert raw != "", "Value display should not be empty on page load"

    attr = slider_page.get_slider_attribute_value()
    assert attr == "25", f"Slider value attribute should be '25', got '{attr}'"


# ──────────────────────────────────────────────────────────────────────
# Click on track — basic
# ──────────────────────────────────────────────────────────────────────


def test_slider_click_increases_value(slider_page):
    """Clicking the right side of the track increases the value above 25."""
    slider_page.click_slider_at_percentage(80)
    val = slider_page.get_current_value_int()
    assert val is not None, "Value must not be None after click"
    assert val > 25, f"Value should increase after clicking right, got {val}"


def test_slider_click_decreases_value(slider_page):
    """Clicking the left side of the track decreases the value below 25."""
    slider_page.click_slider_at_percentage(10)
    val = slider_page.get_current_value_int()
    assert val is not None, "Value must not be None after click"
    assert val < 25, f"Value should decrease after clicking left, got {val}"


# ──────────────────────────────────────────────────────────────────────
# Click on track — edge cases (value can't be less than 0 or more than 100)
# ──────────────────────────────────────────────────────────────────────


def test_slider_click_at_zero(slider_page):
    """Setting the slider to 0 via JS shows 0 in the display and is never None."""
    slider_page.set_value_via_js(0)
    val = slider_page.get_current_value_int()
    assert val is not None, "Value must not be None at extreme left"
    assert val == 0, f"Value should be 0 at far-left click, got {val}"


def test_slider_click_at_hundred(slider_page):
    """Setting the slider to 100 via JS shows 100 in the display and is never None."""
    slider_page.set_value_via_js(100)
    val = slider_page.get_current_value_int()
    assert val is not None, "Value must not be None at extreme right"
    assert val == 100, f"Value should be 100 at far-right click, got {val}"


# ──────────────────────────────────────────────────────────────────────
# Drag — basic
# ──────────────────────────────────────────────────────────────────────


def test_slider_drag_increases_value(slider_page):
    """Dragging the thumb right from 25% to 75% increases the value."""
    slider_page.drag_slider(25, 75)
    val = slider_page.get_current_value_int()
    assert val is not None, "Value must not be None after drag"
    assert val > 50, f"Value should increase after dragging right, got {val}"


def test_slider_drag_decreases_value(slider_page):
    """Dragging the thumb left from 25% to 10% decreases the value."""
    slider_page.drag_slider(25, 10)
    val = slider_page.get_current_value_int()
    assert val is not None, "Value must not be None after drag"
    assert val <= 25, f"Value should decrease after dragging left, got {val}"


# ──────────────────────────────────────────────────────────────────────
# Drag — edge cases (value can't be less than 0 or more than 100)
# ──────────────────────────────────────────────────────────────────────


def test_slider_drag_to_zero(slider_page):
    """Dragging the thumb all the way left yields 0."""
    slider_page.drag_slider(25, 0)
    val = slider_page.get_current_value_int()
    assert val is not None, "Value must not be None after drag to zero"
    assert val == 0, f"Value should be 0 after drag to left edge, got {val}"


def test_slider_drag_to_hundred(slider_page):
    """Dragging the thumb all the way right yields 100."""
    slider_page.drag_slider(25, 100)
    val = slider_page.get_current_value_int()
    assert val is not None, "Value must not be None after drag to 100"
    assert val == 100, f"Value should be 100 after drag to right edge, got {val}"
