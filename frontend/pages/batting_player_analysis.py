# Import python dependencies
from dotenv import load_dotenv
from datetime import datetime
import plotly.express as px
import streamlit as st
import pandas as pd


# Import data functions
from functions.data_functions import (
    read_csv_from_blob,
    Variables
)

# Import ui components
from functions.ui_components import (
    data_source_badge
)

# Import custom ui components
from streamlit_components.ui_components import (
    configure_page_config
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
    st.title(f'{vars.club.capitalize()} CC Player Batting  Analysis')

    # Read dismissal dataframe from blob
    how_out_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                    container_name='play-cricket',
                                    blob_name='batting_how_out.csv')

    batters = how_out_df['PLAYER'].unique()

    # Configure tab components
    tabs = st.tabs(['Runs Scored', 'How Out'])

    # Render data 
    with tabs[1]:

        # Render columns
        cols = st.columns([1, 1, 1])

        # Render components within first column
        with cols[0]:

            # Render selectbox for bowlers metric
            bowler = st.selectbox(label='Batter',
                                  options=batters,
                                  key='selectbox-batter')

        # Render components within 3rd column
        with cols[2]:

            # Render season slider
            season = st.slider(label='Season Range',
                               min_value=datetime.now().year - 20,
                               max_value=datetime.now().year,
                               value=[datetime.now().year - 5, datetime.now().year])

        # Render data source metadata badge
        data_source_badge(blob_connection_string=vars.blob_connection_string,
                          file_name='batting_how_out.csv')

        # Transform season column to only include numeric values
        how_out_df = how_out_df[how_out_df['SEASON'] != 'ALL']
        how_out_df['SEASON'] = pd.to_numeric(how_out_df['SEASON'], errors='coerce')

        # Filter data based on streamlit inputs
        how_out_df = \
            how_out_df[
                (how_out_df['SEASON'] >= season[0]) &
                (how_out_df['SEASON'] <= season[1]) &
                (how_out_df['PLAYER'] == bowler)]

        st.dataframe(how_out_df)
