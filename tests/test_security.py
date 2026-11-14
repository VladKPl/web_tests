import allure
import pytest
from src.pages.MainPage import MainPage

pytestmark = pytest.mark.security


@pytest.mark.parametrize('name,email', [('', 'qa@example.com'), ('QA', ''), ('QA', 'testexample.com'), ('QA', 'test@')])
@allure.title('Обязательные поля и формат email')
def test_registration_validation(driver, base_url, name, email):
    MainPage(driver, base_url).open_main_page().click_signup_login().verify_invalid_signup(name, email)


@allure.title('Пароль скрыт в форме регистрации')
def test_password_field(driver, base_url, unique_user):
    page = MainPage(driver, base_url).open_main_page().click_signup_login().signup_with_credentials('QA', unique_user['email'])
    assert page.get_attribute(page.PASSWORD, 'type') == 'password'
    assert page.get_attribute(page.PASSWORD, 'required') == 'true'
    page.verify_required_fields()


@pytest.mark.parametrize('name', ["Anne O'Neil-Smith", 'A', 'A' * 100])
@allure.title('Допустимые символы и длина имени сохраняются')
def test_name_roundtrip(driver, base_url, unique_user, name):
    MainPage(driver, base_url).open_main_page().click_signup_login().signup_with_credentials(name, unique_user['email']).verify_name(name)
