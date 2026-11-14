import allure
from selenium.webdriver.common.by import By
from .BasePage import BasePage


class CartPage(BasePage):
    INFO = (By.ID, 'cart_info')
    ROWS = (By.CSS_SELECTOR, 'tr[id^="product-"]')
    NAME = (By.CSS_SELECTOR, '.cart_description h4')
    PRICE = (By.CSS_SELECTOR, '.cart_price p')
    QUANTITY = (By.CSS_SELECTOR, '.cart_quantity button')
    TOTAL = (By.CSS_SELECTOR, '.cart_total_price')
    CHECKOUT = (By.CSS_SELECTOR, '.check_out')
    REGISTER = (By.CSS_SELECTOR, '#checkoutModal a[href="/login"]')
    DELETE = (By.CSS_SELECTOR, '.cart_quantity_delete')
    PRODUCTS = (By.CSS_SELECTOR, 'a[href="/products"]')

    @allure.step('Удаление товара из корзины')
    def remove_product(self, index=0):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        row = self.find_elements(self.ROWS)[index]
        row.find_element(*self.DELETE).click()
        WebDriverWait(self.driver, self.timeout).until(EC.staleness_of(row))
        return self

    @allure.step('Возврат к покупкам')
    def continue_shopping(self):
        self.click(self.PRODUCTS)
        from .ProductsPage import ProductsPage
        page = ProductsPage(self.driver, self.base_url)
        page.wait_for_element_visible(page.ITEMS)
        return page

    @allure.step('Регистрация при оформлении')
    def register_at_checkout(self):
        self.click(self.CHECKOUT)
        self.click(self.REGISTER)
        from .LoginPage import LoginPage
        return LoginPage(self.driver, self.base_url).check_login_page_is_opened()

    @allure.step('Оформление заказа')
    def checkout(self):
        self.click(self.CHECKOUT)
        from .CheckoutPage import CheckoutPage
        return CheckoutPage(self.driver, self.base_url).verify_address_and_order()

    @allure.step('Проверка страницы корзины')
    def verify_cart_page_displayed(self):
        self.wait_for_element_visible(self.INFO)
        return self

    @allure.step('Получение содержимого корзины')
    def items(self):
        def money(text):
            return int(text.replace('Rs.', '').strip())
        return [dict(name=e.find_element(*self.NAME).text,
                     price=money(e.find_element(*self.PRICE).text),
                     quantity=int(e.find_element(*self.QUANTITY).text),
                     total=money(e.find_element(*self.TOTAL).text))
                for e in self.find_elements(self.ROWS)]
