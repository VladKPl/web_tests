import allure
from selenium.webdriver.common.by import By
from .CartPage import CartPage


class CheckoutPage(CartPage):
    DELIVERY = (By.ID, 'address_delivery')
    INVOICE = (By.ID, 'address_invoice')
    COMMENT = (By.NAME, 'message')
    PLACE = (By.CSS_SELECTOR, 'a[href="/payment"]')

    @allure.step('Проверка адресов и заказа')
    def verify_address_and_order(self):
        for locator in (self.DELIVERY, self.INVOICE):
            text = self.get_element_text(locator)
            for value in ('Ivan Ivanov', 'Main St 10', 'Toronto Ontario', '12345', 'Canada'):
                assert value in text
        assert self.items()
        return self

    @allure.step('Переход к оплате')
    def place_order(self, comment='Test order'):
        self.enter_text(self.COMMENT, comment)
        self.click(self.PLACE)
        from .PaymentPage import PaymentPage
        page = PaymentPage(self.driver, self.base_url)
        page.wait_for_element_visible(page.PAY)
        return page
