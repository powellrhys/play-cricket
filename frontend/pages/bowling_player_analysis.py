# Import python dependencies
from dotenv import load_dotenv
import plotly.express as px
import streamlit as st
from datetime import datetime

# Import data functions
from functions.data_functions import (
    read_csv_from_blob,
    Variables
)

# Import ui components
from functions.ui_components import (
    configure_page_config,
    data_source_badge
)

# Load environment variables
load_dotenv()
vars = Variables()

# Set page config
configure_page_config()

# Ensure user is authenticated to use application
if not st.experimental_user.is_logged_in:
    st.login('auth0')

# If logged in, render page components
if st.experimental_user.is_logged_in:

    # Render page title
    st.title(f'{vars.club.capitalize()} CC Player Bowling Analysis')

    # Read dismissal dataframe from blob
    dismissal_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                           container_name='play-cricket',
                                           blob_name='bowling_dismissals.csv')

    # Remove 'ALl' season and convert season column to integer type
    dismissal_data_df = dismissal_data_df[dismissal_data_df['SEASON'] != 'ALL']
    dismissal_data_df['SEASON'] = dismissal_data_df['SEASON'].astype(int)

    # Collect a list of unique bowlers and season
    seasons_dismissals = dismissal_data_df['SEASON'].unique()
    bowlers = dismissal_data_df['PLAYER'].unique()

    # Render streamlit tabs
    tabs = st.tabs(['Wicket Taking'])

    # Render streamlit tabs
    with tabs[0]:

        # Render columns
        cols = st.columns([1, 1, 1])

        # Render components within first column
        with cols[0]:

            # Render selectbox for bowlers metric
            bowler = st.selectbox(label='Bowler',
                                  options=bowlers,
                                  key='selectbox-bowler')

        # Render components within 3rd column
        with cols[2]:

            # Render season slider
            season = st.slider(label='Season Range',
                               min_value=datetime.now().year - 20,
                               max_value=datetime.now().year,
                               value=[datetime.now().year - 5, datetime.now().year])

        # Render data source metadata badge
        data_source_badge(blob_connection_string=vars.blob_connection_string,
                          file_name='bowling_dismissals.csv')

        # Filter data based on streamlit inputs
        dismissal_data_df = \
            dismissal_data_df[
                (dismissal_data_df['SEASON'] >= season[0]) &
                (dismissal_data_df['SEASON'] <= season[1]) &
                (dismissal_data_df['PLAYER'] == bowler)]

        # Melt the dataframe to reshape it so dismissal types are in a single column
        dismissal_data_df = dismissal_data_df.melt(id_vars=['SEASON'],
                                                   value_vars=['BOWLED', 'CAUGHT', 'LBW', 'STUMPED', 'HIT ROOF'],
                                                   var_name='TYPE',
                                                   value_name='COUNT')

        # Filter out rows where count is 0
        dismissal_data_df = dismissal_data_df[dismissal_data_df['COUNT'] > 0]

        # Create a bar plot with Plotly Express
        fig = px.bar(dismissal_data_df,
                     x='SEASON',
                     y='COUNT',
                     color='TYPE',
                     barmode='group',
                     title="Bowled and Caught Count by Season",
                     labels={'SEASON': 'Season', 'COUNT': 'Wickets'},
                     color_discrete_map={
                         'BOWLED': '#316151',
                         'CAUGHT': '#FFE31A',
                         'LBW': '#A63D40',
                         'STUMPED': '#6495ED',
                         'Hit ROOF': '#D2B48C'})

        # Render bar chart
        st.plotly_chart(fig)
