import allure
from selenium.webdriver.common.by import By
from .BasePage import BasePage


class AccountCreatedPage(BasePage):
    HEADER = (By.CSS_SELECTOR, "[data-qa='account-created']")
    CONTINUE_BTN = (By.CSS_SELECTOR, "[data-qa='continue-button']")

    @allure.step("Проверка отображения сообщения об успешном создании аккаунта")
    def verify_created_msg(self):
        """Проверяет видимость и возвращает текст сообщения."""
        assert self.get_element_text(self.HEADER) == 'ACCOUNT CREATED!'
        return self

    @allure.step("Нажимаем кнопку 'Continue' на странице успешной регистрации")
    def click_continue(self):
        """Кликает по кнопке продолжения и возвращает экземпляр главной страницы."""
        self.click(self.CONTINUE_BTN)
        from .MainPage import MainPage
        return MainPage(self.driver, self.base_url).verify_main_page_visible()
