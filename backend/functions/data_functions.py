# Import python dependencies
from azure.storage.blob import BlobServiceClient
import pandas as pd
import requests
import io
import os

# Import project dependencies
from functions.logging_functions import (
    log_function_use,
    logger
)

class Variables:
    """
    Class to collect environmental variables from .env file

    Args: None

    Raise: None

    Return: None
    """
    def __init__(self):

        # Collect environmental variables
        self.club = os.getenv('club')
        self.site_id = os.getenv('site_id')
        self.api_token = os.getenv('api_token')
        self.blob_connection_string = os.getenv('blob_connection_string')

class APIService:
    def __init__(
            self,
            api_token: str,
            site_id: int,
            variables: Variables
    ) -> None:
        """
        """
        self._api_token = api_token
        self._site_id = site_id
        self.vars = variables
        self.base_url = "http://play-cricket.com/api/v2/"
        self.logger = logger

    @log_function_use(logger)
    def collect_match_ids(
        self,
        seasons: list
    ) -> None:
        """
        """
        url = self.base_url + "matches.json"
        self.match_ids = []
        for season in seasons:

            params = {
                "site_id": self._site_id,
                "api_token": self._api_token,
                "season": season
            }
            response = requests.get(url=url, params=params)
            matches = response.json()['matches']

            ids = [
                match['id']
                for match in matches
                if (
                    self.vars.club in match['home_club_name'].lower() and
                    match['home_team_name'] in ["1st XI", "2nd XI"]
                ) or (
                    self.vars.club in match['away_club_name'].lower() and
                    match['away_team_name'] in ["1st XI", "2nd XI"]
                )
            ]

            self.match_ids.extend(ids)

    @log_function_use(logger)
    def collect_match_data(
        self
    ) -> None:
        """
        """
        url = self.base_url + 'match_detail.json'

        self.all_batting_df = pd.DataFrame()
        self.all_bowling_df = pd.DataFrame()
        self.all_bowling_dismissals_df = pd.DataFrame()
        for i, match_id in enumerate(self.match_ids, start=1):

            params = {
                "match_id": match_id,
                "api_token": self._api_token
            }
            response = requests.get(url=url, params=params)
            data = response.json()

            match_date = data['match_details'][0]['match_date']
            venue = data['match_details'][0]['home_club_name']

            if self.vars.club in venue.lower():
                home_away = 'HOME'
                opponent = data['match_details'][0]['away_club_name']
            else:
                home_away = 'AWAY'
                opponent = data['match_details'][0]['home_club_name']

            innings = data['match_details'][0]['innings']

            logger.info(f"{i}/{len(self.match_ids)} - Collecting data for {match_date} | {opponent} ({home_away})")

            bowling_innings = []
            batting_innings = []
            bowling_dismissal_innings = []
            for inning in innings:
                if self.vars.club not in inning['team_batting_name'].lower():
                    bowling_innings = inning['bowl']
                    bowling_dismissal_innings = inning['bat']

                if self.vars.club in inning['team_batting_name'].lower():
                    batting_innings = inning['bat']

            if bowling_innings:
                bowling_df = pd.DataFrame(bowling_innings)
                bowling_df['home_away'] = home_away
                bowling_df['opponent'] = opponent
                bowling_df['match_date'] = match_date
                bowling_df['match_date'] = pd.to_datetime(bowling_df['match_date'], format='%d/%m/%Y')
                bowling_df['year'] = bowling_df['match_date'].dt.year

                self.all_bowling_df = pd.concat([self.all_bowling_df, bowling_df])

            if batting_innings:
                batting_df = pd.DataFrame(batting_innings)
                batting_df['home_away'] = home_away
                batting_df['opponent'] = opponent
                batting_df['match_date'] = match_date
                batting_df['match_date'] = pd.to_datetime(batting_df['match_date'], format='%d/%m/%Y')
                batting_df['year'] = batting_df['match_date'].dt.year

                dismissal_map = {
                    'b': 'Bowled',
                    'ct': 'Caught',
                    'lbw': 'LBW',
                    'not out': 'Not Out',
                    'run out': 'Run Out',
                    'did not bat': 'Did Not Bat',
                    'st': 'Stumped'
                }

                batting_df['how_out'] = batting_df['how_out'].map(dismissal_map).fillna('Other')

                batting_df = batting_df.drop(columns=['bowler_id', 'bowler_name', 'fielder_name', 'fielder_id'],
                                             axis=0)

                self.all_batting_df = pd.concat([self.all_batting_df, batting_df])

            if bowling_dismissal_innings:
                bowling_dismissal_df = pd.DataFrame(bowling_dismissal_innings)
                bowling_dismissal_df['home_away'] = home_away
                bowling_dismissal_df['opponent'] = opponent
                bowling_dismissal_df['match_date'] = match_date
                bowling_dismissal_df['match_date'] = pd.to_datetime(bowling_dismissal_df['match_date'],
                                                                    format='%d/%m/%Y')
                bowling_dismissal_df['year'] = bowling_dismissal_df['match_date'].dt.year

                dismissal_map = {
                    'b': 'Bowled',
                    'ct': 'Caught',
                    'lbw': 'LBW',
                    'not out': 'Not Out',
                    'run out': 'Run Out',
                    'did not bat': 'Did Not Bat',
                    'st': 'Stumped'
                }

                bowling_dismissal_df['how_out'] = bowling_dismissal_df['how_out'].map(dismissal_map).fillna('Other')

                bowling_dismissal_df = bowling_dismissal_df[['bowler_id', 'bowler_name', 'how_out', 'year']]

                self.all_bowling_dismissals_df = pd.concat([self.all_bowling_dismissals_df, bowling_dismissal_df])

    @log_function_use(logger)
    def generate_how_out_df(self) -> None:
        """
        """
        self.how_out_df = self.all_batting_df \
            .groupby(['batsman_name', 'year'])['how_out'].value_counts().unstack(fill_value=0) \
            .reset_index()

        self.how_out_df = self.how_out_df.rename(columns={
            'batsman_name': 'player',
            'year': 'season'
        })

        self.how_out_df.columns = [col.upper() for col in self.how_out_df.columns]

    @log_function_use(logger)
    def generate_batting_summary_df(self) -> None:
        """
        """
        summary_batting_df = self.all_batting_df
        summary_batting_df['runs'] = pd.to_numeric(summary_batting_df['runs'], errors='coerce')
        summary_batting_df['fours'] = pd.to_numeric(summary_batting_df['fours'], errors='coerce')
        summary_batting_df['sixes'] = pd.to_numeric(summary_batting_df['sixes'], errors='coerce')
        summary_batting_df['50s'] = ((summary_batting_df['runs'] >= 50) &
                                     (summary_batting_df['runs'] < 100)).astype(int)
        summary_batting_df['100s'] = (summary_batting_df['runs'] >= 100).astype(int)
        summary_batting_df['ducks'] = (summary_batting_df['runs'] == 0).astype(int)
        summary_batting_df['games'] = 1
        summary_batting_df['inns'] = (summary_batting_df['how_out'] != 'Did Not Bat').astype(int)

        summary_batting_df = summary_batting_df \
            .groupby(['batsman_name', 'year']) \
            .agg({
                'games': 'sum',
                'inns': 'sum',
                'runs': ['sum', 'max'],
                '50s': 'sum',
                '100s': 'sum',
                'fours': 'sum',
                'sixes': 'sum',
                'ducks': 'sum',
            }).reset_index()

        input_columns = ['batsman_name', 'year', 'games', 'inns', 'runs_sum', 'runs_max', '50s_sum',
                         '100s_sum', 'fours_sum', 'sixes_sum', 'ducks']
        output_columns = ['PLAYER', 'SEASON', 'GAMES', 'INNS', 'RUNS', 'HIGH SCORE',
                          '50s', '100s', '4s', '6s', 'DUCKS']

        summary_batting_df.columns = input_columns
        summary_batting_df.rename(columns=dict(zip(input_columns, output_columns)), inplace=True)

        self.summary_batting_df = summary_batting_df

    @log_function_use(logger)
    def generate_bowling_summary_df(self) -> None:
        """
        """
        summary_bowling_df = self.all_bowling_df
        for column in ['overs', 'maidens', 'runs', 'wides', 'wickets', 'no_balls']:
            summary_bowling_df[column] = pd.to_numeric(summary_bowling_df[column], errors='coerce')

        summary_bowling_df['balls'] = summary_bowling_df['overs'].apply(lambda x: int(x) * 6 + round((x - int(x)) * 10))

        summary_bowling_df = summary_bowling_df \
            .groupby(
                ['bowler_name', 'year', 'home_away'])[
                    ['balls', 'maidens', 'runs', 'wides', 'wickets', 'no_balls']] \
            .sum().reset_index()

        # Convert balls back to overs
        summary_bowling_df['overs'] = summary_bowling_df['balls'].apply(lambda x: f"{x // 6}.{x % 6}")

        input_columns = ['bowler_name', 'year', 'home_away', 'balls',
                         'maidens', 'runs', 'wides', 'no_balls', 'wickets', 'overs',]
        output_columns = ['PLAYER', 'SEASON', 'HOME/AWAY', 'BALLS', 'MAIDENS',
                          'RUNS', 'WIDES', 'NO BALLS', 'WICKETS', 'OVERS']

        summary_bowling_df.columns = input_columns
        summary_bowling_df.rename(columns=dict(zip(input_columns, output_columns)), inplace=True)

        self.summary_bowling_df = summary_bowling_df

    @log_function_use(logger)
    def generate_bowling_dismissals_summary_df(self) -> None:
        """
        """
        bowling_dismissal_summary_df = self.all_bowling_dismissals_df.dropna(subset=['bowler_name', 'how_out'])

        # Group by bowler_name and year, then count each how_out
        bowling_dismissal_summary_df = bowling_dismissal_summary_df \
            .groupby(['bowler_name', 'year'])['how_out'] \
            .value_counts() \
            .unstack(fill_value=0)

        # Reset index to make 'bowler_name' and 'year' into columns
        bowling_dismissal_summary_df = bowling_dismissal_summary_df.reset_index()

        # Remove rows with blank or missing bowler_name
        bowling_dismissal_summary_df = \
            bowling_dismissal_summary_df[bowling_dismissal_summary_df['bowler_name'].str.strip() != '']

        bowling_dismissal_summary_df = \
            bowling_dismissal_summary_df[['bowler_name', 'year', 'Bowled', 'Caught', 'LBW', 'Stumped']]

        input_columns = ['bowler_name', 'year', 'Bowled', 'Caught', 'LBW', 'Stumped']
        output_columns = ['PLAYER', 'SEASON', 'BOWLED', 'CAUGHT', 'LBW', 'STUMPED']

        bowling_dismissal_summary_df.columns = input_columns
        bowling_dismissal_summary_df.rename(columns=dict(zip(input_columns, output_columns)), inplace=True)

        self.bowling_dismissal_summary_df = bowling_dismissal_summary_df

def write_df_to_blob(
    df: pd.DataFrame,
    connection_string: str,
    container_name: str,
    blob_name: str
) -> None:
    """
    Function to write pandas dataframe to azure blob storage account

    Args:
        df (pd.DataFrame): Pandas dataframe to write to blob
        connection_string (str): Azure blob storage connection string
        container_name (str): Azure container name
        blob_name (str): File name for blob written to blob

    Raise: None

    Return: None
    """
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to the container
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Convert DataFrame to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Upload the CSV to Blob Storage
    blob_client.upload_blob(csv_buffer.getvalue(), overwrite=True)
