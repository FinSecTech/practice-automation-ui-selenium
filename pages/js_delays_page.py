from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class JsDelaysPage(BasePage):
    START_BUTTON = (By.ID, "start")
    DELAY_ELEMENT = (By.ID, "delay")

    @property
    def is_available(self) -> bool:
        return self.is_element_available(self.START_BUTTON)

    def click_start(self):
        button = self.find_clickable(self.START_BUTTON)
        button.click()

    def wait_for_liftoff(self) -> bool:
        return self.wait_for_text_present(self.DELAY_ELEMENT, "Liftoff!")
