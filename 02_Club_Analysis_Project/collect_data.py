from dotenv import load_dotenv
import warnings
import logging
import os

from functions import \
    query_data, \
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


# Import Selenium dependencies
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver

# Open chrome on specific play cricket club
driver.get(f"http://creigiau.play-cricket.com/Matches?tab=Result")

import time

time.sleep(5)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# # Set up WebDriver (replace with the appropriate driver)
# driver = webdriver.Chrome()

# # Load the webpage
# driver.get("URL_OF_THE_PAGE")

# Locate the dropdown element
dropdown = Select(driver.find_element(By.ID, "view_by"))

# Select the "By Year" option by value
dropdown.select_by_value("year")

# Locate the dropdown element
dropdown = Select(driver.find_element(By.ID, "team_id"))

# Select "1st XI" by its value
dropdown.select_by_value("35854")

time.sleep(2)

# Find all result links
result_links = driver.find_elements(By.CLASS_NAME, "link-scorecard")

# Extract result IDs from the href attributes
result_ids = [link.get_attribute("href").split("/")[-1] for link in result_links]

result_ids = list(set(result_ids))

import pandas as pd

# Create an empty DataFrame
bowling_stats = pd.DataFrame()

for result_id in result_ids:

    is_home = True

    driver.get(f"https://creigiau.play-cricket.com/website/results/{result_id}")
    # driver.get(f"https://creigiau.play-cricket.com/website/results/6555688")

    try:

        # Wait for the SCORECARD tab to be visible and clickable
        scorecard_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "pcScorecard-tab"))
        )

        # Click the SCORECARD tab
        scorecard_tab.click()

    except:
        continue

    try:
        # Wait until the <li> elements are present
        wait = WebDriverWait(driver, 10)
        li_elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))

        # Loop through the <li> elements to find the one matching "Creigiau CC"
        for li in li_elements:
            if "CC" in li.text and "Creigiau" not in li.text:
                li.click()  # Click the matching element
                print("Creigiau CC Bowling Innings clicked")
                break  # Exit loop after clicking

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(2)

    # # Wait for the table to load
    # WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.CLASS_NAME, "bowler-detail"))
    # )

    # # Find the table
    # table = driver.find_element(By.CLASS_NAME, "bowler-detail")

    # # Extract table headers
    # headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]

    # # Extract table rows
    # rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip the header row

    # # Extract data
    # data = []
    # for row in rows:
    #     cells = row.find_elements(By.TAG_NAME, "td")
    #     row_data = [cell.text.strip() for cell in cells]
    #     data.append(row_data)

    # import pandas as pd

    # # Create a Pandas DataFrame
    # df = pd.DataFrame(data, columns=headers)

    # # Print or save the DataFrame
    # print(df)

    # Find all elements with class 'team-name'
    team_elements = driver.find_elements(By.CLASS_NAME, "team-name")

    # Extract text from each element
    opponent = list(set([element.text for element in team_elements if element.text != 'Creigiau CC' and element.text != '']))[0]
    print(opponent)

    #  Find the div with class 'leaguedetail-right'
    fixture_detail = driver.find_element(By.CLASS_NAME, "leaguedetail-right")

    # Extract text
    fixture_date = fixture_detail.text.split('@')[0].strip()

    # Print the extracted text
    print(fixture_date)

    import pandas as pd

    # Find all tables with class "bowler-detail"
    tables = driver.find_elements(By.CLASS_NAME, "bowler-detail")

    # List to store DataFrames
    dfs = []

    # Iterate through tables and extract data
    for index, table in enumerate(tables, start=1):

        # Extract table headers
        headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]

        # Extract table rows
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip the header row

        # Extract data
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text.strip() for cell in cells]
            data.append(row_data)

        import pandas as pd

        # Create a Pandas DataFrame
        df = pd.DataFrame(data, columns=headers)

        if all(all(cell == '' for cell in row) for row in data):
            is_home = not is_home

        df['DATE'] = fixture_date
        df['OPPONENT'] = opponent
        df['HOME'] = is_home
        columns = [col for col in df.columns if col != '']

        if len(columns) > 3:
            bowling_stats = pd.concat([bowling_stats, df], ignore_index=True)

        # print(is_home)

        # # Create a Pandas DataFrame
        # df = pd.DataFrame(data, columns=headers)
        # Print or save the DataFrame

        # print(df)
    #     rows = table.find_elements(By.TAG_NAME, "tr")

    #     table_data = []
    #     for row in rows:
    #         cells = row.find_elements(By.TAG_NAME, "td")
    #         row_data = [cell.text for cell in cells]
    #         if row_data:  # Avoid empty rows
    #             table_data.append(row_data)

    #     # Convert table data into DataFrame
    #     df = pd.DataFrame(table_data)
    #     dfs.append(df)

    # # Combine all tables into one DataFrame
    # final_df = pd.concat(dfs, ignore_index=True)

    # # Print DataFrame
    # print(final_df)

    # time.sleep(5)

print(bowling_stats)

# Write data to csv file
bowling_stats.to_csv('data/bowling_stats.csv', index=False)

# Loop through each result ID and visit the corresponding page
# for result_id in result_ids:
    # result_url = f"https://example.com/website/results/{result_id}"  # Update with the correct base URL
    # driver.get(result_url)
    # print(f"Visiting: {result_id}")
    
# time.sleep(2)  # 

# Alternative: Select by visible text
# dropdown.select_by_visible_text("By Year")

# Alternative: Select by index (if known)
# dropdown.select_by_index(1)  # Assuming "By Year" is the second option (index starts from 0)

# Close the driver after some time (optional)
# driver.quit()
