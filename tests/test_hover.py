"""Tests for the Hover page.

Verifies the hover interaction on the ``<h3 id="mouse_over">`` element:
- Initial text is *"Mouse over me"* with default color.
- On hover (mouse over), text changes to *"You did it!"* and turns green.
- On mouse out, text reverts to *"Mouse over me"* with black color.
"""

from pages.hover_page import HoverPage


class TestHover:
    """Test suite for the Hover page."""

    def test_hover_changes_text_and_color(self, hover_page: HoverPage):
        """Hover over the element and verify the text and color change.

        Expectations:
        - Initially, the element shows *"Mouse over me"* and color is blue
          (default link colour, rgba(0, 170, 239, 1)).
        - After hovering, text changes to *"You did it!"* and color to
          green (rgba(0, 128, 0, 1) — ``color: green`` in CSS).
        - After the mouse leaves, text reverts to *"Mouse over me"* and
          color to black.
        """
        page = hover_page

        # ── 1. Initial state ─────────────────────────────────────
        assert page.mouse_over_text == page.DEFAULT_TEXT, (
            f"Expected default text '{page.DEFAULT_TEXT}', "
            f"got '{page.mouse_over_text}'"
        )
        # The default colour is the link blue from the site theme
        initial_color = page.mouse_over_color
        assert initial_color is not None

        # ── 2. Hover ─────────────────────────────────────────────
        page.hover_over_element()

        assert page.is_text_changed_to_hover(), (
            f"Expected text to change to '{page.HOVER_TEXT}' on hover, "
            f"but got '{page.mouse_over_text}'"
        )
        # Firefox returns rgb(), Chrome returns rgba() — accept both
        assert "0, 128, 0" in page.mouse_over_color, (
            f"Expected green color on hover (rgb/rgba containing '0, 128, 0'), "
            f"got {page.mouse_over_color}"
        )

        # ── 3. Move away (mouse out) ─────────────────────────────
        page.move_mouse_away()

        assert page.is_text_reverted(), (
            f"Expected text to revert to '{page.DEFAULT_TEXT}' after mouse out, "
            f"but got '{page.mouse_over_text}'"
        )

    def test_hover_text_content_on_hover(self, hover_page: HoverPage):
        """Directly verify the text content of the element after hover.

        A focused check that the JavaScript ``onmouseover`` handler set the
        inner HTML precisely to *"You did it!"*.
        """
        page = hover_page

        page.hover_over_element()

        assert page.is_text_changed_to_hover(), (
            f"Hover did not change text. "
            f"Expected '{page.HOVER_TEXT}', got '{page.mouse_over_text}'"
        )
