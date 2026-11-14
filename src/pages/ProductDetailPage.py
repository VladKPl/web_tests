import allure
from selenium.webdriver.common.by import By
from .ProductsPage import ProductsPage


class ProductDetailPage(ProductsPage):
    INFO = (By.CSS_SELECTOR, '.product-information')
    QUANTITY = (By.ID, 'quantity')
    ADD_BUTTON = (By.CSS_SELECTOR, 'button.cart')
    TITLE = (By.CSS_SELECTOR, '.product-information h2')
    PRICE = (By.CSS_SELECTOR, '.product-information span span')

    def product(self):
        return dict(name=self.get_element_text(self.TITLE),
                    price=int(self.get_element_text(self.PRICE).replace('Rs.', '').strip()))

    @allure.step('Проверка карточки товара')
    def verify_product_detail_opened(self):
        self.wait_for_element_visible(self.INFO)
        return self

    @allure.step('Изменение количества на {quantity}')
    def set_quantity(self, quantity):
        self.enter_text(self.QUANTITY, str(quantity))
        return self

    @allure.step('Добавление товара в корзину')
    def add_to_cart(self):
        self.click(self.ADD_BUTTON)
        self.wait_for_element_visible(self.MODAL)
        return self
