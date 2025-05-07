# Import python dependencies
from azure.storage.blob import BlobServiceClient
import streamlit as st
import pandas as pd
import io

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


def list_blob_files(
    connection_string: str,
    container_name
) -> tuple[list, list]:
    """
    Function to list all files in a blob storage container

    Args:
        connection_string (str): Azure blob storage connection string
        container_name (str): Azure blob storage container name

    Raise:
        TypeError: If input variables are not strings

    Return:
        blob_file_names (list): List of blob files names with a container
        blob_files (list): List of blob files in container (list of dictionaries)
    """
    # Ensure input variables are strings
    for arg_name, arg_value in locals().items():
        if not isinstance(arg_value, str):
            raise TypeError(f"{arg_name} must be a string, but got {type(arg_value).__name__}")

    # Create BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # List blobs in container
    blob_files = [file for file in container_client.list_blobs()]
    blob_filenames = [file['name'] for file in container_client.list_blobs()]

    return blob_filenames, blob_files


class BlobData:
    """
    A utility class to interact with and manipulate a DataFrame loaded from an Azure Blob Storage CSV.

    The class reads a CSV file from a specified blob and provides various methods to clean,
    transform, and query the resulting pandas DataFrame.

    Methods:
        collect_unique_column_values(column_name): Returns unique values from a specified column.
        fill_nan(columns, fill_value=0): Replaces NaN values in specified columns with a fill value.
        filter_by_column(column, filter_value): Filters rows where the column equals the filter value.
        filter_out_data(column, filter_value=0): Filters out rows where the column equals the filter value.
        melt_dataframe(id_vars, value_vars, var_name, value_name): Converts the DataFrame from wide to long format.
        return_dataframe_columns(): Returns a list of column names in the DataFrame.
        return_dataframe(): Returns the current DataFrame.
        aggregate_dataframe(groupby_columns, agg_columns, agg_func='sum'): Aggregates the DataFrame by grouping and
            applying a function.
        convert_column_to_datetime(column_name): Converts a column to datetime format.
        create_year_column(date_column_name, year_column_name): Creates a new column with the year extracted from a
            datetime column.
        cast_column(column_name, column_type): Casts a column to a specified Python type.
    """
    def __init__(
        self,
        blob_connection_string: str,
        container_name: str,
        blob_name: str
    ) -> None:
        """
        Initializes the BlobData object by loading a CSV from Azure Blob Storage.

        Args:
            blob_connection_string (str): Connection string to the Azure Blob Storage account.
            container_name (str): Name of the container where the blob is stored.
            blob_name (str): Name of the CSV blob to be read.
        """
        # Read dataframe from blob storage
        self.df = read_csv_from_blob(connection_string=blob_connection_string,
                                     container_name=container_name,
                                     blob_name=blob_name)

    def collect_unique_column_values(
        self,
        column_name: str
    ) -> list:
        """
        Returns a list of unique values from the specified column.

        Args:
            column_name (str): The column from which to collect unique values.

        Returns:
            list: Unique values in the column.

        Raises:
            ValueError: If the column is not present in the DataFrame.
        """
        # Check if column_name is present within dataframe
        if column_name not in self.df.columns:
            raise ValueError(f'Column: {column_name} is not present in dataframe')

        # Collect unique values from dataframe column
        unique_values = list(self.df[column_name].unique())

        return unique_values

    def fill_nan(
        self,
        columns: list,
        fill_value: str | int = 0
    ) -> None:
        """
        Replaces NaN values in the specified columns with a given fill value.

        Args:
            columns (list): List of column names to fill.
            fill_value (str | int, optional): The value to use for filling. Defaults to 0.

        Raises:
            ValueError: If any specified column is not present in the DataFrame.
        """
        # Iterate through all columns
        for column in columns:

            # If column in dataframe, replace all NaN values with replacement value
            if column in self.df.columns:
                self.df[column] = self.df[column].fillna(fill_value)

            # Raise error if column not present in dataframe
            else:
                raise ValueError(f"Column: {column} not present in dataframe")

    def filter_by_column(
        self,
        column: str,
        filter_value: str | int
    ) -> None:
        """
        Filters the DataFrame to only include rows where a column matches the given value.

        Args:
            column (str): Column to filter on.
            filter_value (str | int): Value to filter by.
        """
        # Filter out filter value from specified column
        self.df = self.df[self.df[column] == filter_value]

    def filter_out_data(
        self,
        column: str,
        filter_value: str | int = 0
    ) -> None:
        """
        Filters the DataFrame to exclude rows where a column matches the given value.

        Args:
            column (str): Column to filter on.
            filter_value (str | int, optional): Value to exclude. Defaults to 0.
        """
        # Filter out filter value from specified column
        self.df = self.df[self.df[column] != filter_value]

    def melt_dataframe(
        self,
        id_vars: list,
        value_vars: list,
        var_name: str,
        value_name: str
    ) -> None:
        """
        Converts the DataFrame from wide to long format using pandas melt.

        Args:
            id_vars (list): Columns to keep fixed.
            value_vars (list): Columns to unpivot.
            var_name (str): Name of the new variable column.
            value_name (str): Name of the new value column.
        """
        # Melt the dataframe to long format
        self.df = self.df \
            .melt(id_vars=id_vars,
                  value_vars=value_vars,
                  var_name=var_name,
                  value_name=value_name)

    def return_dataframe_columns(
        self
    ) -> list:
        """
        Returns the list of column names in the DataFrame.

        Returns:
            list: List of column names.
        """
        return self.df.columns

    def return_dataframe(
        self
    ) -> pd.DataFrame:
        """
        Returns the current DataFrame.

        Returns:
            pd.DataFrame: The DataFrame object.
        """
        return self.df

    def aggregate_dataframe(
        self,
        groupby_columns: list,
        agg_columns: list,
        agg_func: str = 'sum'
    ) -> None:
        """
        Aggregates the DataFrame using the specified groupby and aggregation function.

        Args:
            groupby_columns (list): Columns to group by.
            agg_columns (list): Columns to apply aggregation on.
            agg_func (str, optional): Aggregation function to use (e.g., 'sum', 'mean'). Defaults to 'sum'.
        """
        # Groupby and aggregate dataframe
        self.df = self.df.groupby(groupby_columns, as_index=False)[agg_columns].agg(agg_func)

    def convert_column_to_datetime(
        self,
        column_name: str
    ) -> None:
        """
        Converts a specified column to datetime format.

        Args:
            column_name (str): Name of the column to convert.
        """
        # Convert column_name column to datetime datatype
        self.df[column_name] = pd.to_datetime(self.df[column_name])

    def create_year_column(
        self,
        date_column_name: str,
        year_column_name: str
    ) -> None:
        """
        Extracts the year from a datetime column and stores it in a new column.

        Args:
            date_column_name (str): Column containing datetime values.
            year_column_name (str): Name of the new column to store the year.
        """
        # Collect year from datetime column
        self.df[year_column_name] = self.df[date_column_name].dt.year

    def cast_column(
        self,
        column_name: str,
        column_type: type
    ) -> None:
        """
        Casts a specified column to a given data type.

        Args:
            column_name (str): Name of the column to cast.
            column_type (type): Python type to cast the column to (e.g., int, str, float).
        """
        # Cast a column to a specific datatype
        self.df[column_name] = self.df[column_name].astype(column_type)

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
