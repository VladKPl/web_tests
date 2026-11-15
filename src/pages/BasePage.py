from urllib.parse import urljoin
from contextlib import nullcontext
from functools import wraps
from src.config.settings import TIMEOUT
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException, NoSuchFrameException

def timed(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        metrics = getattr(self.driver, 'metrics', None)
        with metrics.measure(type(self).__name__ + '.' + method.__name__) if metrics else nullcontext():
            return method(self, *args, **kwargs)
    return wrapped


class BasePage:
    CONSENT_MANAGE = (By.CSS_SELECTOR, '.fc-cta-manage-options')
    CONSENT_CONFIRM = (By.CSS_SELECTOR, '.fc-data-preferences-dialog .fc-confirm-choices')
    CONSENT_OVERLAY = (By.CSS_SELECTOR, '.fc-dialog-overlay')
    AD_FRAMES = (By.TAG_NAME, 'iframe')
    AD_CLOSE = (By.ID, 'dismiss-button')

    def _dismiss_interstitial(self):
        if '#google_vignette' not in self.driver.current_url:
            return
        for frame in self.driver.find_elements(*self.AD_FRAMES):
            try:
                self.driver.switch_to.frame(frame)
                button = EC.element_to_be_clickable(self.AD_CLOSE)(self.driver)
                if button:
                    button.click()
                    return
            except (NoSuchElementException, StaleElementReferenceException, NoSuchFrameException):
                continue
            finally:
                self.driver.switch_to.default_content()

    @allure.step('Закрытие диалога privacy с текущими настройками')
    def dismiss_consent(self, timeout=3):
        try:
            button = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(self.CONSENT_MANAGE))
        except TimeoutException:
            return self
        button.click()
        self.wait_for_element_clickable(self.CONSENT_CONFIRM).click()
        WebDriverWait(self.driver, self.timeout).until(EC.invisibility_of_element_located(self.CONSENT_OVERLAY))
        return self
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, method in list(cls.__dict__.items()):
            if callable(method) and not name.startswith('_'):
                setattr(cls, name, timed(method))

    def __init__(self, driver, base_url, timeout=TIMEOUT):
        self.driver = driver
        self.base_url = base_url
        self.timeout = timeout

    @allure.step("Открываем страницу по URL: {relative_url}")
    def open(self, relative_url=""):
        """Открывает страницу по относительному или полному URL."""
        self.driver.get(urljoin(self.base_url + "/", relative_url))
        self.dismiss_consent()
        return self

    @allure.step("Ожидаем видимость элемента с локатором: {locator}")
    def wait_for_element_visible(self, locator):
        """Ждет, пока элемент станет видимым на странице."""
        def visible(driver):
            self._dismiss_interstitial()
            if any(element.is_displayed() for element in driver.find_elements(*self.CONSENT_OVERLAY)):
                self.dismiss_consent()
            return EC.visibility_of_element_located(locator)(driver)
        return WebDriverWait(self.driver, self.timeout).until(
            visible
        )

    @allure.step("Ожидаем кликабельность элемента с локатором: {locator}")
    def wait_for_element_clickable(self, locator):
        """Ждет, пока элемент станет кликабельным."""
        def clickable(driver):
            if locator not in (self.CONSENT_MANAGE, self.CONSENT_CONFIRM):
                self._dismiss_interstitial()
                if any(e.is_displayed() for e in driver.find_elements(*self.CONSENT_OVERLAY)):
                    self.dismiss_consent()
            return EC.element_to_be_clickable(locator)(driver)
        return WebDriverWait(self.driver, self.timeout).until(
            clickable
        )

    @allure.step("Клик по элементу с локатором: {locator}")
    def click(self, locator):
        """Кликает по элементу по локатору."""
        def press(driver):
            try:
                self._dismiss_interstitial()
                if any(e.is_displayed() for e in driver.find_elements(*self.CONSENT_OVERLAY)):
                    self.dismiss_consent()
                element = EC.element_to_be_clickable(locator)(driver)
                if not element:
                    return False
                driver.execute_script("arguments[0].scrollIntoView({block:'center'})", element)
                ActionChains(driver).move_to_element(element).perform()
                element.click()
                return True
            except (ElementClickInterceptedException, StaleElementReferenceException, NoSuchElementException):
                return False
        WebDriverWait(self.driver, self.timeout).until(press, message=f'Cannot click {locator}')

    def enter_text(self, locator, text):
        """Вводит текст в поле ввода по локатору."""
        element = self.wait_for_element_visible(locator)
        element.clear()
        element.send_keys(text)

    @allure.step("Получаем текущий URL")
    def get_current_url(self):
        """Возвращает текущий URL страницы."""
        return self.driver.current_url

    @allure.step("Выбор значения '{value}' в выпадающем списке с локатором: {locator}")
    def select_by_value(self, locator, value):
        """Выбирает опцию в выпадающем списке по значению (value)."""
        element = self.wait_for_element_visible(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'})", element)
        select_element = Select(element)
        select_element.select_by_value(str(value))
        return self

    @allure.step("Поиск элемента в DOM дереве по локатору: {locator}")
    def find_element(self, locator):
        """Возвращает элемент, если он есть на странице."""
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator),
            message=f"Не удалось найти элемент по локатору: {locator}"
        )

    @allure.step("Поиск списка элементов в DOM дереве по локатору: {locator}")
    def find_elements(self, locator, time=None):
        """Возвращает список элементов, если они есть на странице."""
        wait_timeout = time if time is not None else self.timeout
        return WebDriverWait(self.driver, wait_timeout).until(
            EC.presence_of_all_elements_located(locator),
            message=f"Не удалось найти элементы по локатору: {locator}"
        )

    @allure.step("Наведение мыши на элемент {hover_locator} (индекс: {index}) и клик по {click_locator}")
    def hover_and_click(self, hover_locator, click_locator, index=0):
        """Наводит мышь на элемент (hover) и кликает по другому элементу."""
        actions = ActionChains(self.driver)
        hover_elements = self.find_elements(hover_locator)
        hover_element = hover_elements[index]
        
        actions.move_to_element(hover_element).perform()
        self.click(click_locator)
    wait_for_element_present = find_element

    def get_element_text(self, locator):
        return self.wait_for_element_visible(locator).text

    def get_attribute(self, locator, attribute):
        return self.find_element(locator).get_attribute(attribute)

    def scroll_to_element(self, locator):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", self.find_element(locator))
        return self

    def hover(self, locator):
        ActionChains(self.driver).move_to_element(self.find_element(locator)).perform()
        return self

    def execute_script(self, script, *args):
        return self.driver.execute_script(script, *args)

    def wait_for_url_contains(self, value):
        WebDriverWait(self.driver, self.timeout).until(EC.url_contains(value))
        return self

    @allure.step("Подписка на новости")
    def subscribe(self, email):
        from selenium.webdriver.common.by import By
        self.scroll_to_element((By.ID, 'susbscribe_email'))
        assert self.get_element_text((By.CSS_SELECTOR, '.single-widget h2')) == 'SUBSCRIPTION'
        self.enter_text((By.ID, 'susbscribe_email'), email)
        self.click((By.ID, 'subscribe'))
        assert self.get_element_text((By.ID, 'success-subscribe')) == 'You have been successfully subscribed!'
        return self
