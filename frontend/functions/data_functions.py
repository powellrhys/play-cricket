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
