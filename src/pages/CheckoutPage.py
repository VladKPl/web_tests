import allure
from selenium.webdriver.common.by import By
from .BasePage import BasePage
from .components import CartTableMixin


class CheckoutPage(BasePage, CartTableMixin):
    REVIEW = (By.XPATH, "//h2[normalize-space()='Review Your Order']")
    DELIVERY = (By.ID, 'address_delivery')
    INVOICE = (By.ID, 'address_invoice')
    COMMENT = (By.NAME, 'message')
    PLACE = (By.CSS_SELECTOR, 'a[href="/payment"]')

    @allure.step('Проверка адресов и заказа')
    def verify_address_and_order(self):
        assert self.get_element_text(self.REVIEW) == 'Review Your Order'
        for locator in (self.DELIVERY, self.INVOICE):
            text = self.get_element_text(locator)
            for value in ('Mr. Ivan Ivanov', 'QA', 'Main St 10', 'Suite 2', 'Toronto Ontario', '12345', 'Canada', '1234567'):
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
