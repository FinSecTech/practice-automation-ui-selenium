from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class ClickEventsPage(BasePage):
    CAT_BUTTON = (By.XPATH, "//button[@class='custom_btn btn_hover' and contains(., 'Cat')]")
    DOG_BUTTON = (By.XPATH, "//button[@class='custom_btn btn_hover' and contains(., 'Dog')]")
    PIG_BUTTON = (By.XPATH, "//button[@class='custom_btn btn_hover' and contains(., 'Pig')]")
    COW_BUTTON = (By.XPATH, "//button[@class='custom_btn btn_hover' and contains(., 'Cow')]")
    DEMO_TEXT = (By.ID, "demo")

    _ANIMAL_LOCATORS = {
        "cat": CAT_BUTTON,
        "dog": DOG_BUTTON,
        "pig": PIG_BUTTON,
        "cow": COW_BUTTON,
    }

    @property
    def is_available(self) -> bool:
        return self.is_element_available(self.DEMO_TEXT)

    @property
    def demo_text(self) -> str:
        return self.find_element(self.DEMO_TEXT).text.strip()

    def click_animal(self, animal: str) -> str:
        """Click an animal button and return the demo text."""
        self.find_clickable(self._ANIMAL_LOCATORS[animal]).click()
        return self.demo_text
