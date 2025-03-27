# Import Selenium dependencies
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver

# Import python dependencies
import logging
import os

def configure_logger() -> logging.Logger:
    """
    """
    # Configure Logger
    logger = logging.getLogger('BASIC')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    return logger


class Variables:
    """
    """
    def __init__(self):

        # Collect environmental variables
        self.club = os.getenv('club')
        self.email = os.getenv('email')
        self.password = os.getenv('password')
        self.headless = os.getenv('headless')
        self.driver_path = os.getenv('driver_path')
        self.email_sender = os.getenv('email_sender')
        self.email_password = os.getenv('email_password')
        self.email_reciever = os.getenv('email_reciever')
        self.output_directory = os.getenv('output_directory')
        self.blob_connection_string = os.getenv('blob_connection_string')


def configure_driver(
    driver_path: str = 'chromedriver.exe',
    headless: bool = False
) -> WebDriver:
    """
    """
    # Configure logging to suppress unwanted messages
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")

    if headless:
        chrome_options.add_argument("--headless")

    # Configure Driver with options
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    return driver


def login_to_play_cricket(
    driver: WebDriver,
    club: str,
    email: str,
    password: str
) -> WebDriver:
    """
    """
    for _ in range(10):
        # Open chrome on specific play cricket club
        driver.get(f"http://{club}.play-cricket.com/users/sign_in")

        # Enter Password into login form
        WebDriverWait(driver, 10) \
            .until(EC.presence_of_element_located((By.ID, 'password')))
        driver.find_element(By.ID, 'password').send_keys(password)

        # Enter email into login form
        WebDriverWait(driver, 10) \
            .until(EC.presence_of_element_located((By.ID, 'email')))
        driver.find_element(By.ID, 'email').send_keys(email)

        # Click Login button
        i = 0
        while i < 5:
            try:
                # Click Submit on login form
                WebDriverWait(driver, 10) \
                    .until(EC.presence_of_element_located((By.CLASS_NAME, "sc-bBHwJV")))
                driver.find_element(By.CLASS_NAME, "sc-bBHwJV").click()

            except BaseException:
                pass

            i = i + 1

        # Get all elements with class "mr-10"
        elements = driver.find_elements(By.CLASS_NAME, "mr-10")

        success = False
        for element in elements:
            if club.upper() in element.text:
                success = True
                break

        if success:
            break

    return driver


def remove_cookies_pop_up(
    driver: WebDriver
) -> WebDriver:
    """
    """
    # Remove cookies pop up
    WebDriverWait(driver, 10) \
        .until(EC.presence_of_element_located((By.CLASS_NAME, "onetrust-close-btn-handler")))
    driver.find_element(By.CLASS_NAME, "onetrust-close-btn-handler").click()

    return driver
