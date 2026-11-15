import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from .BasePage import BasePage
from .components import CartModalMixin
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException


class ProductsPage(BasePage, CartModalMixin):
    ITEMS = (By.CSS_SELECTOR, '.productinfo')
    CARDS = (By.CSS_SELECTOR, '.single-products')
    NAME = (By.CSS_SELECTOR, 'p')
    PRICE = (By.CSS_SELECTOR, 'h2')
    ADD = (By.CSS_SELECTOR, '.add-to-cart')
    DETAILS = (By.CSS_SELECTOR, '.choose a[href^="/product_details/"]')

    @allure.step('Открытие каталога')
    def open_catalog(self):
        self.open('/products')
        self.wait_for_element_visible(self.ITEMS)
        return self

    @allure.step('Открытие карточки товара')
    def open_product(self, index=0):
        self.click((By.XPATH, "(//div[contains(@class,'choose')]//a[contains(@href,'/product_details/')])[" + str(index + 1) + "]"))
        from .ProductDetailPage import ProductDetailPage
        return ProductDetailPage(self.driver, self.base_url).verify_product_detail_opened()

    @allure.step('Получение данных каталога')
    def products(self):
        return [dict(name=e.find_element(*self.NAME).get_attribute('textContent').strip(),
                     price=int(e.find_element(*self.PRICE).get_attribute('textContent').replace('Rs.', '').strip()))
                for e in self.find_elements(self.ITEMS)]

    @allure.step('Добавление товара {index}')
    def add_product(self, index=0):
        product_id = self.find_elements(self.CARDS)[index].find_element(*self.ADD).get_attribute('data-product-id')
        card_locator = (By.XPATH, "//div[contains(@class,'single-products')][.//a[@data-product-id='" + product_id + "']]")
        button_locator = (By.CSS_SELECTOR, ".single-products .product-overlay a[data-product-id='" + product_id + "']")

        def hover_and_press(driver):
            try:
                if any(e.is_displayed() for e in driver.find_elements(*self.CONSENT_OVERLAY)):
                    self.dismiss_consent()
                card = driver.find_element(*card_locator)
                driver.execute_script('arguments[0].scrollIntoView({block:"center"})', card)
                ActionChains(driver).move_to_element(card).perform()
                button = EC.element_to_be_clickable(button_locator)(driver)
                if not button:
                    return False
                accessible = driver.execute_script(
                    'const e=arguments[0],r=e.getBoundingClientRect();'
                    'const hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);'
                    'return r.width>0 && r.height>0 && (hit===e || e.contains(hit));', button)
                if not accessible:
                    return False
                button.click()
                return True
            except (StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException):
                return False

        WebDriverWait(self.driver, self.timeout).until(hover_and_press,
            message=f'Add to cart unavailable for product {product_id}')
        self.wait_for_element_visible(self.MODAL)
        return self
