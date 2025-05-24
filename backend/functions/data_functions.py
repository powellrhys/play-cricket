# Import python dependencies
from azure.storage.blob import BlobServiceClient
import pandas as pd
import requests
import io
import os

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
                    self.vars.club in match['home_club_name'] and
                    match['home_team_name'] in ["1st XI"]#, "2nd XI"]
                ) or (
                    self.vars.club in match['away_club_name'] and
                    match['away_team_name'] in ["1st XI"]#, "2nd XI"]
                )
            ]

            self.match_ids.extend(ids)

    def collect_match_data(
        self
    ) -> None:
        """
        """
        url = self.base_url + 'match_detail.json'

        self.all_batting_df = pd.DataFrame()
        self.all_bowling_df = pd.DataFrame()
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

            print(f"{i}/{len(self.match_ids)} - Collecting data for {match_date} | {opponent} ({home_away})")

            bowling_innings = []
            batting_innings = []
            for inning in innings:
                if self.vars.club not in inning['team_batting_name'].lower():
                    bowling_innings = inning['bowl']

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
                batting_df = batting_df.drop(columns=['bowler_id',
                                                      'bowler_name',
                                                      'fielder_name',
                                                      'fielder_id'],
                                             axis=0)
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

                self.all_batting_df = pd.concat([self.all_batting_df, batting_df])

    def generate_how_out_df(self) -> None:
        """
        """
        self.how_out_df = self.all_batting_df \
            .groupby(['batsman_name', 'year'])['how_out'].value_counts().unstack(fill_value=0) \
            .reset_index()

        self. how_out_df = self.how_out_df.rename(columns={
            'batsman_name': 'player',
            'year': 'season'
        })

        self.how_out_df.columns = [col.upper() for col in self.how_out_df.columns]


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


def read_csv_from_blob(
    connection_string: str,
    container_name: str,
    blob_name: str
) -> pd.DataFrame:
    """
    Function to read csv files from blob storage

    Args:
       connection_string (str): Azure storage account connection string
       container_name (str): Azure storage account container name
       blob_name (str): Azure storage account file name

    Raise:
        TypeError: If input values are not strings

    Return:
        df (pd.Dataframe): Pandas dataframe generated from csv data stored in a blob storage
    """
    # Ensure input variables are strings
    for arg_name, arg_value in locals().items():
        if not isinstance(arg_value, str):
            raise TypeError(f"{arg_name} must be a string, but got {type(arg_value).__name__}")

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Download the blob content
    blob_data = blob_client.download_blob()
    csv_content = blob_data.content_as_text()

    # Convert CSV content to DataFrame
    df = pd.read_csv(io.StringIO(csv_content))

    return df
