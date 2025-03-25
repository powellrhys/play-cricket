# Import Selenium dependencies
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver

# Import python dependencies
from bs4 import BeautifulSoup
from typing import Tuple
import pandas as pd
import time


def query_data(
    driver: WebDriver,
    field: str = "BATTING"
) -> WebDriver:
    """
    """
    # Navigate to statistics tab
    WebDriverWait(driver, 10) \
        .until(EC.presence_of_element_located((By.LINK_TEXT, "STATISTICS")))
    driver.find_element(By.LINK_TEXT, "STATISTICS").click()

    if field != "BATTING:":

        # Navigate to statistics tab
        WebDriverWait(driver, 10) \
            .until(EC.element_to_be_clickable((By.LINK_TEXT, field)))
        driver.find_element(By.LINK_TEXT, field).click()

    # Open data filter tab
    time.sleep(1)
    WebDriverWait(driver, 10) \
        .until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-filter")))
    driver.find_element(By.CLASS_NAME, "btn-filter").click()

    # Edit minimum filter to equal one - locate element
    WebDriverWait(driver, 20) \
        .until(EC.visibility_of_element_located((By.NAME, "commit")))

    # Edit minimum filter to equal one - wait until element is clickable
    WebDriverWait(driver, 10) \
        .until(EC.element_to_be_clickable((By.ID, "atleast")))
    driver.find_element(By.ID, "atleast").send_keys(Keys.BACKSPACE + '1')

    # Update search parameters
    WebDriverWait(driver, 20) \
        .until(EC.element_to_be_clickable((By.NAME, "commit")))
    driver.find_element(By.NAME, "commit").click()

    return driver
