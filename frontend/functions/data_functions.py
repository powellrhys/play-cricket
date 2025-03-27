# Import python dependencies
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import os

class Variables:
    """
    """
    def __init__(self):

        # Collect environmental variables
        self.blob_connection_string = os.getenv('blob_connection_string')
        self.club = os.getenv('club')


def read_csv_from_blob(
    connection_string: str,
    container_name: str,
    blob_name: str
) -> pd.DataFrame:
    """
    """
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
    connectio_string: str,
    container_name
) -> list:
    """
    """
    # Create BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connectio_string)

    # Get ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # List blobs in container
    blob_files = [file['name'] for file in container_client.list_blobs()]

    return blob_files
