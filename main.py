from dotenv import load_dotenv
import warnings
import logging
import os

from functions import configure_driver, login_to_play_cricket, \
    remove_cookies_pop_up, query_batting_data, \
    collect_batting_data_summary_data

# Ignore warnings
warnings.filterwarnings("ignore")

# Configure Logger
logger = logging.getLogger('BASIC')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
log_handler = logging.StreamHandler()
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)

# Load environment variables
load_dotenv()
club = os.getenv('club')
email = os.getenv('email')
password = os.getenv('password')

# Configure Selenium Driver
driver = configure_driver()
logger.info('Selenium Driver Configured')

driver = login_to_play_cricket(driver, club, email, password)
logger.info('Play Cricket Authentication Complete')

driver = remove_cookies_pop_up(driver)
logger.info('Cookie Disabled')

driver = query_batting_data(driver)
logger.info('Batting Query Executed')

logger.info('Collecting Summary of Batting Data...')
driver = collect_batting_data_summary_data(driver)
logger.info('Summary of batting data collected')

driver.quit()
