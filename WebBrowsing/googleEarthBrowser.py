from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
url = 'https://earth.google.com/'
driver = webdriver.Chrome()
driver.get(url)
wait = WebDriverWait(driver, 10)
launchButton = wait.until(EC.element_to_be_clickable((By.XPATH, '')))
launchButton.click()