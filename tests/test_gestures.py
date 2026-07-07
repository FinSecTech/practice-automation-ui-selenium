"""
Tests for the Gestures page (https://practice-automation.com/gestures/).

Verifies three drag & drop exercises:
  1. Draggable box (#moveMe)  — ActionChains-based drag
  2. HTML5 Drag & Drop image  — JS DragEvent dispatch (ActionChains
     cannot complete the HTML5 DnD drop lifecycle because the browser
     blocks synthetic mouse events from triggering native ``drop``)
  3. Apple MapKit map panning  — ActionChains-based drag
"""


# ═══════════════════════════════════════════════════════════════
# 1. Draggable box (#moveMe)
# ═══════════════════════════════════════════════════════════════


def test_move_me_drag_changes_position(gestures_page):
    """Dragging #moveMe by an offset updates its inline top/left style.

    The box starts with no inline style, so ``get_move_me_position()``
    returns (0, 0) before the drag.  After the drag the inline style
    is populated with the offset applied from the original layout
    position.
    """
    pos_before = gestures_page.get_move_me_position()
    assert pos_before["top"] == 0 and pos_before["left"] == 0, (
        "Box should have no inline position initially"
    )

    gestures_page.drag_move_me_by_offset(120, 60)

    pos_after = gestures_page.get_move_me_position()
    assert pos_after["top"] > 0 and pos_after["left"] > 0, (
        f"Inline position should be set after drag, got top={pos_after['top']} left={pos_after['left']}"
    )


# ═══════════════════════════════════════════════════════════════
# 2. HTML5 Drag & Drop image (#dragMe → div1 → div2)
# ═══════════════════════════════════════════════════════════════


def test_image_starts_in_div1(gestures_page):
    """The draggable image should initially be inside #div1."""
    assert gestures_page.is_image_in_div1(), (
        "Image should start inside div1"
    )
    assert not gestures_page.is_image_in_div2(), (
        "Image should not be in div2 initially"
    )


def test_image_drag_to_div2(gestures_page):
    """Dragging the image to #div2 moves it via the HTML5 DnD API.

    Uses JavaScript DragEvent dispatch because ActionChains cannot
    complete the HTML5 DnD lifecycle (the ``drop`` event is never
    fired by synthetic mouse actions — a browser security constraint).
    """
    assert gestures_page.is_image_in_div1(), (
        "Precondition: image in div1"
    )

    gestures_page.html5_drag_image_to_div2()

    assert gestures_page.is_image_in_div2(), (
        "Image should have moved to div2 after drag & drop"
    )


# ═══════════════════════════════════════════════════════════════
# 3. Apple MapKit Map panning
# ═══════════════════════════════════════════════════════════════


def test_map_pan(gestures_page):
    """Panning the map via click-and-hold + drag should not throw.
    
    Pan horizontally only — vertical pan may push the pointer beyond
    the viewport bottom when the map is near the page footer.
    """
    gestures_page.pan_map(-100, 0)
