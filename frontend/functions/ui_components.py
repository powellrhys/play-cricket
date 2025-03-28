# Import python dependencies
import streamlit as st
import warnings

# Import data functions
from functions.data_functions import (
    list_blob_files
)

def configure_page_config(
    initial_sidebar_state: str = "expanded",
    layout: str = "wide"
) -> None:
    """
    """
    # Set page config
    st.set_page_config(
        initial_sidebar_state=initial_sidebar_state,
        layout=layout,
        page_icon='🏏',
        menu_items={
            "Report a Bug": "https://github.com/powellrhys/play-cricket/issues"
        }
    )

    warnings.filterwarnings("ignore")

    st.sidebar.markdown(f"👤 **Logged in as:** {st.experimental_user.name}")

    if st.sidebar.button('Log Out'):
        st.logout()


def data_source_badge(
    blob_connection_string: str,
    file_name: str
) -> None:
    """
    """
    # Collect list of blob files
    _, blob_files = list_blob_files(connection_string=blob_connection_string,
                                    container_name='play-cricket')

    last_modified = [file for file in blob_files if file['name'] == file_name][0]['last_modified']

    st.badge(label=f'Data Source: {file_name} | Data Last Updated: {last_modified.strftime("%m/%d/%Y %H:%M:%S")}',
             color='primary')
