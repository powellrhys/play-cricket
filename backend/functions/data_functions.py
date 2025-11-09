# Import dependencies
from backend.functions.logging_functions import log_function_use, logger
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
    """
    Class to interact, collect and transform data from the play cricket api service.
    """
    def __init__(
            self,
            api_token: str,
            site_id: int,
            variables: Variables
    ) -> None:
        """
        Initialize the API client with authentication and configuration settings.

        Args:
            api_token (str): The API token used for authenticating requests to the Play-Cricket API.
            site_id (int): The unique identifier for the site associated with this API client.
            variables (Variables): An instance of the Variables class containing runtime or configuration variables.
        """
        # Initialise class variables
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
        Collect match IDs for specified seasons involving the target club's 1st XI or 2nd XI teams.

        This method queries the Play-Cricket API for each given season, filters the matches
        to include only those where the home or away club name matches the configured club name
        and the team is either "1st XI" or "2nd XI", and stores their match IDs.

        Args:
            seasons (list): A list of season years (as integers or strings) to retrieve matches from.

        Side Effects:
            Populates self.match_ids with a list of relevant match IDs.

        Return: None
        """
        # Define api endpoint and empty match ids list
        url = self.base_url + "matches.json"
        self.match_ids = []

        # Iterate through seasons list
        for season in seasons:

            # Define request parameters
            params = {
                "site_id": self._site_id,
                "api_token": self._api_token,
                "season": season
            }

            # Execute request
            response = requests.get(url=url, params=params)
            matches = response.json()['matches']

            # Collect match ids for 1st and 2nd XI games
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

            # Append ids to match ids list
            self.match_ids.extend(ids)

    def append_metadata_to_df(
        self,
        df: pd.DataFrame,
        home_away: str,
        opponent: str,
        match_date: str
    ) -> pd.DataFrame:
        """
        Appends match metadata to a DataFrame and processes dismissal information if present.

        Parameters:
            df (pd.DataFrame): The input DataFrame containing match data.
            home_away (str): Indicator of whether the match was played at home or away.
            opponent (str): Name of the opposing team.
            match_date (str): Match date in the format 'dd/mm/yyyy'.

        Returns:
            pd.DataFrame: The modified DataFrame with appended metadata and processed 'how_out' column if present.

        Notes:
            - Adds 'home_away', 'opponent', and 'match_date' columns to the DataFrame.
            - Converts 'match_date' to datetime and extracts the year into a new 'year' column.
            - If the 'how_out' column exists, maps its values to standardized dismissal types.
        """
        # Append metadata to dataframe
        df['home_away'] = home_away
        df['opponent'] = opponent
        df['match_date'] = match_date
        df['match_date'] = pd.to_datetime(df['match_date'], format='%d/%m/%Y')
        df['year'] = df['match_date'].dt.year

        # If how_out column present in dataframe, perform necessary casting
        if 'how_out' in df.columns:

            # Define dismissal map
            dismissal_map = {
                'b': 'Bowled',
                'ct': 'Caught',
                'lbw': 'LBW',
                'not out': 'Not Out',
                'run out': 'Run Out',
                'did not bat': 'Did Not Bat',
                'st': 'Stumped'
            }

            # Perform mapping on how_out columns (fill NaN values with other value)
            df['how_out'] = df['how_out'].map(dismissal_map).fillna('Other')

        return df

    @log_function_use(logger)
    def collect_match_data(
        self
    ) -> None:
        """
            Collects and processes match data for a predefined list of match IDs.

            This method retrieves detailed match information via an API, including
            batting, bowling, and dismissal data for each match. It appends relevant
            metadata (match date, opponent, home/away status) to each dataset and
            stores the aggregated results in instance attributes:
            - `self.all_batting_df`
            - `self.all_bowling_df`
            - `self.all_bowling_dismissals_df`

            The method determines whether each match was home or away based on the venue,
            and processes data accordingly for both innings (batting and bowling). It limits
            the data collection to the first 6 match IDs.

            Returns:
                None

            Notes:
                - Requires `self.base_url`, `self.match_ids`, `self._api_token`, and `self.vars.club` to be defined.
                - Makes HTTP GET requests to fetch match details in JSON format.
                - Uses `append_metadata_to_df` to enrich each DataFrame with consistent metadata.
                - Drops certain unused columns from the batting DataFrame before storing.
                - Filters and stores only relevant columns from the dismissal data.
                - Logs progress for each processed match.
            """
        # Define request url
        url = self.base_url + 'match_detail.json'

        # Define empty dataframes for later union
        self.all_batting_df = pd.DataFrame()
        self.all_bowling_df = pd.DataFrame()
        self.all_bowling_dismissals_df = pd.DataFrame()

        # Iterate through each match_id to collect  match data
        for i, match_id in enumerate(self.match_ids, start=1):

            # Define request parameters
            params = {
                "match_id": match_id,
                "api_token": self._api_token
            }

            # Execute request to collect match data
            response = requests.get(url=url, params=params)
            data = response.json()

            # Collect match date and venue from payload
            match_date = data['match_details'][0]['match_date']
            venue = data['match_details'][0]['home_club_name']

            # Identify if match was home or away and collect opponent club name
            if self.vars.club in venue.lower():
                home_away = 'HOME'
                opponent = data['match_details'][0]['away_club_name']
            else:
                home_away = 'AWAY'
                opponent = data['match_details'][0]['home_club_name']

            # Collect innings data
            innings = data['match_details'][0]['innings']

            # Log iteration
            logger.info(f"{i}/{len(self.match_ids)} - Collecting data for {match_date} | {opponent} ({home_away})")

            # Define empty innings list objects
            bowling_innings = []
            batting_innings = []
            bowling_dismissal_innings = []

            # Iterate through innings
            for inning in innings:

                # Collect bowling data from fielding innings
                if self.vars.club not in inning['team_batting_name'].lower():
                    bowling_innings = inning['bowl']
                    bowling_dismissal_innings = inning['bat']

                # Collect batting data from batting innings
                if self.vars.club in inning['team_batting_name'].lower():
                    batting_innings = inning['bat']

            # Generate bowling innings dataframe
            if bowling_innings:
                bowling_df = pd.DataFrame(bowling_innings)
                bowling_df = self.append_metadata_to_df(df=bowling_df,
                                                        home_away=home_away,
                                                        opponent=opponent,
                                                        match_date=match_date)

                # Union data to existing data
                self.all_bowling_df = pd.concat([self.all_bowling_df, bowling_df])

            # Generate batting innings dataframe
            if batting_innings:
                batting_df = pd.DataFrame(batting_innings)
                batting_df = self.append_metadata_to_df(df=batting_df,
                                                        home_away=home_away,
                                                        opponent=opponent,
                                                        match_date=match_date)

                # Drop unwanted columns
                batting_df = batting_df.drop(columns=['bowler_id', 'bowler_name', 'fielder_name', 'fielder_id'],
                                             axis=0)

                # Union data to existing data
                self.all_batting_df = pd.concat([self.all_batting_df, batting_df])

            # Generate bowling dismissal data
            if bowling_dismissal_innings:
                bowling_dismissal_df = pd.DataFrame(bowling_dismissal_innings)
                bowling_dismissal_df = self.append_metadata_to_df(df=bowling_dismissal_df,
                                                                  home_away=home_away,
                                                                  opponent=opponent,
                                                                  match_date=match_date)

                # Remove unwanted columns
                bowling_dismissal_df = bowling_dismissal_df[['bowler_id', 'bowler_name', 'how_out', 'year']]

                # Union data to existing data
                self.all_bowling_dismissals_df = pd.concat([self.all_bowling_dismissals_df, bowling_dismissal_df])

    @log_function_use(logger)
    def generate_how_out_df(self) -> None:
        """
        Collects and processes match data for a predefined list of match IDs.

        This method retrieves detailed match information via an API, including
        batting, bowling, and dismissal data for each match. It appends relevant
        metadata—such as match date, opponent, and home/away status—to each dataset,
        and stores the aggregated results in the following instance attributes:
            - `self.all_batting_df`
            - `self.all_bowling_df`
            - `self.all_bowling_dismissals_df`

        The method determines whether the match was played at home or away based on the venue,
        then processes and enriches the data for both innings (batting and bowling).
        Only the first 6 match IDs in `self.match_ids` are processed.

        Returns:
            None

        Notes:
            - Requires `self.base_url`, `self.match_ids`, `self._api_token`, and `self.vars.club` to be defined.
            - Makes HTTP GET requests to retrieve match details in JSON format.
            - Calls `append_metadata_to_df` to enrich each DataFrame with consistent metadata.
            - Drops unused columns from the batting DataFrame before storing.
            - Selects and stores only relevant columns from the dismissal data.
            - Logs progress for each processed match.
        """
        # Group data by batsman and year and count each instance of how_out
        self.how_out_df = self.all_batting_df \
            .groupby(['batsman_name', 'year'])['how_out'].value_counts().unstack(fill_value=0) \
            .reset_index()

        # Rename columns ready for blob write
        self.how_out_df = self.how_out_df.rename(columns={
            'batsman_name': 'player',
            'year': 'season'
        })

        # Make all columns upper case
        self.how_out_df.columns = [col.upper() for col in self.how_out_df.columns]

    @log_function_use(logger)
    def generate_batting_summary_df(self) -> None:
        """
        Generates a season-wise batting summary DataFrame from individual match data.

        This method processes the aggregated batting data stored in `self.all_batting_df` to
        compute season-level statistics for each batsman. Metrics calculated include total runs,
        high score, number of 50s and 100s, boundary counts, and ducks. It also computes games played
        and innings batted.

        The summarized results are stored in the `self.summary_batting_df` attribute with
        standardized column names suitable for reporting or further analysis.

        Returns:
            None

        Notes:
            - Assumes `self.all_batting_df` is already populated and contains columns such as
            'runs', 'fours', 'sixes', 'how_out', and 'batsman_name'.
            - Handles type coercion for numeric fields and uses logical conditions to compute
            derived metrics (e.g., 50s, 100s, ducks).
            - Groups data by batsman and year for summarization.
            - Renames output columns to user-friendly labels.
        """
        # Convert runs columns to numeric values
        summary_batting_df = self.all_batting_df
        summary_batting_df['runs'] = pd.to_numeric(summary_batting_df['runs'], errors='coerce')
        summary_batting_df['fours'] = pd.to_numeric(summary_batting_df['fours'], errors='coerce')
        summary_batting_df['sixes'] = pd.to_numeric(summary_batting_df['sixes'], errors='coerce')

        # Calculate if runs scored equate to 0, a 50 or a 100 runs scored in a game
        summary_batting_df['50s'] = ((summary_batting_df['runs'] >= 50) &
                                     (summary_batting_df['runs'] < 100)).astype(int)
        summary_batting_df['100s'] = (summary_batting_df['runs'] >= 100).astype(int)
        summary_batting_df['ducks'] = (summary_batting_df['runs'] == 0).astype(int)

        # Create games and innings columns based on whether batter batted
        summary_batting_df['games'] = 1
        summary_batting_df['inns'] = (summary_batting_df['how_out'] != 'Did Not Bat').astype(int)

        # Perform aggregation on batters innings
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

        # Define columns before and after rename
        input_columns = ['batsman_name', 'year', 'games', 'inns', 'runs_sum', 'runs_max', '50s_sum',
                         '100s_sum', 'fours_sum', 'sixes_sum', 'ducks']
        output_columns = ['PLAYER', 'SEASON', 'GAMES', 'INNS', 'RUNS', 'HIGH SCORE',
                          '50s', '100s', '4s', '6s', 'DUCKS']

        # Rename columns
        summary_batting_df.columns = input_columns
        summary_batting_df.rename(columns=dict(zip(input_columns, output_columns)), inplace=True)

        # Store summary of batting data in a class object
        self.summary_batting_df = summary_batting_df

    @log_function_use(logger)
    def generate_bowling_summary_df(self) -> None:
        """
        Generates a home/away and season-wise bowling summary DataFrame.

        This method processes the aggregated bowling data stored in `self.all_bowling_df`
        to compute summarized bowling metrics per bowler, grouped by season and home/away status.
        It calculates totals such as balls bowled, maidens, runs conceded, wides, no balls, and wickets.

        The method converts fractional overs into actual ball counts for internal aggregation,
        then back into overs format for the final summary. The processed data is stored in
        the `self.summary_bowling_df` attribute with cleaned and user-friendly column names.

        Returns:
            None

        Notes:
            - Assumes `self.all_bowling_df` is populated and includes columns such as
            'overs', 'maidens', 'runs', 'wides', 'wickets', 'no_balls', 'bowler_name', and 'year'.
            - Converts overs (e.g., 4.3) into actual ball counts for accurate aggregation.
            - Regroups the data by bowler, season, and home/away status.
            - Reformats overs from total balls (e.g., 27 balls → '4.3').
            - Renames output columns for presentation or reporting.
        """
        # Convert columns to numeric datatype
        summary_bowling_df = self.all_bowling_df
        for column in ['overs', 'maidens', 'runs', 'wides', 'wickets', 'no_balls']:
            summary_bowling_df[column] = pd.to_numeric(summary_bowling_df[column], errors='coerce')

        # Calculate number of balls bowled
        summary_bowling_df['balls'] = summary_bowling_df['overs'].apply(lambda x: int(x) * 6 + round((x - int(x)) * 10))

        # Aggregate metrics based on bowler name, year and venue (home or away)
        summary_bowling_df = summary_bowling_df \
            .groupby(
                ['bowler_name', 'year', 'home_away'])[
                    ['balls', 'maidens', 'runs', 'wides', 'wickets', 'no_balls']] \
            .sum().reset_index()

        # Convert balls back to overs
        summary_bowling_df['overs'] = summary_bowling_df['balls'].apply(lambda x: f"{x // 6}.{x % 6}")

        # Define input and output columns of dataframe
        input_columns = ['bowler_name', 'year', 'home_away', 'balls',
                         'maidens', 'runs', 'wides', 'no_balls', 'wickets', 'overs',]
        output_columns = ['PLAYER', 'SEASON', 'HOME/AWAY', 'BALLS', 'MAIDENS',
                          'RUNS', 'WIDES', 'NO BALLS', 'WICKETS', 'OVERS']

        # Rename columns
        summary_bowling_df.columns = input_columns
        summary_bowling_df.rename(columns=dict(zip(input_columns, output_columns)), inplace=True)

        # Store summary dataframe as class object
        self.summary_bowling_df = summary_bowling_df

    @log_function_use(logger)
    def generate_bowling_dismissals_summary_df(self) -> None:
        """
        Generates a season-wise summary of bowling dismissals by type.

        This method processes the dismissal data in `self.all_bowling_dismissals_df`,
        counting how each bowler dismissed batters across different seasons. It filters
        out invalid records, groups the data by bowler and year, and pivots dismissal
        types into separate columns. The resulting summary includes only expected
        dismissal types and is stored in `self.bowling_dismissal_summary_df` with
        standardized column names in uppercase.

        Returns:
            None

        Notes:
            - Assumes `self.all_bowling_dismissals_df` is populated with valid match data.
            - Handles missing values and removes rows with empty bowler names.
            - Only includes the following dismissal types if present:
            'Bowled', 'Caught', 'LBW', 'Stumped'.
            - Converts column names to uppercase for output standardization.
        """
        # Drop NaN from dataframe
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

        # Identify which columns to drop
        expected_input_columns = ['bowler_name', 'year', 'Bowled', 'Caught', 'LBW', 'Stumped']
        input_columns = [item for item in expected_input_columns if item in bowling_dismissal_summary_df.columns]

        # Drop unexpected columns
        bowling_dismissal_summary_df = \
            bowling_dismissal_summary_df[input_columns]

        # Rename columns
        bowling_dismissal_summary_df.rename(columns={'bowler_name': 'PLAYER', 'year': 'SEASON'}, inplace=True)

        # Capitalize column headers
        bowling_dismissal_summary_df.columns = bowling_dismissal_summary_df.columns.str.upper()

        # Make dataframe object accessible by class
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
