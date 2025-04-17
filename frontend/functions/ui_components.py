# Import python dependencies
import streamlit as st

# Import data functions
from functions.data_functions import (
    list_blob_files
)

def data_source_badge(
    blob_connection_string: str,
    file_name: str,
    additional_comments: str = ''
) -> None:
    """
    Function to render data source metadata badge.

    Args:
        blob_connection_string (str): azure blob storage connection string
        file_name (str): blob storage file name
        additional_comments (str = ''): Additional notes to render on badge

    Raise:
        TypeError: If blob_connection_string or file_name not a string

    Return: None
    """
    # Ensure input variables are strings
    for arg_name, arg_value in locals().items():
        if not isinstance(arg_value, str):
            raise TypeError(f"{arg_name} must be a string, but got {type(arg_value).__name__}")

    # Collect list of blob files
    _, blob_files = list_blob_files(connection_string=blob_connection_string,
                                    container_name='play-cricket')

    # Filter blob files list to retrieve file of interest and when file was last modified
    last_modified = [file for file in blob_files if file['name'] == file_name][0]['last_modified']

    # Configure additional notes string
    if additional_comments:
        additional_note = f' **| Note:** {additional_comments}'
    else:
        additional_note = ''

    # Define Badge message
    badge_message = f'**Data Source:** {file_name} **| Data Updated:** ' + \
        f'{last_modified.strftime("%d/%m/%Y %H:%M:%S")} {additional_note}'

    # Render badge on streamlit page
    st.badge(label=badge_message,
             color='primary')
