# Import Selenium dependencies
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Import python dependencies
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Tuple
import pandas as pd
import logging
import time


def query_data(
    driver: WebDriver,
    field: str = "BATTING"
) -> WebDriver:
    """
    Function to navigate to correct tab on the play cricket website

    Args:
        driver (WebDriver): Selenium driver
        field (str = 'BATTING): Data type being explored. Acceptable values include
            'BATTING', 'BOWLING' or 'FIELDING'

    Raise:
        ValueError: If field value not one of acceptable values

    Return:
        driver (WebDriver): Selenium WebDriver
    """
    # Ensure field value is acceptable
    if field not in ['BATTING', 'BOWLING', 'FIELDING']:
        raise ValueError(f"field value: {field} not acceptable. Acceptable values "
                         "include 'BATTING', 'BOWLING', 'FIELDING'")

    # Navigate to statistics tab
    WebDriverWait(driver, 10) \
        .until(EC.presence_of_element_located((By.LINK_TEXT, "STATISTICS")))
    driver.find_element(By.LINK_TEXT, "STATISTICS").click()

    if field != "BATTING:":
        # Navigate to statistics tab
        WebDriverWait(driver, 10) \
            .until(EC.element_to_be_clickable((By.LINK_TEXT, field)))
        driver.find_element(By.LINK_TEXT, field).click()

    # Locate the dropdown element
    time.sleep(1)
    dropdown_element = driver.find_element("id", "season")

    # Wrap it with a Select object
    dropdown = Select(dropdown_element)

    # Select the option with visible text of previous year
    dropdown.select_by_visible_text(str(int(datetime.now().year) - 1))

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


def collect_table_data(
    driver: WebDriver,
    columns: list,
    df: pd.DataFrame,
    rank: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Function to collect summary data from play cricket

    Args:
        driver (WebDriver): Selenium Webdriver
        columns (list): Columns for dataframe
        df (pd.DataFrame): Summary of data collected so far
        rank (int): The table rank evaluating

    Raise: None

    Return:
        df (pd.DataFrame): Summary dataframe collected so far
        page_df (pd.DataFrame): Summary dataframe of current page being evaluated
    """
    # Wait for page to render
    WebDriverWait(driver, 10) \
        .until(EC.text_to_be_present_in_element((By.CLASS_NAME, "tfont1"), str(rank)))

    # Collect page source code
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('table')

    # Iterate through table to collect data
    rows = []
    for tr in table.find_all('tr')[1:]:
        cells = tr.find_all('td')
        row = [cell.text.strip() for cell in cells]
        rows.append(row)

    # Remove non relevant data
    data = [row for row in rows if len(row) == len(columns)]

    # Put data into a dataframe
    page_df = pd.DataFrame(data, columns=columns)

    # Union new data with existing data
    df = pd.concat([df, page_df])

    return df, page_df


def collect_dismissal_data(
    dismissal_metric: str,
    driver: WebDriver,
    player_name: str,
    dismissal_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Function to collect dismissal data (only applicable for bowling and batting)

    Args:
        dismissal_metric (str): Metric to click on play cricket frontend
        driver (WebDriver): Selenium WebDriver
        player_name (str): Player name to append to dataframe
        dismissal_df (pd.DataFrame): Summary of existing dismissal data

    Raise:
        ValueError: If dismissal error is not 'Dismissals' or 'How Out'

    Return:
        dismissal_df (pd.DataFrame): Summary of dismissal dataframe
    """
    # Ensure dismissal metric is acceptable value
    if dismissal_metric not in ['Dismissals', 'How Out']:
        raise ValueError(f'dismissal_metric value {dismissal_metric} not acceptable, '
                         "acceptable values include 'Dismissals' or 'How Out'")

    # Open individual player batting stats
    WebDriverWait(driver, 10) \
        .until(EC.element_to_be_clickable((By.LINK_TEXT, dismissal_metric)))
    driver.find_element(By.LINK_TEXT, dismissal_metric).click()

    # Wait until player statistics header has loaded
    WebDriverWait(driver, 10) \
        .until(EC.text_to_be_present_in_element((By.TAG_NAME, "h2"), 'PLAYER STATISTICS'))

    # Load page source
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Locate player data
    table = soup.find('table')

    # Iterate through each row in table and collect the data
    rows = []
    for tr in table.find_all('tr')[1:]:
        cells = tr.find_all('td')
        row = [cell.text.strip() for cell in cells]
        rows.append(row)

    # Filter out incorrect data
    data = [row for row in rows if len(row) == len(dismissal_df.columns)]

    # Convert data into dataframe and append player name to dataframe
    page_df = pd.DataFrame(data, columns=dismissal_df.columns)
    page_df['PLAYER'] = player_name

    # Function to remove percentages
    def remove_percentage(cell):
        return cell.split(" ")[0] if "(" in cell else cell  # Keep only the number before '('

    # Apply the function to the entire DataFrame (excluding SEASON and PLAYER columns)
    page_df.iloc[:, 1:-1] = page_df.iloc[:, 1:-1].applymap(remove_percentage)

    # Union existing data with new data
    dismissal_df = pd.concat([dismissal_df, page_df])

    # Return back to previous page
    driver.back()

    return dismissal_df


def collect_individual_player_data(
    driver: WebDriver,
    player_name: str,
    player_stats_df: pd.DataFrame,
    dismissal_df: pd.DataFrame,
    field: str,
    logger: logging.Logger
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Function to collect individual player data

    Args:
        driver (WebDriver): Selenium Driver
        player_name (str): Player name to click on when navigating the frontend
        player_stats_df (pd.DataFrame): Summary of individual player data
        dismissal_df (pd.DataFrame): Summary of dismissal dataframe
        field (str): Dataset to explore, acceptable values are 'BATTING', 'BOWLING' & 'FIELDING'
        logger (logging.Logger): Python logging object

    Raise:
        ValueError: If field is not acceptable value

    Return
        player_stats_df (pd.DataFrame): Summary of player stats
        dismissal_df (pd.DataFrame): Summary of dismissal stats

    """
    # Ensure field value is acceptable
    if field not in ['BATTING', 'BOWLING', 'FIELDING']:
        raise ValueError(f'dismissal_metric value {field} not acceptable, '
                         "acceptable values include 'BATTING', 'BOWLING' or 'FIELDING'")

    # Log which player we're collecting data for
    logger.info(f'Collecting {field.lower()} data for {player_name}')

    # Open individual player batting stats
    WebDriverWait(driver, 10) \
        .until(EC.element_to_be_clickable((By.LINK_TEXT, player_name)))
    driver.find_element(By.LINK_TEXT, player_name).click()

    WebDriverWait(driver, 10) \
        .until(EC.text_to_be_present_in_element((By.TAG_NAME, "h2"), 'PLAYER STATISTICS'))

    # Load page source
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Locate player data
    table = soup.find('table')

    # Iterate through each row in table and collect the data
    rows = []
    for tr in table.find_all('tr')[1:]:
        cells = tr.find_all('td')
        row = [cell.text.strip() for cell in cells]
        rows.append(row)

    # Filter out incorrect data
    data = [row for row in rows if len(row) == len(player_stats_df.columns)]

    # Convert data into dataframe and append player name to dataframe
    page_df = pd.DataFrame(data, columns=player_stats_df.columns)
    page_df['PLAYER'] = player_name

    # Union existing data with new data
    player_stats_df = pd.concat([player_stats_df, page_df])

    # If field is bowling, calculate bowling dismissal data
    if field == 'BOWLING':
        dismissal_df = collect_dismissal_data(dismissal_metric='Dismissals',
                                              driver=driver,
                                              player_name=player_name,
                                              dismissal_df=dismissal_df)

    # If field is batting, calculate batting dismissal data
    if field == 'BATTING':
        dismissal_df = collect_dismissal_data(dismissal_metric='How Out',
                                              driver=driver,
                                              player_name=player_name,
                                              dismissal_df=dismissal_df)

    # Return to previous page
    driver.back()

    return player_stats_df, dismissal_df


def collect_player_statistics_data(
    driver: WebDriver,
    logger: logging.Logger,
    field: str = 'BATTING'
) -> Tuple[WebDriver, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Function to collect player statistics

    Args:
        driver (WebDriver): Selenium Webdriver
        logger: (logging.Logger): Python logging object
        filed (str): Filed to investigate. Acceptable values include 'BATTING', 'BOWLING' or 'FIELDING'

    Raise:
        ValueError: If field not an acceptable value

    Return:
        driver (WebDriver): Selenium WebDriver
        summary_df (pd.DataFrame): Summary high level data
        player_stats_df (pd.DataFrame): Summary of granular player data
        dismissal_df (pd.DataFrame): Summary of dismissal data
    """
    # Ensure field value is acceptable
    if field not in ['BATTING', 'BOWLING', 'FIELDING']:
        raise ValueError(f'dismissal_metric value {field} not acceptable, '
                         "acceptable values include 'BATTING', 'BOWLING' or 'FIELDING'")

    # Navigate to statistics page
    driver = query_data(driver=driver,
                        field=field)

    # Collect page source
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Parse the html to find the data
    table = soup.find('table')

    # Collect table headers
    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    # Create empty high level summary dataframe
    summary_df = pd.DataFrame(columns=headers)

    # Define dataframe columns
    metric_columns = []
    dismissal_columns = []

    # Define batting columns
    if field == 'BATTING':
        # Define individual batting stats column headers
        metric_columns = ['SEASON', 'GAMES', 'INNS', 'NOT OUTS',
                          'RUNS', 'HIGH SCORE', 'AVG', '50s', '100s',
                          '4s', '6s', 'DUCKS', '%TEAM RUNS', 'PLAYER']

        dismissal_columns = ['SEASON', 'BOWLED', 'CAUGHT', 'LBW', 'STUMPED',
                             'RUN OUT', 'NOT OUT', 'DID NOT BAT', 'HIT ROOF', 'OTHER']

    # Define bowling data
    if field == 'BOWLING':
        # Define individual bowling stats columns headers
        metric_columns = ['SEASON', 'OVERS', 'MAIDENS', 'RUNS', 'WICKETS',
                          'BEST BOWLING', '5 WICKET HAUL', 'ECONOMY RATE',
                          'STRIKE RATE', 'AVERAGE', '%TEAM WICKETS', 'PLAYER']

        dismissal_columns = ['SEASON', 'BOWLED', 'CAUGHT', 'LBW', 'STUMPED', 'HIT ROOF']

    # Create low level granular stats dataframe
    player_stats_df = pd.DataFrame(columns=metric_columns)

    # Create dismissal stats dataframe
    dismissal_df = pd.DataFrame(columns=dismissal_columns)

    # Iterate through each page to collect batting stats for the year
    rank = 1
    while True:
        try:
            # Scrape high level summary of outfield data
            summary_df, page_df = collect_table_data(driver=driver,
                                                     columns=headers,
                                                     df=summary_df,
                                                     rank=rank)

            # Collect granular batting data if field is batting
            if field == 'BATTING':
                # Iterate through each player and collect their batting data
                for player in page_df['PLAYER'].tolist():

                    # Collect individual batting data
                    player_stats_df, dismissal_df = \
                        collect_individual_player_data(driver=driver,
                                                       player_name=player,
                                                       player_stats_df=player_stats_df,
                                                       dismissal_df=dismissal_df,
                                                       field=field,
                                                       logger=logger)

            # COllect granular bowling data if field is bowling
            if field == 'BOWLING':
                # Iterate through each player and collect their batting data
                for player in page_df['PLAYER'].tolist():

                    # Collect individual batting data
                    player_stats_df, dismissal_df = \
                        collect_individual_player_data(driver=driver,
                                                       player_name=player,
                                                       player_stats_df=player_stats_df,
                                                       dismissal_df=dismissal_df,
                                                       field=field,
                                                       logger=logger)

            try:
                # Return to previous page
                WebDriverWait(driver, 10) \
                    .until(EC.element_to_be_clickable((By.LINK_TEXT, "Next")))
                driver.find_element(By.LINK_TEXT, "Next").click()

                # Increment rank for next page
                rank = rank + 10

            except TimeoutException:
                driver.execute_script("window.scrollTo(0, 0);")
                break

        except BaseException as e:
            logger.error(f'Issue collecting {field.lower()} data - {e}')
            break

    return driver, summary_df, player_stats_df, dismissal_df
