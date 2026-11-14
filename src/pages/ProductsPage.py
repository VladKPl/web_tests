import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from .BasePage import BasePage


class ProductsPage(BasePage):
    ITEMS = (By.CSS_SELECTOR, '.productinfo')
    NAME = (By.CSS_SELECTOR, 'p')
    PRICE = (By.CSS_SELECTOR, 'h2')
    ADD = (By.CSS_SELECTOR, '.add-to-cart')
    OVERLAY_ADD = (By.CSS_SELECTOR, '.product-overlay .add-to-cart')
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
        ActionChains(self.driver).move_to_element(item).perform()
        wrapper = item.find_element(By.XPATH, '..')
        button = wrapper.find_element(*self.OVERLAY_ADD)
        WebDriverWait(self.driver, self.timeout).until(lambda _: self.driver.execute_script(
            'const e=arguments[0],r=e.getBoundingClientRect();'
            'const hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);'
            'return r.width>0 && r.height>0 && (hit===e || e.contains(hit));', button))
        button.click()
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
