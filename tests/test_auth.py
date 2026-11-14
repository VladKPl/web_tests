import allure
import pytest
from src.pages.MainPage import MainPage

pytestmark = [pytest.mark.auth, pytest.mark.regression]


@pytest.fixture
def account(driver, base_url, unique_user):
    home = MainPage(driver, base_url).open_main_page()
    home.click_signup_login().signup_with_credentials(unique_user['name'], unique_user['email']).register_user(unique_user).click_continue().verify_logged_in_as()
    yield unique_user
    home.open_main_page()
    if not driver.find_elements(*home.LOGGED_AS):
        home.click_signup_login().login_with_credentials(unique_user['email'], unique_user['password'])
    home.click_delete_account().verify_deleted_msg().click_continue()


@allure.title('TC1: Регистрация пользователя')
def test_01_register(driver, base_url, account):
    home = MainPage(driver, base_url).verify_logged_in_as()
    assert account['name'] in home.get_element_text(home.LOGGED_AS)


@allure.title('TC2: Вход с правильными данными')
def test_02_login(driver, base_url, account):
    home = MainPage(driver, base_url)
    home.click_logout().check_login_page_is_opened().login_with_credentials(account['email'], account['password']).verify_logged_in_as().click_logout().check_login_page_is_opened()


@allure.title('TC3: Ошибка входа')
def test_03_invalid_login(driver, base_url, unique_user):
    login = MainPage(driver, base_url).open_main_page().click_signup_login()
    login.login_with_credentials(unique_user['email'], unique_user['password'], wrong=True).verify_login_error().check_login_page_is_opened()


@allure.title('TC4: Выход')
def test_04_logout(driver, base_url, account):
    MainPage(driver, base_url).click_logout().check_login_page_is_opened()


@allure.title('TC5: Повторная регистрация email')
def test_05_duplicate(driver, base_url, account):
    MainPage(driver, base_url).click_logout().signup_with_credentials(account['name'], account['email'], wrong=True).verify_signup_error()
