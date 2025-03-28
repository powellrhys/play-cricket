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
    filter_reports_by_bowlers,
    collect_match_report_ids,
    analyse_match_reports
)

# Import data functions
from functions.data_functions import (
    write_df_to_blob
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
try:
    logger.info('Collecting Summary of Batting Data...')
    driver, batting_summary_df, batting_df, batting_dismissal_df = collect_player_statistics_data(driver=driver,
                                                                                                  logger=logger,
                                                                                                  field='BATTING')
    logger.info('Summary of batting data collected\n')

    # Write batting data to blob storage
    logger.info('Writing batting data to blob storage account...')
    write_df_to_blob(df=batting_df,
                     connection_string=vars.blob_connection_string,
                     container_name='play-cricket',
                     blob_name='batting_data.csv')
    write_df_to_blob(df=batting_dismissal_df,
                     connection_string=vars.blob_connection_string,
                     container_name='play-cricket',
                     blob_name='batting_how_out.csv')
    logger.info('Batting data written to blob\n')

except BaseException as e:
    logger.error(f'Failed to collect and export batting data - {e}\n')

try:
    # Collect bowling data
    logger.info('Collecting Summary of Bowling Data...')
    driver, bowling_summary_df, bowling_df, bowling_dismissal_df = collect_player_statistics_data(driver=driver,
                                                                                                  logger=logger,
                                                                                                  field='BOWLING')
    logger.info('Summary of bowling data collected\n')

    # Write bowling data to blob storage
    logger.info('Writing bowling data to blob storage account...')
    write_df_to_blob(df=bowling_df,
                     connection_string=vars.blob_connection_string,
                     container_name='play-cricket',
                     blob_name='bowling_data.csv')
    write_df_to_blob(df=bowling_dismissal_df,
                     connection_string=vars.blob_connection_string,
                     container_name='play-cricket',
                     blob_name='bowling_dismissals.csv')
    logger.info('Bowling data written to blob\n')

except BaseException as e:
    logger.error(f'Failed to collect and export bowling data - {e}\n')

try:
    # Collect fielding data
    logger.info('Collecting Summary of Fielding Data...')
    driver, fielding_summary_df, _, _ = collect_player_statistics_data(driver=driver,
                                                                       logger=logger,
                                                                       field='FIELDING')
    logger.info('Summary of fielding data collected\n')

    # Write fielding data to blob storage
    logger.info('Writing fielding data to blob storage account...')
    write_df_to_blob(df=fielding_summary_df,
                     connection_string=vars.blob_connection_string,
                     container_name='play-cricket',
                     blob_name='fielding_data.csv')
    logger.info('Fielding data written to blob\n')

except BaseException as e:
    logger.error(f'Failed to collect and export fielding data - {e}\n')

try:
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

    # Filter report data by recent bowlers at club
    logger.info('Filtering match report data by recent club bowlers...')
    match_report_bowling_data = \
        filter_reports_by_bowlers(match_report_bowling_data=match_report_bowling_data,
                                  vars=vars)
    logger.info('Match report data filtered by recent club bowlers')

    # Write match report bowling data to blob storage
    logger.info('Writing match report bowling data to blob storage account...')
    write_df_to_blob(df=match_report_bowling_data,
                     connection_string=vars.blob_connection_string,
                     container_name='play-cricket',
                     blob_name='bowling_match_data.csv')
    logger.info('Match report bowling data written to blob\n')

except BaseException as e:
    logger.error(f'Failed to collect and export bowling match report data data - {e}\n')

driver.close()
