import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

server = subprocess.Popen([sys.executable, '-m', 'http.server', '8765', '--bind', '127.0.0.1', '--directory', 'allure-report'],
                          creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')
    with webdriver.Firefox(options=options) as driver:
        driver.get('http://127.0.0.1:8765')
        WebDriverWait(driver, 20).until(lambda d: '20' in d.find_element(By.TAG_NAME, 'body').text)
        print(driver.title)
        print(driver.find_element(By.TAG_NAME, 'body').text[:1200])
finally:
    server.terminate()
    server.wait(timeout=10)
