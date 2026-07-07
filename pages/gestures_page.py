from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config


class GesturesPage:
    """Page object for the Gestures page (https://practice-automation.com/gestures/).

    Three drag & drop exercises:
      1. Draggable box (#moveMe) — ActionChains.drag_and_drop_by_offset
      2. HTML5 Drag & Drop image (#dragMe) — JS DragEvent dispatch
      3. Apple MapKit map panning — ActionChains.click_and_hold + move_by_offset
    """

    # ── Element 1: Draggable box ──────────────────────────────────
    MOVE_ME_BOX = (By.ID, "moveMe")
    MOVE_ME_HEADER = (By.ID, "moveMeHeader")

    # ── Element 2: HTML5 Drag & Drop ──────────────────────────────
    DIV1 = (By.ID, "div1")
    DIV2 = (By.ID, "div2")
    DRAG_ME = (By.ID, "dragMe")

    # ── Element 3: Apple MapKit Map ───────────────────────────────
    MAP_VIEW = (By.CSS_SELECTOR, ".mk-map-view")

    def __init__(self, driver):
        self.driver = driver

    # ── Locator helpers ───────────────────────────────────────────

    def _find(self, locator):
        wait = WebDriverWait(self.driver, config.DEFAULT_TIMEOUT)
        return wait.until(EC.presence_of_element_located(locator))

    @property
    def is_available(self) -> bool:
        try:
            self._find(self.MOVE_ME_BOX)
            return True
        except Exception:
            return False

    # ═══════════════════════════════════════════════════════════════
    # 1. Draggable box (#moveMe) — jQuery-based drag
    # ═══════════════════════════════════════════════════════════════

    def get_move_me_position(self) -> dict:
        """Return the current {'top', 'left'} of #moveMe as integers.

        Parses the inline ``style`` attribute (set by the JS drag handler).
        """
        el = self._find(self.MOVE_ME_BOX)
        style = el.get_attribute("style") or ""
        top = left = 0
        for part in style.split(";"):
            part = part.strip()
            if part.startswith("top:"):
                top = int(part.split(":")[1].strip().rstrip("px"))
            elif part.startswith("left:"):
                left = int(part.split(":")[1].strip().rstrip("px"))
        return {"top": top, "left": left}

    def drag_move_me_by_offset(self, offset_x: int, offset_y: int) -> None:
        """Drag #moveMe by the given pixel offset using ActionChains."""
        header = self._find(self.MOVE_ME_HEADER)
        actions = ActionChains(self.driver)
        actions.drag_and_drop_by_offset(header, offset_x, offset_y).perform()

    # ═══════════════════════════════════════════════════════════════
    # 2. HTML5 Drag & Drop image — JS DragEvent dispatch
    # ═══════════════════════════════════════════════════════════════

    def is_image_in_div1(self) -> bool:
        """Return True if #dragMe is a child of #div1."""
        drag_me = self._find(self.DRAG_ME)
        return drag_me.find_element(By.XPATH, "..").get_attribute("id") == "div1"

    def is_image_in_div2(self) -> bool:
        """Return True if #dragMe is a child of #div2."""
        drag_me = self._find(self.DRAG_ME)
        return drag_me.find_element(By.XPATH, "..").get_attribute("id") == "div2"

    def html5_drag_image_to_div2(self) -> None:
        """Simulate HTML5 drag & drop of #dragMe from #div1 to #div2.

        Dispatches dragstart, dragenter, dragover, drop, and dragend
        events with a proper ``DataTransfer`` so the page's ``drop()``
        handler appends the image into #div2.
        """
        source = self._find(self.DRAG_ME)
        target = self._find(self.DIV2)

        self.driver.execute_script(
            """
            var source = arguments[0];
            var target = arguments[1];

            var dt = new DataTransfer();
            dt.setData('text', source.id);

            source.dispatchEvent(new DragEvent('dragstart', {
                bubbles: true, cancelable: true, dataTransfer: dt
            }));
            target.dispatchEvent(new DragEvent('dragenter', {
                bubbles: true, cancelable: true, dataTransfer: dt
            }));
            target.dispatchEvent(new DragEvent('dragover', {
                bubbles: true, cancelable: true, dataTransfer: dt
            }));
            target.dispatchEvent(new DragEvent('drop', {
                bubbles: true, cancelable: true, dataTransfer: dt
            }));
            source.dispatchEvent(new DragEvent('dragend', {
                bubbles: true, cancelable: true, dataTransfer: dt
            }));
            """,
            source,
            target,
        )

    # ═══════════════════════════════════════════════════════════════
    # 3. Apple MapKit Map — ActionChains pan
    # ═══════════════════════════════════════════════════════════════

    def pan_map(self, offset_x: int, offset_y: int) -> None:
        """Pan the map by the given offset.

        The Apple MapKit map lives inside a Shadow DOM whose
        ``scrollIntoView`` does not scroll the main page.  We scroll
        the main page with ``window.scrollTo``, wait for the scroll
        to settle and the lazy-loaded tiles to render, then perform
        the drag via ``click_and_hold(el)`` directly (instead of
        separate ``move_to_element`` + ``click_and_hold()``) with
        intra-chain ``pause()`` ticks.

        ``ActionChains.pause()`` is **not** ``time.sleep()`` — it
        inserts a delay in milliseconds within Selenium's internal
        action queue (the browser's input tick system), keeping the
        test free of Python-level sleeps.

        Without this, under xdist parallel load the map tiles may
        still be 0×0 when the drag fires, or the coordinate captured
        by ``move_to_element`` may become stale before the chain
        executes.
        """
        wait = WebDriverWait(self.driver, config.DEFAULT_TIMEOUT)
        el = self._find(self.MAP_VIEW)

        # Wait for the map host to be rendered (non-zero dimensions).
        # Apple MapKit lazy-loads its tiles — the host element can be
        # present in the DOM but have 0×0 bounding rect.
        wait.until(
            lambda d: d.execute_script(
                "var r = arguments[0].getBoundingClientRect(); "
                "return r.width > 0 && r.height > 0;",
                el,
            )
        )

        # Scroll map into view so its center is well above the bottom
        # of the viewport, giving room to pan left without hitting
        # the page boundary.
        self.driver.execute_script(
            """
            var el = arguments[0];
            var rect = el.getBoundingClientRect();
            var absCenterY = rect.top + window.scrollY + rect.height / 2;
            window.scrollTo(0, absCenterY - 300);
            """,
            el,
        )

        # Wait for the scroll to settle AND the map centre to be in a
        # good position (non-zero size check repeated because the map
        # may have been mid-resize when we first checked).
        wait.until(
            lambda d: d.execute_script(
                "var r = arguments[0].getBoundingClientRect(); "
                "return r.top + r.height / 2 < window.innerHeight - 100 "
                "&& r.width > 0 && r.height > 0;",
                el,
            )
        )

        actions = ActionChains(self.driver)
        actions.click_and_hold(el)
        actions.pause(0.1)
        actions.move_by_offset(offset_x, offset_y)
        actions.pause(0.1)
        actions.release()
        actions.perform()
