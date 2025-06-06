# Import python dependencies
from streamlit_components.data_functions import (
    BlobData
)
import streamlit as st
import pandas as pd

class Variables:
    """
    Class to collect environmental variables from secrets.toml file. Secrets should
    be located in .streamlit/secrets.toml file

    Args: None

    Raise: None

    Return: None
    """
    def __init__(self):

        # Collect environmental variables
        self.blob_connection_string = st.secrets['general']['blob_connection_string']
        self.club = st.secrets['general']['club']


class CricketData(BlobData):
    """
    A specialized subclass of BlobData for processing cricket statistics data.

    This class provides methods specifically tailored for cleaning and filtering cricket-related datasets,
    such as removing 'ALL' season entries, handling not-out score markers, and filtering by player or season range.

    Methods:
        remove_all_season_data(season_column='SEASON'):
            Removes entries labeled 'ALL' in the season column and converts remaining season values to numeric.

        remove_not_out_marker(column_name='HIGH SCORE'):
            Removes the '*' character (used to denote 'not out') from high score entries and converts to float.

        filter_data_by_player(player_name, column_name='PLAYER'):
            Filters the dataset to include only rows matching the specified player name.

        filter_data_by_season_range(season, column_name='SEASON'):
            Filters the dataset to include only rows where the season falls within the specified range.
    """
    def remove_all_season_data(
        self,
        season_column: str = 'SEASON'
    ) -> None:
        """
        Removes rows with 'ALL' in the season column and converts the remaining values to numeric.

        Args:
            season_column (str, optional): Name of the column containing season data. Defaults to 'SEASON'.

        Notes:
            Non-numeric season entries will be coerced to NaN during conversion.
        """
        # Remove 'ALL' season from seasons column
        self.df = self.df[self.df[season_column] != 'ALL']

        # Convert all season yearly values to numeric values
        self.df[season_column] = pd.to_numeric(self.df['SEASON'], errors='coerce')

    def remove_not_out_marker(
        self,
        column_name: str = 'HIGH SCORE'
    ) -> None:
        """
        Removes the '*' character from high score entries, which typically indicates 'not out',
        and converts the values to float.

        Args:
            column_name (str, optional): Name of the column containing high score data. Defaults to 'HIGH SCORE'.
        """
        # Remove '*' from column
        self.df[column_name] = self.df[column_name].str.replace('*', '', regex=False).astype('float')

    def filter_data_by_player(
        self,
        player_name: str,
        column_name: str = 'PLAYER'
    ) -> None:
        """
        Filters the dataset to include only records matching the specified player name.

        Args:
            player_name (str): Name of the player to filter by.
            column_name (str, optional): Column that contains player names. Defaults to 'PLAYER'.
        """
        # Filter data by player name
        self.df = self.df[(self.df[column_name] == player_name)]

    def filter_data_by_season_range(
        self,
        season: tuple[int, int],
        column_name: str = 'SEASON'
    ) -> None:
        """
        Filters the dataset to include only rows where the season falls within the specified range.

        Args:
            season (tuple[int, int]): A tuple containing the start and end seasons (inclusive).
            column_name (str, optional): Name of the column containing season data. Defaults to 'SEASON'.
        """
        # Filter data by season range
        self.df = self.df[(self.df[column_name] >= season[0]) &
                          (self.df[column_name] <= season[1])]

    def group_home_and_away_metrics(
        self,
        groupby_columns: list
    ) -> None:
        """
        Groups the DataFrame by specified columns (e.g., ['PLAYER', 'SEASON']) and
        aggregates all numeric columns (e.g., RUNS, BALLS, WICKETS). If an 'OVERS'
        column exists, it is recalculated from the total BALLS column using standard
        cricket notation (e.g., 37.5 means 37 overs and 5 balls).

        Parameters:
        ----------
        groupby_columns : list
            A list of column names to group the DataFrame by.
        """
        # Group by the given columns and sum all numeric fields
        self.df = self.df.groupby(groupby_columns, as_index=False).sum(numeric_only=True)

        # If an 'OVERS' column exists, recalculate it based on total balls
        if 'overs' in [col.lower() for col in self.df.columns]:
            self.df['OVERS'] = self.df['BALLS'].apply(lambda balls: f"{balls // 6}.{balls % 6}")
