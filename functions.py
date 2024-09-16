from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


def configure_driver():

    # Configure logging to suppress unwanted messages
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    return driver


def login_to_play_cricket(driver, club, email, password):

    driver.get(f"http://{club}.play-cricket.com/users/sign_in")

    time.sleep(2)

    password_element = driver.find_element(By.ID, 'password')
    password_element.send_keys(password)

    email_element = driver.find_element(By.ID, 'email')
    email_element.send_keys(email)

    i = 0
    while i < 5:
        try:
            login_submit_button = driver \
                .find_element(By.CLASS_NAME, "sc-bBHwJV")
            login_submit_button.click()
            time.sleep(1)
        except BaseException:
            pass

        i = i + 1

    time.sleep(3)

    return driver


def remove_cookies_pop_up(driver):

    time.sleep(5)

    cookie_popup = driver \
        .find_element(By.CLASS_NAME, "onetrust-close-btn-handler")
    cookie_popup.click()

    time.sleep(1)

    return driver


def query_batting_data(driver):

    statistics_tab = driver.find_element(By.LINK_TEXT, "STATISTICS")
    statistics_tab.click()

    time.sleep(1)

    filters_button = driver.find_element(By.CLASS_NAME, "btn-filter")
    filters_button.click()

    time.sleep(1)

    min_innings_input = driver.find_element(By.ID, "atleast")
    min_innings_input.send_keys(Keys.BACKSPACE + '1')

    time.sleep(1)

    min_innings_input = driver.find_element(By.NAME, "commit")
    min_innings_input.click()

    time.sleep(1)

    return driver


def collect_batting_data_summary_data(driver):

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('table')

    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    summary_df = pd.DataFrame(columns=headers)

    indiviaul_batting_stats_columns = \
        ['SEASON', 'GAMES', 'INNS', 'NOT OUTS', 'RUNS', 'HIGH SCORE',
         'AVG', '50s', '100s', '4s', '6s', 'DUCKS', '%TEAM RUNS', 'PLAYER']

    batting_stats_df = \
        pd.DataFrame(columns=indiviaul_batting_stats_columns)

    scan_pages = True
    while scan_pages:
        try:
            summary_df, page_df = collect_table_data(driver, headers,
                                                     summary_df)

            time.sleep(1)

            for player in page_df['PLAYER'].tolist():

                batting_stats_df = \
                    collect_individual_player_batting_data(driver, player,
                                                           batting_stats_df)

            next_button = driver.find_element(By.LINK_TEXT, "Next")
            next_button.click()

            time.sleep(1)

        except BaseException:
            scan_pages = False

    summary_df = summary_df.reset_index().drop(columns=['index'])
    batting_stats_df = batting_stats_df.reset_index() \
        .drop(columns=['index', 'SEASON', 'GAMES', 'INNS', 'NOT OUTS', 'RUNS',
                       'HIGH SCORE', 'AVG', '50s', '100s'])

    batting_df = summary_df.merge(batting_stats_df, left_on='PLAYER',
                                  right_on='PLAYER', how='inner')

    batting_df.to_csv('batting_data.csv', index=False)

    # summary_df.to_csv('batting.csv', index=False)
    # batting_stats_df.to_csv('individual_batting.csv', index=False)

    return driver


def collect_individual_player_batting_data(driver, player_name,
                                           batting_stats_df):

    play_button = driver.find_element(By.LINK_TEXT, player_name)
    play_button.click()

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('table')

    rows = []
    for tr in table.find_all('tr')[1:]:
        cells = tr.find_all('td')
        row = [cell.text.strip() for cell in cells]
        rows.append(row)

    data = [row for row in rows if len(row) == len(batting_stats_df.columns)]

    page_df = pd.DataFrame(data, columns=batting_stats_df.columns)
    page_df['PLAYER'] = player_name

    batting_stats_df = pd.concat([batting_stats_df, page_df])

    batting_stats_df = batting_stats_df[batting_stats_df['SEASON'] ==
                                        str(datetime.now().year)]

    driver.back()

    return batting_stats_df


def collect_table_data(driver, columns, df):

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('table')

    rows = []
    for tr in table.find_all('tr')[1:]:
        cells = tr.find_all('td')
        row = [cell.text.strip() for cell in cells]
        rows.append(row)

    data = [row for row in rows if len(row) == len(columns)]

    page_df = pd.DataFrame(data, columns=columns)

    df = pd.concat([df, page_df])

    return df, page_df
