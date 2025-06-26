# Import python dependencies
from dotenv import load_dotenv
import streamlit as st

# Import project dependencies
from streamlit_components.ui_components import (
    configure_page_config
)
from functions.data_functions import (
    CricketData,
    Variables
)
from functions.ui_sections import (
    render_batting_player_runs_scored,
    render_batting_player_how_out
)

# Load environment variables
load_dotenv()
vars = Variables()

# Set page config
configure_page_config(repository_name='play-cricket',
                      page_icon='🏏')

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# If logged in, render page components
if st.user.is_logged_in:

    # Render page title
    st.title(f'{vars.club.capitalize()} CC Player Batting  Analysis')

    # Configure tab components
    tabs = st.tabs(['Runs Scored', 'How Out'])

    # Render components in the first tab
    with tabs[0]:

        # Create CricketData object and read in batting_how_out.csv data from blob
        batting_df = CricketData(blob_connection_string=vars.blob_connection_string,
                                 container_name='play-cricket',
                                 blob_name='batting_data.csv')

        # Render Player batting runs scored section
        render_batting_player_runs_scored(data=batting_df,
                                          vars=vars)

    # Render components in second tab
    with tabs[1]:

        # Create CricketData object and read in batting_how_out.csv data from blob
        how_out_df = CricketData(blob_connection_string=vars.blob_connection_string,
                                 container_name='play-cricket',
                                 blob_name='batting_how_out.csv')

        # Render player batting how out section
        render_batting_player_how_out(data=how_out_df,
                                      vars=vars)
