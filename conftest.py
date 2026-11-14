import json
import logging
import uuid

import allure
import pytest
from selenium import webdriver
from src.config import settings


def pytest_addoption(parser):
    parser.addoption('--browser', choices=['chrome', 'firefox'], default=settings.BROWSER)
    parser.addoption('--url', default=settings.BASE_URL)
    parser.addoption('--grid-url', default=settings.SELENIUM_GRID_URL)
    parser.addoption('--mode', choices=['remote', 'local'], default='remote' if settings.REMOTE_MODE else 'local')
    parser.addoption('--headless', action='store_true')


@pytest.fixture(scope='session')
def base_url(request):
    return request.config.getoption('--url').rstrip('/')


@pytest.fixture(scope='session')
def grid_url(request):
    return request.config.getoption('--grid-url')


@pytest.fixture
def driver(request, grid_url, base_url):
    browser = request.config.getoption('--browser')
    options = webdriver.ChromeOptions() if browser == 'chrome' else webdriver.FirefoxOptions()
    if request.config.getoption('--headless'):
        options.add_argument('--headless=new' if browser == 'chrome' else '-headless')
    if browser == 'chrome':
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'performance': 'ALL'})
    factory = webdriver.Chrome if browser == 'chrome' else webdriver.Firefox
    instance = (webdriver.Remote(command_executor=grid_url, options=options)
                if request.config.getoption('--mode') == 'remote' else factory(options=options))
    try:
        from src.metrics import Metrics
        instance.metrics = Metrics(request.node.nodeid, browser, uuid.uuid4().hex)
        instance.implicitly_wait(0)
        instance.set_page_load_timeout(60)
        instance.set_window_size(1440, 1000)
        yield instance
    finally:
        try:
            user = getattr(instance, 'pending_account', None)
            if user:
                from src.pages.MainPage import MainPage
                home = MainPage(instance, base_url).open_main_page()
                if not instance.find_elements(*home.LOGGED_AS):
                    home.click_signup_login().login_with_credentials(user['email'], user['password'])
                home.click_delete_account().verify_deleted_msg()
        finally:
            try:
                instance.metrics.save()
            finally:
                instance.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    report = (yield).get_result()
    if not report.failed:
        return
    instance = item.funcargs.get('driver')
    if instance is None:
        return
    artifact_id = item.name + '-' + uuid.uuid4().hex
    settings.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        screenshot = instance.get_screenshot_as_png()
        (settings.SCREENSHOTS_DIR / (artifact_id + '.png')).write_bytes(screenshot)
        allure.attach(screenshot, 'Failure screenshot', allure.attachment_type.PNG)
    except Exception as exc:
        logging.warning('Screenshot unavailable: %s', type(exc).__name__)
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    for kind in ('browser', 'performance'):
        try:
            entries = instance.get_log(kind)
            # Do not persist URLs, headers, request bodies or console messages.
            from src.diagnostics import sanitize
            safe = sanitize(entries, kind)
            data = json.dumps({'kind': kind, 'entries': safe})
        except Exception as exc:
            data = json.dumps({'kind': kind, 'unavailable': type(exc).__name__})
        (settings.LOGS_DIR / (artifact_id + '-' + kind + '.json')).write_text(data, encoding='utf-8')
        allure.attach(data, kind, allure.attachment_type.JSON)


@pytest.fixture
def unique_user():
    class TestUser(dict):
        def __repr__(self):
            return repr({k: '[REDACTED]' if k == 'password' else v for k, v in self.items()})
    return TestUser(name='Test User', email=f'qa_{uuid.uuid4().hex}@example.com', password=uuid.uuid4().hex)


@pytest.fixture(autouse=True)
def report_labels(request):
    allure.dynamic.epic('Automation Exercise')
    allure.dynamic.feature(request.node.path.stem)
    allure.dynamic.story(request.node.originalname or request.node.name)
    allure.dynamic.severity(allure.severity_level.NORMAL)
    allure.dynamic.tag(*[m.name for m in request.node.iter_markers()])
