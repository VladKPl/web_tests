import allure
from contextlib import nullcontext
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .BasePage import BasePage


class SignupPage(BasePage):
    NAME = (By.ID, 'name')

    @allure.step('Проверка сохранения имени в форме')
    def verify_name(self, expected):
        assert self.get_attribute(self.NAME, 'value') == expected
        return self

    PASSWORD = (By.ID, 'password')
    TITLE = (By.ID, 'id_gender1')
    TITLE_MRS = (By.ID, 'id_gender2')
    DAYS = (By.ID, 'days')
    MONTHS = (By.ID, 'months')
    YEARS = (By.ID, 'years')
    COUNTRY = (By.ID, 'country')
    NEWSLETTER = (By.ID, 'newsletter')
    OPTIN = (By.ID, 'optin')
    CREATE = (By.CSS_SELECTOR, '[data-qa="create-account"]')
    ADDRESS_FIELDS = {key: (By.ID, key) for key in (
        'first_name', 'last_name', 'company', 'address1', 'address2',
        'state', 'city', 'zipcode', 'mobile_number')}

    @allure.step('Обязательные поля полной формы не принимают пустые значения')
    def verify_required_fields(self):
        for locator in (self.PASSWORD, *[v for k, v in self.ADDRESS_FIELDS.items() if k not in ('company', 'address2')]):
            field = self.find_element(locator)
            assert field.get_attribute('required') == 'true'
            assert not self.execute_script('return arguments[0].checkValidity()', field)
            assert field.get_attribute('validationMessage')
        self.click(self.CREATE)
        self.wait_for_url_contains('/signup')
        self.wait_for_element_visible(self.PASSWORD)
        return self

    def register_user(self, user):
        # Context step deliberately excludes password and user arguments.
        with allure.step('Заполнение формы и создание аккаунта'):
            self.click(self.TITLE_MRS if user.get('title') == 'Mrs' else self.TITLE)
            self.enter_text(self.PASSWORD, user['password'])
            for locator, value in ((self.DAYS, '15'), (self.MONTHS, '5'), (self.YEARS, '1995')):
                self.select_by_value(locator, value)
            self.click(self.NEWSLETTER)
            self.click(self.OPTIN)
            values = dict(first_name='Ivan', last_name='Ivanov', company='QA',
                          address1='Main St 10', address2='Suite 2', state='Ontario',
                          city='Toronto', zipcode='12345', mobile_number='1234567')
            values.update(user.get('address', {}))
            for key, locator in self.ADDRESS_FIELDS.items():
                self.enter_text(locator, values[key])
            Select(self.find_element(self.COUNTRY)).select_by_visible_text('Canada')
            self.driver.pending_account = user
            metrics = getattr(self.driver, 'metrics', None)
            with metrics.measure('registration_response') if metrics else nullcontext():
                self.click(self.CREATE)
                from .AccountCreatedPage import AccountCreatedPage
                return AccountCreatedPage(self.driver, self.base_url).verify_created_msg()
