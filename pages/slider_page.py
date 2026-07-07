from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from pages.base_page import BasePage


class SliderPage(BasePage):
    SLIDER = (By.ID, "slideMe")
    VALUE_DISPLAY = (By.ID, "value")

    @property
    def is_available(self) -> bool:
        return self.is_element_available(self.SLIDER)

    # ── Value helpers ─────────────────────────────────────────────

    def get_current_value_text(self) -> str:
        """Return the raw text from the value display <span>."""
        return self.find_element(self.VALUE_DISPLAY).text.strip()

    def set_value_via_js(self, value: int) -> None:
        """Set the slider value directly via JavaScript and fire the input event.

        Used for reliable edge-case testing (0 and 100). The JS setter
        triggers the same ``oninput`` handler that a real click or drag would.
        """
        slider = self.find_element(self.SLIDER)
        self.driver.execute_script(
            "arguments[0].value = arguments[1]; "
            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
            slider, str(value),
        )

    def get_current_value_int(self) -> int | None:
        """Return the current value as int, or None if the display is empty."""
        text = self.get_current_value_text()
        if text == "":
            return None
        try:
            return int(text)
        except ValueError:
            return None

    def get_slider_attribute_value(self) -> str | None:
        """Return the slider's HTML value attribute (raw)."""
        return self.find_element(self.SLIDER).get_attribute("value")

    def _ensure_slider_visible(self):
        """Scroll the slider into the viewport centre so that
        ActionChains mouse coordinates are computed correctly.

        Under parallel xdist load the element may be partially off-screen,
        causing Chromium to offset the click/drag coordinates.
        """
        slider = self.find_element(self.SLIDER)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            slider,
        )

    # ── Click on track ────────────────────────────────────────────

    def click_slider_at_percentage(self, pct: float) -> None:
        """Click on the slider track at a percentage position (0‑100).

        A click at 0% targets the far-left edge (expect value ≈ 0).
        A click at 100% targets the far-right edge (expect value ≈ 100).
        """
        self._ensure_slider_visible()
        slider = self.find_element(self.SLIDER)
        width = slider.size["width"]
        # Offset relative to element centre (Selenium convention)
        x_offset = int((pct / 100 - 0.5) * width)
        ActionChains(self.driver).move_to_element_with_offset(
            slider, x_offset, 0
        ).click().perform()

    # ── Drag (click-and-hold) ──────────────────────────────────────

    def drag_slider(self, start_pct: int, end_pct: int) -> None:
        """Move the slider thumb from start_pct% to end_pct% via drag.

        1. Scroll the slider into view.
        2. Move the mouse to the given start percentage on the track.
        3. Press and hold (this snaps the thumb to that position).
        4. Drag to the end percentage.
        5. Release.
        """
        self._ensure_slider_visible()
        slider = self.find_element(self.SLIDER)
        width = slider.size["width"]
        start_x = int((start_pct / 100 - 0.5) * width)
        end_x = int((end_pct / 100 - 0.5) * width)
        move_x = end_x - start_x

        actions = ActionChains(self.driver)
        actions.move_to_element_with_offset(slider, start_x, 0)
        actions.click_and_hold()
        actions.move_by_offset(move_x, 0)
        actions.release()
        actions.perform()
