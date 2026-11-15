import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CartModalMixin:
    CONTINUE = (By.CSS_SELECTOR, '#cartModal .close-modal')
    MODAL = (By.ID, 'cartModal')
    CART = (By.CSS_SELECTOR, '#cartModal a[href="/view_cart"]')

    @allure.step('Продолжение покупок')
    def click_continue_shopping(self):
        self.click(self.CONTINUE)
        WebDriverWait(self.driver, self.timeout).until(EC.invisibility_of_element_located(self.MODAL))
        return self

    @allure.step('Просмотр корзины')
    def click_view_cart(self):
        self.click(self.CART)
        from .CartPage import CartPage
        return CartPage(self.driver, self.base_url).verify_cart_page_displayed()


class CartTableMixin:
    ROWS = (By.CSS_SELECTOR, 'tr[id^="product-"]')
    NAME = (By.CSS_SELECTOR, '.cart_description h4')
    PRICE = (By.CSS_SELECTOR, '.cart_price p')
    QUANTITY = (By.CSS_SELECTOR, '.cart_quantity button')
    TOTAL = (By.CSS_SELECTOR, '.cart_total_price')

    @allure.step('Получение содержимого корзины')
    def items(self):
        def money(text):
            return int(text.replace('Rs.', '').strip())
        return [dict(name=e.find_element(*self.NAME).text,
                     price=money(e.find_element(*self.PRICE).text),
                     quantity=int(e.find_element(*self.QUANTITY).text),
                     total=money(e.find_element(*self.TOTAL).text))
                for e in self.find_elements(self.ROWS)]
