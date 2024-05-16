from selenium import webdriver
from selenium.webdriver.common.by import By
import time


# Set up Safari driver
driver = webdriver.Safari()

# Open a webpage
driver.get('https://adamchoi.co.uk/teamgoals/detailed')

all_matches_button = driver.find_element(By.XPATH, '//label[@analytics-event="All matches"]')
all_matches_button.click()

time.sleep(5)

# Close the browser
driver.quit()
