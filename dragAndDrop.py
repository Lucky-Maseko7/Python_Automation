from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
chromeOptions = webdriver.ChromeOptions()
# chromeOptions.add_argument('--no-sandbox')
# chromeOptions.add_argument('--disable-gpu')
# chromeOptions.add_argument('--headless')
# chromeOptions.add_argument('--disable-dev-shm-usage')
chromeOptions.add_argument('--allow-running-insecure-content')
chromeOptions.add_argument('--ignore-certificate-errors')
chromeOptions.add_argument("--disable-proxy-certificate-handler")
chromeOptions.add_argument('--disable-third-party-cookies')
chromeOptions.add_argument("--disable-web-security")

# Set Chrome preferences to enable third-party cookies
prefs = {
    "profile": {
        "default_content_setting_values": {
            "cookies": 2  # Enable third-party cookies
        }
    }
}
chromeOptions.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chromeOptions)
driver.maximize_window()
driver.get('http://dhtmlgoodies.com/scripts/drag-drop-custom/demo-drag-drop-3.html')

source = driver.find_element('xpath', '//*[@id="box7"]')
dest = driver.find_element('xpath', '//*[@id="box107"]')

actions = ActionChains(driver)
actions.drag_and_drop(source, dest).perform()

