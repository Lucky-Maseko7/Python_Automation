from selenium import webdriver

driver = webdriver.Chrome()
driver.get('https://scrapingclub.com/exercise/basic_login/')

loginName = driver.find_element('id', 'id_name')
loginName.send_keys('johnCarter')

loginPassword = driver.find_element('id', 'id_password')
loginPassword.send_keys('Password@123')

loginbutton = driver.find_element('xpath', '/html/body/div[3]/div/div/div[1]/div[3]/form/button')
loginbutton.click()