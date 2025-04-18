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
    st.title(f'{vars.club.capitalize()} CC Player Bowling Analysis')

    # Read dismissal dataframe from blob
    dismissal_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                           container_name='play-cricket',
                                           blob_name='bowling_dismissals.csv')

    # Remove 'ALL' season and convert season column to integer type
    dismissal_data_df = dismissal_data_df[dismissal_data_df['SEASON'] != 'ALL']
    dismissal_data_df['SEASON'] = dismissal_data_df['SEASON'].astype(int)

    # Collect a list of unique bowlers and season
    seasons_dismissals = dismissal_data_df['SEASON'].unique()
    bowlers = dismissal_data_df['PLAYER'].unique()

    # Render streamlit tabs
    tabs = st.tabs(['Wicket Taking', 'Home/Away Performance'])

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

    # Render components in second tab
    with tabs[1]:

        # Collect match report data
        bowling_match_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                                   container_name='play-cricket',
                                                   blob_name='bowling_match_data.csv')

        # Collect year from bowling match report data
        bowling_match_data_df['DATE'] = pd.to_datetime(bowling_match_data_df['DATE'])
        bowling_match_data_df['SEASON'] = bowling_match_data_df['DATE'].dt.year

        # Collect unique season values from dataframes
        seasons_extras = bowling_match_data_df['SEASON'].unique()
        bowlers_extras = bowling_match_data_df['BOWLER'].unique()

        # Render columns
        cols = st.columns([2, 1, 2, 2])

        # Render components within first column
        with cols[0]:

            # Render selectbox for bowlers metric
            bowler = st.selectbox(label='Bowler',
                                  options=bowlers_extras,
                                  key='selectbox-bowler-extras')

        with cols[2]:

            # Render metric pills
            metric_extras = st.pills(label='Metric',
                                     options=['WIDES', 'NO BALLS', 'WICKETS'],
                                     selection_mode='single',
                                     default='WIDES',
                                     key='player-pills-extras')

        # Render components within 3rd column
        with cols[3]:

            # Render season slider
            season = st.slider(label='Season Range',
                               min_value=bowling_match_data_df['SEASON'].min(),
                               max_value=datetime.now().year,
                               value=[datetime.now().year - 5, datetime.now().year],
                               key='season-bowler-extras-analysis')

        # Render data source metadata badge
        data_source_badge(blob_connection_string=vars.blob_connection_string,
                          file_name='bowling_match_data.csv')

        # Filter data based on streamlit inputs
        bowling_match_data_df = \
            bowling_match_data_df[
                (bowling_match_data_df['BOWLER'] == bowler) &
                (bowling_match_data_df['SEASON'] >= season[0]) &
                (bowling_match_data_df['SEASON'] <= season[1])]

        # Filter data based on bowler selected
        bowling_match_data_df = bowling_match_data_df[bowling_match_data_df['BOWLER'] == bowler]

        # Apply lambda function to calculate the number of ball delivered
        bowling_match_data_df['BALLS'] = \
            bowling_match_data_df['OVERS'] \
            .apply(lambda x: (int(str(x).split('.')[0]) * 6) + int(str(x).split('.')[1][0])
                   if '.' in str(x) else int(x) * 6)

        # Group data by bowler, season and venue
        bowling_match_data_df = bowling_match_data_df.groupby(['BOWLER', 'SEASON', 'VENUE'], as_index=False)[
            ['BALLS', 'MAIDENS', 'WICKETS', 'RUNS', 'WIDES', 'NO BALLS']
        ].sum()

        # Create dynamic metric column
        bowling_match_data_df['METRIC'] = bowling_match_data_df[metric_extras]

        # Configure bar chart
        fig = px.bar(
            bowling_match_data_df,
            x='SEASON',
            y=metric_extras,
            color='VENUE',
            barmode='group',
            title="Conceded by Bowlers at Different Venues",
            labels={'METRIC': metric_extras},
            color_discrete_map={'Home': '#316151', 'Away': '#FFE31A'},
            hover_name='BOWLER',
            hover_data={
                'BALLS': True,
                metric_extras: True
            }
        )

        # Render plot
        st.plotly_chart(fig)
