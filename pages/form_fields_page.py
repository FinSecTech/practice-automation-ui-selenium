from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from pages.base_page import BasePage


class FormFieldsPage(BasePage):
    NAME_INPUT = (By.ID, "name-input")
    REQUIRED_INDICATOR = (By.CLASS_NAME, "red_txt")
    PASSWORD_INPUT = (By.XPATH, "//input[@type='password']")

    DRINK_WATER = (By.ID, "drink1")
    DRINK_MILK = (By.ID, "drink2")
    DRINK_COFFEE = (By.ID, "drink3")
    DRINK_WINE = (By.ID, "drink4")
    DRINK_CTRL_ALT_DELIGHT = (By.ID, "drink5")

    COLOR_RED = (By.ID, "color1")
    COLOR_BLUE = (By.ID, "color2")
    COLOR_YELLOW = (By.ID, "color3")
    COLOR_GREEN = (By.ID, "color4")
    COLOR_PINK = (By.ID, "color5")

    AUTOMATION_SELECT = (By.ID, "automation")
    EMAIL_INPUT = (By.ID, "email")
    MESSAGE_TEXTAREA = (By.ID, "message")
    SUBMIT_BUTTON = (By.ID, "submit-btn")

    @property
    def is_available(self) -> bool:
        return self.is_element_available(self.NAME_INPUT)

    def fill_name(self, name: str) -> None:
        el = self.find_element(self.NAME_INPUT)
        el.clear()
        el.send_keys(name)

    def get_name_value(self) -> str:
        return self.find_element(self.NAME_INPUT).get_attribute("value")

    def fill_password(self, password: str) -> None:
        el = self.find_element(self.PASSWORD_INPUT)
        el.clear()
        el.send_keys(password)

    def select_drink(self, drink_id: tuple) -> None:
        """Check a drink checkbox.

        Uses _safe_click (JS-fallback) to handle overlay interception
        that can occur for elements at the bottom of a long page,
        particularly in Chromium-based browsers (Edge, Opera).
        """
        checkbox = self.find_clickable(drink_id)
        if not checkbox.is_selected():
            self._safe_click(checkbox)

    def select_all_drinks(self) -> None:
        for locator in (
            self.DRINK_WATER,
            self.DRINK_MILK,
            self.DRINK_COFFEE,
            self.DRINK_WINE,
            self.DRINK_CTRL_ALT_DELIGHT,
        ):
            self.select_drink(locator)

    def select_color(self, color_id: tuple) -> None:
        """Select a color radio button.

        Uses _safe_click (JS-fallback) to handle overlay interception
        that can occur for elements at the bottom of a long page,
        particularly in Chromium-based browsers (Edge, Opera).
        """
        radio = self.find_clickable(color_id)
        if not radio.is_selected():
            self._safe_click(radio)

    def select_automation_option(self, value: str) -> None:
        select_el = self.find_element(self.AUTOMATION_SELECT)
        Select(select_el).select_by_value(value)

    def fill_email(self, email: str) -> None:
        el = self.find_element(self.EMAIL_INPUT)
        el.clear()
        el.send_keys(email)

    def fill_message(self, message: str) -> None:
        el = self.find_element(self.MESSAGE_TEXTAREA)
        el.clear()
        el.send_keys(message)

    def click_submit(self) -> None:
        """Click the Submit button.

        Uses _safe_click (JS-fallback) because the form submit button
        is at the bottom of a long page where overlays (ads, sticky
        headers) can intercept native clicks, especially in Edge/Opera.
        """
        self._safe_click(self.SUBMIT_BUTTON)

    def get_required_indicator_text(self) -> str:
        return self.find_element(self.REQUIRED_INDICATOR).text

    def is_required_indicator_visible(self) -> bool:
        return self.find_element(self.REQUIRED_INDICATOR).is_displayed()

    def get_page_body_text(self) -> str:
        from selenium.webdriver.common.by import By
        return self.driver.find_element(By.TAG_NAME, "body").text
