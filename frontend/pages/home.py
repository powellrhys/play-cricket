# Import dependencies
from streamlit_components.ui_components import configure_page_config
from functions.data_functions import Variables
from dotenv import load_dotenv
import streamlit as st

# Set page config
configure_page_config(repository_name='play-cricket',
                      page_icon='🏏')

# Load environment variables
load_dotenv()
vars = Variables()

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# If user logged in, render streamlit content
if st.user.is_logged_in:

    # Render page title
    st.title(f'{vars.club.capitalize()} CC Analysis')

    # Render container
    with st.container(border=True):

        # Render application overview paragraph
        st.write(
            """
            This Streamlit project is a data-driven web app that displays club cricket statistics for analysis.
            The data is sourced from the Play-Cricket website and stored in a Blob Storage account, which is
            automatically updated via a GitHub scheduled action using a cron job. This ensures the app always
            presents the latest cricket data, enabling users to explore trends, performance metrics, and insights
            in an interactive and user-friendly way.
            """
        )
