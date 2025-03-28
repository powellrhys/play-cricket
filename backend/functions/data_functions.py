# Import python dependencies
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io

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
