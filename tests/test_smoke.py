import allure
import pytest
from src.pages.MainPage import MainPage


@pytest.mark.smoke
@allure.title('Главная страница и форма входа доступны')
def test_home_and_login(driver, base_url):
    MainPage(driver, base_url).open_main_page().verify_main_page_visible().click_signup_login().check_login_page_is_opened()
