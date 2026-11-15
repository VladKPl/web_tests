import allure
from selenium.webdriver.common.by import By
from .BasePage import BasePage


class AccountDeletedPage(BasePage):
    HEADER = (By.CSS_SELECTOR, "[data-qa='account-deleted']")
    CONTINUE_BTN = (By.CSS_SELECTOR, "[data-qa='continue-button']")

    @allure.step("Проверка отображения сообщения об успешном удалении аккаунта")
    def verify_deleted_msg(self):
        """Проверяет видимость и возвращает сообщение."""
        assert self.get_element_text(self.HEADER) == 'ACCOUNT DELETED!'
        self.driver.pending_account = None
        return self

    @allure.step("Нажимаем кнопку 'Continue' на странице удаления аккаунта")
    def click_continue(self):
        """Кликает по кнопке продолжения и возвращает экземпляр главной страницы."""
        self.click(self.CONTINUE_BTN)
        from .MainPage import MainPage
        return MainPage(self.driver, self.base_url).verify_main_page_visible()
