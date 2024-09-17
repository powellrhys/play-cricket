
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time


def configure_driver():

    # Configure logging to suppress unwanted messages
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")

    # Configure Driver with options
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    return driver


def login_to_play_cricket(driver, club, email, password):

    # Open chrome on specific play cricket club
    driver.get(f"http://{club}.play-cricket.com/users/sign_in")
    time.sleep(2)

    # Enter email and password into login page
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.ID, 'email').send_keys(email)

    # Click Login button
    i = 0
    while i < 5:
        try:
            time.sleep(1)
            driver.find_element(By.CLASS_NAME, "sc-bBHwJV") \
                .click()

        except BaseException:
            pass

        i = i + 1

    # Allow some time for to ensure the login was succesful
    time.sleep(3)

    return driver


def remove_cookies_pop_up(driver):

    # Remove cookies pop up
    time.sleep(5)
    driver.find_element(By.CLASS_NAME, "onetrust-close-btn-handler") \
        .click()
    time.sleep(1)

    return driver


def query_data(driver, field: str = "BATTING"):

    # Navigate to statistics tab
    driver.find_element(By.LINK_TEXT, "STATISTICS").click()
    time.sleep(1)

    # Navigate to statistics tab
    driver.find_element(By.LINK_TEXT, field).click()
    time.sleep(1)

    # Open data filter tab
    driver.find_element(By.CLASS_NAME, "btn-filter").click()
    time.sleep(1)

    # Edit minimum filter to equal one
    driver.find_element(By.ID, "atleast").send_keys(Keys.BACKSPACE + '1')
    time.sleep(1)

    # Update search paramaters
    driver.find_element(By.NAME, "commit").click()
    time.sleep(1)

    return driver


def collect_outfield_data(driver, output_filename: str):

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
    while scan_pages:
        try:
            summary_df, _ = collect_table_data(driver, headers,
                                               summary_df)
            time.sleep(1)

            # Return to previous page
            driver.find_element(By.LINK_TEXT, "Next").click()
            time.sleep(1)

        except BaseException:

            # Exit while loop
            scan_pages = False

    # Clean batting summary dataframe
    summary_df = summary_df.reset_index().drop(columns=['index'])

    # Write data to csv file
    summary_df.to_csv(output_filename, index=False)

    return driver


def collect_batting_data(driver):

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
    while scan_pages:
        try:
            summary_df, page_df = collect_table_data(driver, headers,
                                                     summary_df)
            time.sleep(1)

            # Iterate through each player and collect their batting data
            for player in page_df['PLAYER'].tolist():

                # Collect individual batting data
                batting_stats_df = \
                    collect_individual_player_batting_data(driver, player,
                                                           batting_stats_df)

            # Return to previous page
            driver.find_element(By.LINK_TEXT, "Next").click()
            time.sleep(1)

        except BaseException:

            # Exit while loop
            scan_pages = False

    # Clean batting summary dataframe
    summary_df = summary_df.reset_index().drop(columns=['index'])

    # Clean the individual batting stats dataframe
    batting_stats_df = batting_stats_df.reset_index() \
        .drop(columns=['index', 'SEASON', 'GAMES', 'INNS', 'NOT OUTS', 'RUNS',
                       'HIGH SCORE', 'AVG', '50s', '100s'])

    # Join both dataframes on player name
    batting_df = summary_df.merge(batting_stats_df, left_on='PLAYER',
                                  right_on='PLAYER', how='inner')

    # Write data to csv file
    batting_df.to_csv('batting_data.csv', index=False)

    return driver


def collect_individual_player_batting_data(driver, player_name,
                                           batting_stats_df):

    # Open indivial player batting stats
    driver.find_element(By.LINK_TEXT, player_name).click()

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

    # Convert data into dataframe and append player name to dataframe
    page_df = pd.DataFrame(data, columns=batting_stats_df.columns)
    page_df['PLAYER'] = player_name

    # Union existing data with new data
    batting_stats_df = pd.concat([batting_stats_df, page_df])

    # Filter out old data - only keep data from the current season
    batting_stats_df = batting_stats_df[batting_stats_df['SEASON'] ==
                                        str(datetime.now().year)]

    # Return to previous page
    driver.back()

    return batting_stats_df


def collect_table_data(driver, columns, df):

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
