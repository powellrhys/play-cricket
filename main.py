from dotenv import load_dotenv
import warnings
import logging
import os

from functions import \
    query_data, \
    email_results, \
    configure_driver, \
    collect_batting_data, \
    login_to_play_cricket, \
    remove_cookies_pop_up, \
    collect_outfield_data

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
output_directory = os.getenv('output_directory')

# Configure Selenium Driver
driver = configure_driver(driver_path=driver_path,
                          headless=bool(headless))
logger.info('Selenium Driver Configured')

# Login to play cricket
driver = login_to_play_cricket(driver=driver,
                               club=club,
                               email=email,
                               password=password)
logger.info('Play Cricket Authentication Complete')

# Disable cookies
driver = remove_cookies_pop_up(driver=driver)
logger.info('Cookie Disabled')

# Query batting data
driver = query_data(driver=driver,
                    field='BATTING')
logger.info('Batting Query Executed')

# Collect batting data
logger.info('Collecting Summary of Batting Data...')
driver, batting_df = collect_batting_data(driver=driver,
                                          output_directory=output_directory)
logger.info('Summary of batting data collected')

# Query bowling data
driver = query_data(driver=driver,
                    field='BOWLING')
logger.info('Bowling Query Executed')

# Collect batting data
logger.info('Collecting Summary of Bowling Data...')
driver, bowling_df = collect_outfield_data(driver=driver,
                                           output_directory=output_directory,
                                           output_filename='bowling_data.csv')
logger.info('Summary of bowling data collected')

# Query bowling data
driver = query_data(driver=driver,
                    field='FIELDING')
logger.info('Fielding Query Executed')

# Collect batting data
logger.info('Collecting Summary of Fielding Data...')
driver, fielding_df = collect_outfield_data(driver=driver,
                                            output_directory=output_directory,
                                            output_filename='fielding_data.csv')
logger.info('Summary of fielding data collected')

if os.getenv('to_email'):

    logger.info('Emailing Results...')
    email_results(club=club,
                  email_sender=email_sender,
                  email_password=email_password,
                  email_reciever=email_reciever,
                  batting_df=batting_df,
                  bowling_df=bowling_df,
                  fielding_df=fielding_df)
    logger.info('Results emailed')

driver.quit()
