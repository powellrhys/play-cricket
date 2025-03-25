# Import python dependencies
from dotenv import load_dotenv
import warnings

# Import backend setup functions
from functions.setup_functions import (
    login_to_play_cricket,
    remove_cookies_pop_up,
    configure_driver,
    configure_logger,
    Variables
)

# Import statistics functions
from functions.statistics_functions import (
    query_data
)

# Import 
from functions.old_functions import (
    collect_outfield_data,
    collect_batting_data,
    query_data,
)

# Import result functions
from functions.result_functions import (
    collect_match_report_ids,
    analyse_match_reports
)

# Ignore warnings
warnings.filterwarnings("ignore")

# Configure Logger
logger = configure_logger()

# Load environment variables
load_dotenv()
vars = Variables()

# Configure Selenium Driver
driver = configure_driver(driver_path=vars.driver_path,
                          headless=bool(vars.headless))
logger.info('Selenium Driver Configured')

# Login to play cricket
driver = login_to_play_cricket(driver=driver,
                               club=vars.club,
                               email=vars.email,
                               password=vars.password)
logger.info('Play Cricket Authentication Complete')

# Disable cookies
driver = remove_cookies_pop_up(driver=driver)
logger.info('Cookie Disabled')

# # Query batting data
# driver = query_data(driver=driver,
#                     field='BATTING')
# logger.info('Batting Query Executed')

# # Collect batting data
# logger.info('Collecting Summary of Batting Data...')
# driver, batting_df = collect_batting_data(driver=driver,
#                                           output_directory=output_directory)
# logger.info('Summary of batting data collected')

# # Query bowling data
# driver = query_data(driver=driver,
#                     field='BOWLING')
# logger.info('Bowling Query Executed')

# # Collect batting data
# logger.info('Collecting Summary of Bowling Data...')
# driver, bowling_df = collect_outfield_data(driver=driver,
#                                            output_directory=output_directory,
#                                            output_filename='bowling_data.csv')
# logger.info('Summary of bowling data collected')

# # Query bowling data
# driver = query_data(driver=driver,
#                     field='FIELDING')
# logger.info('Fielding Query Executed')

# # Collect batting data
# logger.info('Collecting Summary of Fielding Data...')
# driver, fielding_df = collect_outfield_data(driver=driver,
#                                             output_directory=output_directory,
#                                             output_filename='fielding_data.csv')
# logger.info('Summary of fielding data collected')


# Collect match report ids
driver, match_report_ids = collect_match_report_ids(
    driver=driver,
    club=vars.club
)

# Analyse match reports to collect bowling data
driver, bowling_stats, logger = analyse_match_reports(
    logger=logger,
    driver=driver,
    result_ids=match_report_ids,
    club=vars.club
)

# Write data to csv file
bowling_stats.to_csv('data/bowling_stats.csv', index=False)
