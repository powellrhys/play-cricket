# Import Selenium dependencies
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver

# Import email dependencies
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Import python dependencies
from bs4 import BeautifulSoup
from datetime import datetime
from io import StringIO
import pandas as pd
import smtplib
import time
import ssl


def create_email_attachment(em, df, filename):

    # Convert DataFrame to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    # Attach CSV to email
    csv_attachment = MIMEApplication(csv_data, _subtype="csv")
    csv_attachment.add_header('Content-Disposition',
                              'attachment',
                              filename=filename)
    em.attach(csv_attachment)

    return em


def email_results(club: str,
                  email_sender: str,
                  email_password: str,
                  email_reciever: str,
                  batting_df,
                  bowling_df,
                  fielding_df):

    # Define email subject and body
    subject = f'{club.upper()} CC - Stats Update'
    body = ''

    # Configure email payload
    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_reciever
    em['Subject'] = subject

    # Attach the email body
    em.attach(MIMEText(body, "plain"))
    em = create_email_attachment(em, batting_df, 'batting_data.csv')
    em = create_email_attachment(em, bowling_df, 'bowling_data.csv')
    em = create_email_attachment(em, fielding_df, 'fielding_data.csv')

    # Configure email protocol
    context = ssl.create_default_context()

    # Send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_reciever, em.as_string())


def configure_driver(driver_path: str = 'chromedriver.exe',
                     headless: bool = False):

    # Configure logging to suppress unwanted messages
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")

    if headless:
        chrome_options.add_argument("--headless")

    # Configure Driver with options
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    return driver


def login_to_play_cricket(driver, club, email, password):

    # Open chrome on specific play cricket club
    driver.get(f"http://{club}.play-cricket.com/users/sign_in")

    # Enter Password into login form
    WebDriverWait(driver, 10) \
        .until(EC.presence_of_element_located((By.ID, 'password')))
    driver.find_element(By.ID, 'password').send_keys(password)

    # Enter email into login form
    WebDriverWait(driver, 10) \
        .until(EC.presence_of_element_located((By.ID, 'email')))
    driver.find_element(By.ID, 'email').send_keys(email)

    # Click Login button
    i = 0
    while i < 5:
        try:
            # Click Submit on login form
            WebDriverWait(driver, 10) \
                .until(EC.presence_of_element_located((By.CLASS_NAME, "sc-bBHwJV")))
            driver.find_element(By.CLASS_NAME, "sc-bBHwJV").click()

        except BaseException:
            pass

        i = i + 1

    return driver


def remove_cookies_pop_up(driver):

    # Remove cookies pop up
    WebDriverWait(driver, 10) \
        .until(EC.presence_of_element_located((By.CLASS_NAME, "onetrust-close-btn-handler")))
    driver.find_element(By.CLASS_NAME, "onetrust-close-btn-handler").click()

    return driver


def query_data(driver, field: str = "BATTING"):

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
    summary_df.to_csv(f'data/{output_filename}', index=False)

    return driver, summary_df


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

    # Clean the individual batting stats dataframe
    batting_stats_df = batting_stats_df.reset_index() \
        .drop(columns=['index', 'SEASON', 'GAMES', 'INNS', 'NOT OUTS', 'RUNS',
                       'HIGH SCORE', 'AVG', '50s', '100s'])

    # Join both dataframes on player name
    batting_df = summary_df.merge(batting_stats_df, left_on='PLAYER',
                                  right_on='PLAYER', how='inner')

    # Write data to csv file
    batting_df.to_csv('data/batting_data.csv', index=False)

    return driver, batting_df


def collect_individual_player_batting_data(driver, player_name,
                                           batting_stats_df):

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

    # Convert data into dataframe and append player name to dataframe
    page_df = pd.DataFrame(data, columns=batting_stats_df.columns)
    page_df['PLAYER'] = player_name

    # Union existing data with new data
    batting_stats_df = pd.concat([batting_stats_df, page_df])

    # Filter out old data - only keep data from the current season
    batting_stats_df = batting_stats_df[batting_stats_df['SEASON'] == str(datetime.now().year)]

    # Return to previous page
    driver.back()

    return batting_stats_df


def collect_table_data(driver, columns, df, rank):

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
