# This script opens Google Earth using Selenium WebDriver
# and clicks the "Apps" button to launch the app.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def open_google_earth():
    """
    Opens Google Earth using Selenium WebDriver and clicks the "Apps" button to launch the app.
    """
    # Define the URL for Google Earth
    url = 'https://earth.google.com/'
    
    # Create a new instance of the Chrome WebDriver
    driver = webdriver.Chrome()
    
    # Navigate to the Google Earth URL
    driver.get(url)
    
    # Create a WebDriverWait object with a timeout of 10 seconds
    wait = WebDriverWait(driver, 10)
    
    # Wait for the "Apps" button to be clickable and click it
    launch_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="apps-button"]')))
    launch_button.click()

open_google_earth()

