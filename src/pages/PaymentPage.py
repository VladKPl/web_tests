import allure
from selenium.webdriver.common.by import By
from .BasePage import BasePage


class PaymentPage(BasePage):
    FIELDS = {name: (By.NAME, name) for name in ('name_on_card', 'card_number', 'cvc', 'expiry_month', 'expiry_year')}
    PAY = (By.CSS_SELECTOR, '[data-qa="pay-button"]')
    SUCCESS = (By.CSS_SELECTOR, '[data-qa="order-placed"]')
    CONFIRMATION = (By.CSS_SELECTOR, '#form p')

    @allure.step('Оплата демонстрационными данными')
    def pay(self):
        values = ('Test User', '4111111111111111', '123', '12', '2030')
        for locator, value in zip(self.FIELDS.values(), values):
            self.enter_text(locator, value)
        self.click(self.PAY)
        assert 'ORDER PLACED!' in self.get_element_text(self.SUCCESS)
        assert self.get_element_text(self.CONFIRMATION) == 'Congratulations! Your order has been confirmed!'
        from .MainPage import MainPage
        return MainPage(self.driver, self.base_url)
