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
    def __init__(
        self,
        blob_connection_string: str,
        container_name: str,
        blob_name: str
    ):
        self.df = read_csv_from_blob(connection_string=blob_connection_string,
                                     container_name=container_name,
                                     blob_name=blob_name)

    def collect_unique_column_values(
        self,
        column_name: str
    ) -> list:
        """
        """
        # Check if column_name is present within dataframe
        if column_name not in self.df.columns:
            raise ValueError(f'Column: {column_name} is not present in dataframe')

        # Collect unique values from dataframe column
        unique_values = self.df[column_name].unique()

        return unique_values

    def fill_nan(
        self,
        columns: list,
        fill_value: str | int = 0
    ) -> None:
        """
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
        """
        # Filter out filter value from specified column
        self.df = self.df[self.df[column] == filter_value]

    def filter_out_data(
        self,
        column: str,
        filter_value: str | int = 0
    ) -> None:
        """
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
        """
        return self.df.columns

    def return_dataframe(
        self
    ) -> pd.DataFrame:
        """
        """
        return self.df

    def aggregate_dataframe(
        self,
        groupby_columns: list,
        agg_columns: list,
        agg_func: str = 'sum'
    ) -> None:
        """
        """
        self.df = self.df.groupby(groupby_columns, as_index=False)[agg_columns].agg(agg_func)

class CricketData(BlobData):
    def remove_all_season_data(
        self,
        season_column: str = 'SEASON'
    ) -> None:
        """
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
        """
        # Remove '*' from column
        self.df[column_name] = self.df[column_name].str.replace('*', '', regex=False).astype('float')

    def filter_data_by_player(
        self,
        player_name: str,
        column_name: str = 'PLAYER'
    ) -> None:
        """
        """
        # Filter data by player name
        self.df = self.df[(self.df[column_name] == player_name)]

    def filter_data_by_season_range(
        self,
        season: tuple[int, int],
        column_name: str = 'SEASON'
    ) -> None:
        """
        """
        # Filter data by season range
        self.df = self.df[(self.df[column_name] >= season[0]) &
                          (self.df[column_name] <= season[1])]
