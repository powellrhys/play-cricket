from dotenv import load_dotenv
import warnings
import logging
import os

from functions import configure_driver, login_to_play_cricket, \
    remove_cookies_pop_up, query_data, collect_batting_data, \
    collect_outfield_data, email_results

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
headless = os.getenv('headless')
driver_path = os.getenv('driver_path')
email_sender = os.getenv('email_sender')
email_password = os.getenv('email_password')
email_reciever = os.getenv('email_reciever')

# Configure Selenium Driver
driver = configure_driver(driver_path, bool(headless))
logger.info('Selenium Driver Configured')

# Login to play cricket
driver = login_to_play_cricket(driver, club, email, password)
logger.info('Play Cricket Authentication Complete')

# Disable cookies
driver = remove_cookies_pop_up(driver)
logger.info('Cookie Disabled')

# Query batting data
driver = query_data(driver, 'BATTING')
logger.info('Batting Query Executed')

# Collect batting data
logger.info('Collecting Summary of Batting Data...')
driver, batting_df = collect_batting_data(driver)
logger.info('Summary of batting data collected')

# Query bowling data
driver = query_data(driver, 'BOWLING')
logger.info('Bowling Query Executed')

# Collect batting data
logger.info('Collecting Summary of Bowling Data...')
driver, bowling_df = collect_outfield_data(driver, 'bowling_data.csv')
logger.info('Summary of bowling data collected')

# Query bowling data
driver = query_data(driver, 'FIELDING')
logger.info('Fielding Query Executed')

# Collect batting data
logger.info('Collecting Summary of Fielding Data...')
driver, fielding_df = collect_outfield_data(driver, 'fielding_data.csv')
logger.info('Summary of fielding data collected')

logger.info('Emailing Results...')
email_results(club, email_sender, email_password, email_reciever,
              batting_df, bowling_df, fielding_df)
logger.info('Results emailed')

driver.quit()
