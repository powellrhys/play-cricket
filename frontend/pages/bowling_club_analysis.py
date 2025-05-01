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
    render_bowling_club_bowling_effectiveness,
    render_bowling_club_extras_analysis,
    render_bowling_club_wicket_taking
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

# If user logged in, render streamlit components
if st.experimental_user.is_logged_in:

    # Render page title
    st.title(f'{vars.club.capitalize()} CC Bowling Analysis')

    # Render streamlit tabs on page
    tabs = st.tabs(tabs=['Bowling Effectiveness', 'Extras Analysis', 'Wicket Taking'])

    # Render components within the first tab
    with tabs[0]:

        # Create CricketData object and read in bowling_data.csv data from blob
        bowling_data_df = CricketData(blob_connection_string=vars.blob_connection_string,
                                      container_name='play-cricket',
                                      blob_name='bowling_data.csv')

        # Render bowling effectiveness section
        render_bowling_club_bowling_effectiveness(data=bowling_data_df, vars=vars)

    # Render components within second tab
    with tabs[1]:

        # Create CricketData object and read in bowling_match_data.csv data from blob
        bowling_match_data = CricketData(blob_connection_string=vars.blob_connection_string,
                                         container_name='play-cricket',
                                         blob_name='bowling_match_data.csv')

        # Render bowling extras analysis section
        render_bowling_club_extras_analysis(data=bowling_match_data, vars=vars)

    # Render final tab
    with tabs[2]:

        # Create CricketData object and read in bowling_dismissals.csv data from blob
        dismissal_data_df = CricketData(blob_connection_string=vars.blob_connection_string,
                                        container_name='play-cricket',
                                        blob_name='bowling_dismissals.csv')

        # Render bowling wicket taking section
        render_bowling_club_wicket_taking(data=dismissal_data_df, vars=vars)
