import allure
import pytest
from src.pages.MainPage import MainPage


@pytest.mark.auth
@allure.title('Очистка после сбоя проверки создания аккаунта')
def test_cleanup_after_registration_check_failure(driver, base_url, unique_user, monkeypatch):
    from src.pages.AccountCreatedPage import AccountCreatedPage
    original = AccountCreatedPage.verify_created_msg
    def interrupted(page):
        original(page)
        raise RuntimeError('Simulated assertion failure after account creation')
    monkeypatch.setattr(AccountCreatedPage, 'verify_created_msg', interrupted)
    signup = MainPage(driver, base_url).open_main_page().click_signup_login().signup_with_credentials(unique_user['name'], unique_user['email'])
    with pytest.raises(RuntimeError, match='Simulated assertion'):
        signup.register_user(unique_user)
    assert driver.pending_account is unique_user
    # Driver teardown must delete this account, and reports an error if it cannot.


@pytest.mark.cart
@allure.title('Удаление товара и продолжение покупок')
def test_remove_and_continue(driver, base_url):
    products = MainPage(driver, base_url).open_main_page().click_products()
    cart = products.add_product().click_view_cart()
    cart.remove_product().continue_shopping()


@pytest.mark.cart
@allure.title('Переход из каталога в карточку сохраняет название и цену')
def test_catalog_detail(driver, base_url):
    from src.pages.ProductsPage import ProductsPage
    catalog = ProductsPage(driver, base_url).open_catalog()
    expected = catalog.products()[0]
    assert catalog.open_product().product() == expected
