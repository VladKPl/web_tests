import allure
from selenium.webdriver.common.by import By
from .BasePage import BasePage


class MainPage(BasePage):
    # Элементы для навигации и проверок
    LOGO = (By.CSS_SELECTOR, ".logo img")
    SIGNUP_LOGIN_BTN = (By.CSS_SELECTOR, "a[href='/login']")
    CONTACT_US_BTN = (By.CSS_SELECTOR, "a[href='/contact_us']")
    SUBSCRIBE_EMAIL_INPUT = (By.ID, "susbscribe_email")
    SUBSCRIBE_BTN = (By.ID, "subscribe")
    SUCCESS_SUBSCRIBE_ALERT = (By.ID, "success-subscribe")
    LOGGED_AS = (By.XPATH, "//a[contains(text(), 'Logged in as')]")
    LOGOUT = (By.XPATH, "//a[contains(text(), 'Logout')]")
    DELETE_ACCOUNT = (By.XPATH, "//a[contains(text(), 'Delete Account')]")
    PRODUCTS_BUTTON = (By.CSS_SELECTOR, "a[href='/products']")
    SLIDER = (By.ID, "slider")
    FIRST_VIEW_PRODUCT_BTN = (By.XPATH, "(//a[contains(text(), 'View Product')])[1]")
    VIEW_CART = (By.XPATH, "//a[contains(text(), 'Cart')]")

    @allure.step("Открывает главную страницу")
    def open_main_page(self):
        """Открывает главную страницу в браузере."""
        self.open("/")
        return self

    @allure.step("Клик по кнопке Signup / Login в верхнем меню")
    def click_signup_login(self):
        """Кликает по кнопке Signup / Login и возвращает страницу LoginPage."""
        self.click(self.SIGNUP_LOGIN_BTN)
        from .LoginPage import LoginPage
        return LoginPage(self.driver, self.base_url).check_login_page_is_opened()

    @allure.step("Проверка отображения блока 'Logged in as'")
    def verify_logged_in_as(self):
        assert self.wait_for_element_visible(self.LOGGED_AS)
        return self

    @allure.step("Удаление аккаунта")
    def click_delete_account(self):
        self.click(self.DELETE_ACCOUNT)
        from .AccountDeletedPage import AccountDeletedPage
        return AccountDeletedPage(self.driver, self.base_url)

    @allure.step("Выход из системы (Logout)")
    def click_logout(self):
        self.click(self.LOGOUT)
        from .LoginPage import LoginPage
        return LoginPage(self.driver, self.base_url)

    @allure.step("Проверка отображения главной страницы")
    def verify_main_page_visible(self):
        assert self.find_element(self.SLIDER).is_displayed(), "Главная страница не отображается"
        return self

    @allure.step("Переход в раздел 'Products'")
    def click_products(self):
        self.find_element(self.PRODUCTS_BUTTON).click()
        from .ProductsPage import ProductsPage
        page = ProductsPage(self.driver, self.base_url)
        page.wait_for_element_visible(page.ITEMS)
        return page

    @allure.step("Нажатие 'View Product' у первого товара в списке")
    def click_first_view_product(self):
        self.find_element(self.FIRST_VIEW_PRODUCT_BTN).click()
        from .ProductDetailPage import ProductDetailPage
        return ProductDetailPage(self.driver, self.base_url)

    @allure.step("Переход в корзину через верхнее меню")
    def click_view_cart(self):
        self.find_element(self.VIEW_CART).click()
        from .CartPage import CartPage
        return CartPage(self.driver, self.base_url)
