import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .BasePage import BasePage


class ProductsPage(BasePage):
    ITEMS = (By.CSS_SELECTOR, '.productinfo')
    NAME = (By.CSS_SELECTOR, 'p')
    PRICE = (By.CSS_SELECTOR, 'h2')
    ADD = (By.CSS_SELECTOR, '.add-to-cart')
    CONTINUE = (By.CSS_SELECTOR, '#cartModal .close-modal')
    MODAL = (By.ID, 'cartModal')
    CART = (By.CSS_SELECTOR, '#cartModal a[href="/view_cart"]')

    @allure.step('Получение данных каталога')
    def products(self):
        return [dict(name=e.find_element(*self.NAME).text,
                     price=int(e.find_element(*self.PRICE).text.replace('Rs.', '').strip()))
                for e in self.find_elements(self.ITEMS)]

    @allure.step('Добавление товара {index}')
    def add_product(self, index=0):
        item = self.find_elements(self.ITEMS)[index]
        self.driver.execute_script('arguments[0].scrollIntoView({block:"center"})', item)
        item.find_element(*self.ADD).click()
        self.wait_for_element_visible(self.MODAL)
        return self

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
