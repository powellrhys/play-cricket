# Import selenium dependencies
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

# Import python dependencies
from datetime import datetime
import pandas as pd
import logging

# Import data functions
from functions.data_functions import (
    read_csv_from_blob
)

# Import setup functions
from functions.setup_functions import (
    Variables
)

def collect_match_report_ids(
    logger: logging.Logger,
    driver: WebDriver,
    club: str
) -> tuple[WebDriver, list, logging.Logger]:
    """
    Function to collect match report ids

    Args:
        logger (logging.Logger): Python logging object
        driver (WebDriver): Selenium Webdriver
        club (str): Club name

    Raise: None

    Return
        driver (WebDriver): Selenium WebDriver
        result_ids (list): List of report ids
    """
    try:
        # Open chrome on specific play cricket club
        driver.get(f"http://{club}.play-cricket.com/Matches?tab=Result")

        # Locate the dropdown element
        dropdown = Select(driver.find_element(By.ID, "view_by"))

        # Select the "By Year" option by value
        dropdown.select_by_value("year")

        # Locate the dropdown element
        dropdown = Select(driver.find_element(By.ID, "team_id"))

        # Select "1st XI" by its value
        dropdown.select_by_visible_text("1st XI")

        # Generate a list of years from this year to 5 years ago
        years = [str(datetime.now().year - i) for i in range(6)]
        years.reverse()

        # Locate the dropdown by its ID
        dropdown_element = driver.find_element(By.ID, "season_id")
        dropdown = Select(dropdown_element)

        # Create a dictionary mapping inner text to values
        option_map = {option.get_attribute("innerText").split(' ')[-1].strip(): option.get_attribute("value")
                      for option in dropdown.options}

        # Iterate through seasons and fetch match report ids
        result_ids = []
        for year in years:

            # Locate the dropdown by its ID
            dropdown_element = driver.find_element(By.ID, "season_id")
            dropdown = Select(dropdown_element)

            # Select reports from variable year
            driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                                  dropdown_element,
                                  str(option_map[year]))

            # Find all result links
            result_links = driver.find_elements(By.CLASS_NAME, "link-scorecard")

            # Extract result IDs from the href attributes
            yearly_result_ids = [link.get_attribute("href").split("/")[-1] for link in result_links]

            # Collect unique yearly result ids
            yearly_result_ids = list(set(yearly_result_ids))

            # Append yearly ids to result ids list
            result_ids.extend(yearly_result_ids)

    except BaseException:
        logger.error('Failed to collect match report ids')

    return driver, result_ids, logger


def analyse_match_reports(
    logger: logging.Logger,
    driver: WebDriver,
    result_ids: list,
    club: str
) -> tuple[WebDriver, pd.DataFrame, logging.Logger]:
    """
    Function to analyse play cricket match report

    Args:
        logger (logging.Logger): Python logging object
        driver (WebDriver): Selenium WebDriver
        result_ids (list): List of play cricket report ids
        club (str): Play cricket club name
    
    Raise: None

    Return:
        driver (WebDriver): Selenium WebDriver
        bowling_stats (pd.DataFrame): Bowling stats from match reports
        logger (logging.Logger): Python logging object
    """
    # Create an empty DataFrame
    bowling_stats = pd.DataFrame()

    # Iterate through match reports
    for index, result_id in enumerate(result_ids, start=1):
        try:
            # Navigate to match report
            driver.get(f"https://{club}.play-cricket.com/website/results/{result_id}")

            # Find all elements with class 'team-name'
            team_elements = driver.find_elements(By.CLASS_NAME, "team-name")

            # Identify whether game was home or away
            venue = [element.text for element in team_elements][0]
            if club.capitalize() not in venue:
                home_or_away = 'Away'
            else:
                home_or_away = 'Home'

            # Identify opponent club
            opponent = list(set([element.text for element in team_elements
                                if element.text != f'{club.capitalize()} CC' and element.text != '']))[0]

            # Find the div with class 'leaguedetail-right'
            fixture_detail = driver.find_element(By.CLASS_NAME, "leaguedetail-right")

            # Extract text
            fixture_date = fixture_detail.text.split('@')[0].strip()

            # Log out info
            logger.info(f'{index}/{len(result_ids)}: Analysing match against {opponent} '
                        f'({home_or_away[0]}) - {fixture_date}...')

        except BaseException:
            logger.error(f'Failed to Collect match report metadata from report id - {result_id}\n')
            continue

        try:
            # Wait for the SCORECARD tab to be visible and clickable
            scorecard_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "pcScorecard-tab"))
            )

            # Click the SCORECARD tab
            scorecard_tab.click()

        except BaseException:
            logger.error(f'Failed to collect data for {fixture_date} - {opponent} ({home_or_away[0]})\n')
            continue

        try:
            # Wait until the <li> elements are present
            wait = WebDriverWait(driver, 10)
            li_elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))

            # Loop through the <li> elements to find the one matching the opposition batting innings
            for li in li_elements:
                if "CC" in li.text and club.capitalize() not in li.text:
                    # Once element found - click the matching element
                    li.click()
                    break

        except Exception:
            logger.error(f"Failed to collect bowling data for {fixture_date} - {opponent} ({home_or_away[0]})\n")
            continue

        # Find all tables with class "bowler-detail"
        tables = driver.find_elements(By.CLASS_NAME, "bowler-detail")

        # Iterate through tables and extract data
        for _, table in enumerate(tables, start=1):

            # Extract table headers
            headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]

            # Extract table rows
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]

            # Extract data
            data = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = [cell.text.strip() for cell in cells]
                data.append(row_data)

            # Create a Pandas DataFrame
            df = pd.DataFrame(data, columns=headers)

            # Remove rows where any cell is an empty string
            if (df == "").any().any():
                # Convert empty cells with NaN
                df = df.replace('', pd.NA).dropna()

            # Append metadata columns to dataframe
            df['DATE'] = fixture_date
            df['OPPONENT'] = opponent
            df['VENUE'] = venue
            df['VENUE'] = df['VENUE'].apply(lambda venue: 'Home' if club.capitalize() in venue else 'Away')

            # If data collected, append to master dataframe
            if not df.empty:
                bowling_stats = pd.concat([bowling_stats, df], ignore_index=True)

    return driver, bowling_stats, logger

def filter_reports_by_bowlers(
    match_report_bowling_data: pd.DataFrame,
    vars: Variables
) -> pd.DataFrame:
    """
    Function to filter match report data to ensure all bowlers are at the club

    Args:
        match_report_bowling_data (pd.DataFrame): Bowling stats from match reports
        vars (Variables): Project Variables Class

    Raise: None

    Return:
        match_report_bowling_data (pd.DataFrame): Filtered bowling stats from reports
    """
    # Collect bowling data from blob
    bowling_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                    container_name='play-cricket',
                                    blob_name='bowling_data.csv')

    # Generate a unique list of bowlers from recent season
    bowlers = bowling_df['PLAYER'].unique()

    # Filter match report data based on recent club bowlers
    match_report_bowling_data = match_report_bowling_data[match_report_bowling_data['BOWLER'].isin(bowlers)]

    # Convert only 'date_column' to datetime, invalid dates become NaT
    match_report_bowling_data['DATE'] = pd.to_datetime(match_report_bowling_data['DATE'], errors='coerce')

    # Drop rows where 'date_column' is NaT
    match_report_bowling_data = match_report_bowling_data.dropna(subset=['DATE'])

    return match_report_bowling_data
