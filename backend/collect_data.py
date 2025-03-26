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
    collect_player_statistics_data
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

# Collect batting data
logger.info('Collecting Summary of Batting Data...')
driver, batting_summary_df, batting_df, batting_dismissal_df = collect_player_statistics_data(driver=driver,
                                                                                              field='BATTING')
logger.info('Summary of batting data collected\n')

batting_df.to_csv('data/batting_data.csv', index=False)
batting_dismissal_df.to_csv('data/batting_how_out.csv', index=False)

# Collect bowling data
logger.info('Collecting Summary of Bowling Data...')
driver, bowling_summary_df, bowling_df, bowling_dismissal_df = collect_player_statistics_data(driver=driver,
                                                                                              field='BOWLING')
logger.info('Summary of bowling data collected\n')

bowling_df.to_csv('data/bowling_data.csv', index=False)
bowling_dismissal_df.to_csv('data/bowling_dismissals.csv', index=False)

# Collect fielding data
logger.info('Collecting Summary of Bowling Data...')
driver, fielding_summary_df, _, _ = collect_player_statistics_data(driver=driver,
                                                                   field='FIELDING')
logger.info('Summary of bowling data collected\n')

bowling_df.to_csv('data/fielding_data.csv', index=False)


# Collect match report ids
logger.info('Collecting Match report ids...')
driver, match_report_ids = collect_match_report_ids(
    logger=logger,
    driver=driver,
    club=vars.club
)
logger.info('All match report ids collected\n')

# Analyse match reports to collect bowling data
logger.info('Analysing match reports')
driver, match_report_bowling_data, logger = analyse_match_reports(logger=logger,
                                                                  driver=driver,
                                                                  result_ids=match_report_ids,
                                                                  club=vars.club)
logger.info('Match report analysis completed\n')

# Write data to csv file
match_report_bowling_data.to_csv('data/bowling_match_data.csv', index=False)

driver.close()
