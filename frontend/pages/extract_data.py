# Import python dependencies
from dotenv import load_dotenv
import streamlit as st

# Import data functions
from functions.data_functions import (
    read_csv_from_blob,
    list_blob_files,
    Variables
)

# Import ui components
from functions.ui_components import (
    configure_page_config
)

# Load environment variables
load_dotenv()
vars = Variables()

# Set page config
configure_page_config()

# Ensure user is authenticated to use application
if not st.experimental_user.is_logged_in:
    st.login('auth0')

if st.experimental_user.is_logged_in:

    # Render page title
    st.title('Extract Club Data')

    # List all files in blob container
    files = list_blob_files(connectio_string=vars.blob_connection_string,
                            container_name='play-cricket')

    col1, col2 = st.columns([2, 3])

    with col1:

        # Render file selectbox
        file = st.selectbox(label='File',
                            options=files)

        # Download file from csv
        df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                container_name='play-cricket',
                                blob_name=file)

        # Render dataframe download button
        st.download_button(
            label="Download Data",
            data=df.to_csv().encode("utf-8"),
            file_name=file,
            mime="text/csv",
            icon=":material/download:"
        )

    with st.expander(label='Preview Data',
                     expanded=False):

        # Render data in dataframe format
        st.dataframe(df)
