import allure
from selenium.webdriver.common.by import By
from .BasePage import BasePage


class LoginPage(BasePage):
    @allure.step('Проверка отклонения некорректных регистрационных данных')
    def verify_invalid_signup(self, name, email):
        self.enter_text(self.SIGNUP_NAME_INPUT, name)
        self.enter_text(self.SIGNUP_EMAIL_INPUT, email)
        self.click(self.SIGNUP_BUTTON)
        field = self.find_element(self.SIGNUP_NAME_INPUT if not name else self.SIGNUP_EMAIL_INPUT)
        assert not self.execute_script('return arguments[0].checkValidity()', field)
        assert field.get_attribute('validationMessage')
        return self.check_login_page_is_opened()

    # Элементы на странице логина/регистрации
    LOGIN_HEADER = (By.CSS_SELECTOR, ".login-form h2")
    SIGNUP_HEADER = (By.CSS_SELECTOR, ".signup-form h2")

    # Элементы для формы LOGIN
    LOGIN_EMAIL_INPUT = (By.CSS_SELECTOR, "[data-qa='login-email']")
    LOGIN_PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-qa='login-password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "[data-qa='login-button']")

    # Элементы для формы SIGN UP
    SIGNUP_NAME_INPUT = (By.CSS_SELECTOR, "[data-qa='signup-name']")
    SIGNUP_EMAIL_INPUT = (By.CSS_SELECTOR, "[data-qa='signup-email']")
    SIGNUP_BUTTON = (By.CSS_SELECTOR, "[data-qa='signup-button']")
    WRONG_CREDS = (By.XPATH, "//*[text()='Your email or password is incorrect!']")
    WRONG_EMAIL = (By.XPATH, "//*[text()='Email Address already exist!']")

    @allure.step("Проверка страницы логина/регистрации")
    def check_login_page_is_opened(self):
        """Проверяет, что страница логина/регистрации открылась."""
        assert "login" in self.get_current_url(), "URL не соответствует странице логина"
        assert self.wait_for_element_visible(self.LOGIN_HEADER).is_displayed(), "Форма логина не найдена"
        assert self.wait_for_element_visible(self.SIGNUP_HEADER).is_displayed(), "Форма регистрации не найдена"
        return self

    def login_with_credentials(self, email, password, wrong=False):
        """Вводит данные пользователя и выполняет вход."""
        # Явно ждем загрузку страницы, чтобы поля были кликабельны
        self.enter_text(self.LOGIN_EMAIL_INPUT, email)
        self.enter_text(self.LOGIN_PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

        if wrong:
            return self.verify_login_error()
        from .MainPage import MainPage
        return MainPage(self.driver, self.base_url).verify_logged_in_as()

    @allure.step("Регистрация пользователя с именем '{name}' и email '{email}'")
    def signup_with_credentials(self, name, email, wrong=False):
        """Вводит данные пользователя (имя и email) и начинает регистрацию."""
        self.enter_text(self.SIGNUP_NAME_INPUT, name)
        self.enter_text(self.SIGNUP_EMAIL_INPUT, email)
        self.click(self.SIGNUP_BUTTON)

        if wrong:
            return self.verify_signup_error()
        from .SignupPage import SignupPage
        page = SignupPage(self.driver, self.base_url)
        page.wait_for_element_visible(page.PASSWORD)
        return page

    @allure.step("Проверка отображения ошибки неверных учетных данных при входе")
    def verify_login_error(self):
        self.wait_for_element_visible(self.WRONG_CREDS)
        return self

    @allure.step("Проверка отображения ошибки существующего email при регистрации")
    def verify_signup_error(self):
        self.wait_for_element_visible(self.WRONG_EMAIL)
        return self
