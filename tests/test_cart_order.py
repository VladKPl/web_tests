import allure
import pytest
from src.pages.MainPage import MainPage

pytestmark = [pytest.mark.cart, pytest.mark.regression]


@allure.title('TC12: Два товара в корзине')
def test_12_products(driver, base_url):
    products = MainPage(driver, base_url).open_main_page().verify_main_page_visible().click_products()
    expected = products.products()[:2]
    cart = products.add_product(0).click_continue_shopping().add_product(1).click_view_cart()
    assert cart.items() == [dict(**p, quantity=1, total=p['price']) for p in expected]


@allure.title('TC13: Количество товара равно четырём')
def test_13_quantity(driver, base_url):
    cart = MainPage(driver, base_url).open_main_page().click_first_view_product().verify_product_detail_opened().set_quantity(4).add_to_cart().click_view_cart()
    items = cart.items()
    assert len(items) == 1
    assert items[0]['quantity'] == 4
    assert items[0]['total'] == items[0]['price'] * 4


@pytest.mark.order
@pytest.mark.parametrize('during_checkout', [True, False], ids=['TC14', 'TC15'])
@allure.title('Заказ с регистрацией')
def test_order(driver, base_url, unique_user, during_checkout):
    home = MainPage(driver, base_url).open_main_page()
    created = False
    try:
        if during_checkout:
            login = home.click_products().add_product().click_view_cart().register_at_checkout()
        else:
            login = home.click_signup_login()
        result = login.signup_with_credentials(unique_user['name'], unique_user['email']).register_user(unique_user)
        created = True
        result.click_continue().verify_logged_in_as()
        cart = home.click_view_cart() if during_checkout else home.click_products().add_product().click_view_cart()
        expected = cart.items()
        checkout = cart.checkout()
        assert checkout.items() == expected
        checkout.place_order().pay()
    finally:
        if created:
            home.click_delete_account().verify_deleted_msg().click_continue()
