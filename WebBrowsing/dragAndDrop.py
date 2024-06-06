from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


def configure_chrome_options():
    """
    Configure Chrome options to enable third-party cookies and disable security restrictions.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-proxy-certificate-handler')
    chrome_options.add_argument('--disable-third-party-cookies')
    chrome_options.add_argument('--disable-web-security')

    # Set Chrome preferences to enable third-party cookies
    prefs = {
        "profile": {
            "default_content_setting_values": {
                "cookies": 2  # Enable third-party cookies
            }
        }
    }
    chrome_options.add_experimental_option("prefs", prefs)

    return chrome_options


def navigate_to_url(driver):
    """
    Navigate to the specified URL.
    """
    driver.maximize_window()
    driver.get('http://dhtmlgoodies.com/scripts/drag-drop-custom/demo-drag-drop-3.html')


def perform_drag_and_drop(driver):
    """
    Perform a drag and drop operation on the specified elements.
    """
    source = driver.find_element('xpath', '//*[@id="box7"]')
    dest = driver.find_element('xpath', '//*[@id="box107"]')

    actions = ActionChains(driver)
    actions.drag_and_drop(source, dest).perform()


if __name__ == '__main__':
    # Configure Chrome options
    chrome_options = configure_chrome_options()

    # Create a new Chrome driver with the configured options
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the specified URL
    navigate_to_url(driver)

    # Perform the drag and drop operation
    perform_drag_and_drop(driver)

