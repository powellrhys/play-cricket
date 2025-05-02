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
    render_bowling_player_home_away_performance,
    render_bowling_player_wicket_taking
)

# Load environment variables
load_dotenv()
vars = Variables()

# Set page config
configure_page_config(repository_name='play-cricket',
                      page_icon='🏏')

# Ensure user is authenticated to use application
if not st.experimental_user.is_logged_in:
    st.login('auth0')

# If logged in, render page components
if st.experimental_user.is_logged_in:

    # Render page title
    st.title(f'{vars.club.capitalize()} CC Player Bowling Analysis')

    # Render streamlit tabs
    tabs = st.tabs(['Wicket Taking', 'Home/Away Performance'])

    # Render streamlit tabs
    with tabs[0]:

        # Create CricketData object and read in bowling_dismissals.csv data from blob
        dismissal_data_df = CricketData(blob_connection_string=vars.blob_connection_string,
                                        container_name='play-cricket',
                                        blob_name='bowling_dismissals.csv')

        # Render player bowling wicket taking section
        render_bowling_player_wicket_taking(data=dismissal_data_df,
                                            vars=vars)

    # Render components in second tab
    with tabs[1]:

        # Create CricketData object and read in bowling_match_data.csv data from blob
        bowling_match_data_df = CricketData(blob_connection_string=vars.blob_connection_string,
                                            container_name='play-cricket',
                                            blob_name='bowling_match_data.csv')

        # Render player bowling home and away performance
        render_bowling_player_home_away_performance(data=bowling_match_data_df,
                                                    vars=vars)
