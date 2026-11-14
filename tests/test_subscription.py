import allure
import pytest
from src.pages.MainPage import MainPage

pytestmark = pytest.mark.subscription


@allure.title('TC10: Подписка на главной странице')
def test_10_home(driver, base_url, unique_user):
    MainPage(driver, base_url).open_main_page().verify_main_page_visible().subscribe(unique_user['email'])


@allure.title('TC11: Подписка в корзине')
def test_11_cart(driver, base_url, unique_user):
    MainPage(driver, base_url).open_main_page().click_view_cart().subscribe(unique_user['email'])
