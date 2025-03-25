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

def query_data(driver: WebDriver,
               field: str = "BATTING") -> WebDriver:

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

    # Edit minimum filter to equal one
    WebDriverWait(driver, 20) \
        .until(EC.visibility_of_element_located((By.NAME, "commit")))
    WebDriverWait(driver, 10) \
        .until(EC.element_to_be_clickable((By.ID, "atleast")))
    driver.find_element(By.ID, "atleast").send_keys(Keys.BACKSPACE + '1')

    # Update search parameters
    WebDriverWait(driver, 20) \
        .until(EC.element_to_be_clickable((By.NAME, "commit")))
    driver.find_element(By.NAME, "commit").click()

    return driver


def collect_outfield_data(driver: WebDriver,
                          output_directory: str,
                          output_filename: str) -> Tuple[WebDriver, pd.DataFrame]:

    # Collect page source
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Parse the html to find the data
    table = soup.find('table')

    # Collect table headers
    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    # Create empty dataframe
    summary_df = pd.DataFrame(columns=headers)

    # Iterate through each page to collect batting stats for the year
    scan_pages = True
    rank = 1
    while scan_pages:
        try:
            # Scrape high level summary of outfield data
            summary_df, _ = collect_table_data(driver, headers,
                                               summary_df, rank)

            # Return to previous page
            WebDriverWait(driver, 10) \
                .until(EC.element_to_be_clickable((By.LINK_TEXT, "Next")))
            driver.find_element(By.LINK_TEXT, "Next").click()

            rank = rank + 10

        except BaseException:

            # Exit while loop
            scan_pages = False

    # Clean batting summary dataframe
    summary_df = summary_df.reset_index().drop(columns=['index'])

    # Write data to csv file
    summary_df.to_csv(f'{output_directory}{output_filename}', index=False)

    return driver, summary_df


def collect_batting_data(driver: WebDriver,
                         output_directory: str) -> Tuple[WebDriver, pd.DataFrame]:

    # Collect page source
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Parse the html to find the data
    table = soup.find('table')

    # Collect table headers
    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    # Create empty dataframe
    summary_df = pd.DataFrame(columns=headers)

    # Define individual batting stats column headers
    individual_batting_stats_columns = \
        ['SEASON', 'GAMES', 'INNS', 'NOT OUTS', 'RUNS', 'HIGH SCORE',
         'AVG', '50s', '100s', '4s', '6s', 'DUCKS', '%TEAM RUNS', 'PLAYER']

    # Create empty individual batting stats dataframe
    batting_stats_df = \
        pd.DataFrame(columns=individual_batting_stats_columns)

    # Iterate through each page to collect batting stats for the year
    scan_pages = True
    rank = 1
    while scan_pages:
        try:
            # Scrape high level summary of batting data
            summary_df, page_df = collect_table_data(driver, headers,
                                                     summary_df, rank)

            # Iterate through each player and collect their batting data
            for player in page_df['PLAYER'].tolist():

                # Collect individual batting data
                batting_stats_df = \
                    collect_individual_player_batting_data(driver, player,
                                                           batting_stats_df)

            # Navigate to next page
            WebDriverWait(driver, 10) \
                .until(EC.element_to_be_clickable((By.LINK_TEXT, "Next")))
            driver.find_element(By.LINK_TEXT, "Next").click()

            rank = rank + 10

        except BaseException:

            # Exit while loop
            driver.execute_script("window.scrollTo(0, 0);")
            scan_pages = False

    # Clean batting summary dataframe
    summary_df = summary_df.reset_index().drop(columns=['index'])

    # Write data to csv file
    batting_stats_df.to_csv(f'{output_directory}batting_data.csv', index=False)

    return driver, batting_stats_df


def collect_individual_player_batting_data(driver: WebDriver,
                                           player_name: str,
                                           batting_stats_df: pd.DataFrame) -> pd.DataFrame:

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
    data = [row for row in rows if len(row) == len(batting_stats_df.columns)]

    # print(data[0:3])

    # Convert data into dataframe and append player name to dataframe
    page_df = pd.DataFrame(data, columns=batting_stats_df.columns)
    page_df['PLAYER'] = player_name

    # Union existing data with new data
    batting_stats_df = pd.concat([batting_stats_df, page_df])

    # # Filter out old data - only keep data from the current season
    # batting_stats_df = batting_stats_df[batting_stats_df['SEASON'] == str(datetime.now().year)]

    # Return to previous page
    driver.back()

    return batting_stats_df


def collect_table_data(driver: WebDriver,
                       columns: list,
                       df: pd.DataFrame,
                       rank: int) -> Tuple[pd.DataFrame, pd.DataFrame]:

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
