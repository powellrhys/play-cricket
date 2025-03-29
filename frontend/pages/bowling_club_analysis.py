# Import python dependencies
from dotenv import load_dotenv
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

# If user logged in, render streamlit components
if st.experimental_user.is_logged_in:

    # Render page title
    st.title(f'{vars.club.capitalize()} CC Bowling Analysis')

    # Collect bowling data
    bowling_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                         container_name='play-cricket',
                                         blob_name='bowling_data.csv')

    # Collect match report data
    bowling_match_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                               container_name='play-cricket',
                                               blob_name='bowling_match_data.csv')

    # Collect bowling dismissal data
    dismissal_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                           container_name='play-cricket',
                                           blob_name='bowling_dismissals.csv')

    # Collect year from bowling match report data
    bowling_match_data_df['DATE'] = pd.to_datetime(bowling_match_data_df['DATE'])
    bowling_match_data_df['SEASON'] = bowling_match_data_df['DATE'].dt.year

    # Collect unique season values from dataframes
    seasons_overs = bowling_data_df['SEASON'].unique()
    seasons_extras = bowling_match_data_df['SEASON'].unique()
    seasons_dismissals = dismissal_data_df['SEASON'].unique()

    # Render streamlit tabs on page
    tabs = st.tabs(tabs=['Bowling Effectiveness', 'Extras Analysis', 'Wicket Taking'])

    # Render components within the first tab
    with tabs[0]:

        # Render streamlit columns
        cols = st.columns([2, 1, 1, 1])

        # Render components within first column
        with cols[0]:

            # Render season selectbox
            season_overs = st.selectbox(label='Season',
                                        options=seasons_overs,
                                        key='selectbox-overs')

        # Render components within 3rd column
        with cols[2]:

            # Render metric pills
            metric_overs = st.pills(label='Metric',
                                    options=['WICKETS', 'RUNS'],
                                    selection_mode='single',
                                    default='WICKETS',
                                    key='pills-overs')

        # Filter bowling data by season
        bowling_data_df = bowling_data_df[bowling_data_df['SEASON'] == season_overs]

        # Render data source metadata badge
        data_source_badge(blob_connection_string=vars.blob_connection_string,
                          file_name='bowling_data.csv')

        # Configure scatter plot
        fig = px.scatter(data_frame=bowling_data_df,
                         x='OVERS',
                         y=metric_overs,
                         hover_name='PLAYER',
                         trendline='ols',
                         title=f'{metric_overs.capitalize()} for every over bowled')

        # Set all points to color #316151
        fig.update_traces(marker=dict(color='#316151'))

        # Render scatter plot
        st.plotly_chart(fig)

    # Render components within second tab
    with tabs[1]:

        # Render columns
        cols = st.columns([2, 1, 1, 1])

        # Render components within first column
        with cols[0]:

            # Render selectbox for season metric
            season_extras = st.selectbox(label='Season',
                                         options=seasons_extras,
                                         key='selectbox-extras')

        # Render components within the second column
        with cols[2]:

            # Render metric pills
            metric_extras = st.pills(label='Metric',
                                     options=['WIDES', 'NO BALLS'],
                                     selection_mode='single',
                                     default='WIDES',
                                     key='pills-extras')

        # Render components within the 4th column
        with cols[3]:

            # Render normalise pill
            normalise_extras = st.pills(label='Normalise Data',
                                        options=[True, False],
                                        selection_mode='single',
                                        default=False,
                                        key='pills-extras-normalise')

        # Render data source metadata badge
        data_source_badge(blob_connection_string=vars.blob_connection_string,
                          file_name='bowling_match_data.csv')

        # Filter bowling report data by season
        bowling_match_data_df = bowling_match_data_df[bowling_match_data_df['SEASON'] == season_extras]

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

        # Normalise data by number of balls delivered if required
        y_axis_label = metric_extras.capitalize()
        if normalise_extras:
            bowling_match_data_df['METRIC'] = bowling_match_data_df['METRIC'] / (bowling_match_data_df['BALLS'] / 6)
            y_axis_label = f'{metric_extras.capitalize()} per Over'

        # Sort data by metric count
        bowling_match_data_df = bowling_match_data_df.sort_values(by='METRIC', ascending=False)

        # Calculate total metric per bowler (summing across all venues)
        df_sorted = bowling_match_data_df.groupby('BOWLER', as_index=False)['METRIC'].sum()

        # Sort by total metric (descending)
        df_sorted = df_sorted.sort_values(by='METRIC', ascending=False)

        # Merge sorted order back to original df_grouped
        bowling_match_data_df = bowling_match_data_df.set_index('BOWLER').loc[df_sorted['BOWLER']].reset_index()

        # Remove rows where metric is equal to zero
        bowling_match_data_df = bowling_match_data_df[bowling_match_data_df['METRIC'] != 0]

        # Configure bar chart
        fig = px.bar(
            bowling_match_data_df,
            x='BOWLER',
            y='METRIC',
            color='VENUE',
            barmode='group',
            title=f"{y_axis_label} Conceded by Bowlers at Different Venues",
            labels={'METRIC': y_axis_label},
            color_discrete_map={'Home': '#316151', 'Away': '#FFE31A'},
            hover_name='BOWLER',
            hover_data={
                'BALLS': True,
                metric_extras: True
            }
        )

        # Render bar chart
        st.plotly_chart(fig)

    # Render final tab
    with tabs[2]:

        # Render columns
        cols = st.columns([2, 1, 1, 1])

        # Render components within first column
        with cols[0]:

            # Render season select box
            season_wickets = st.selectbox(label='Season',
                                          options=seasons_dismissals,
                                          key='selectbox-wicket')

        # Render data source metadata badge
        data_source_badge(blob_connection_string=vars.blob_connection_string,
                          file_name='bowling_dismissals.csv')

        # Filter data by season
        dismissal_data_df = dismissal_data_df[dismissal_data_df['SEASON'] == season_wickets]

        # Group data by season and aggregate wicket taking types
        dismissal_data_df = dismissal_data_df \
            .groupby('SEASON', as_index=False)[['BOWLED', 'CAUGHT', 'LBW', 'STUMPED', 'HIT ROOF']].sum()

        # Summing across seasons to get total dismissals per category
        dismissal_data_df = dismissal_data_df.drop(columns=['SEASON']).sum().reset_index()
        dismissal_data_df.columns = ['Dismissal Type', 'Count']

        # Create pie chart
        fig = px.pie(
            dismissal_data_df,
            names='Dismissal Type',
            values='Count',
            color='Dismissal Type',
            title="Total Dismissals by Type",
            color_discrete_map={
                'BOWLED': '#316151',
                'CAUGHT': '#FFE31A',
                'LBW': '#A63D40',
                'STUMPED': '#6495ED',
                'Hit ROOF': '#D2B48C'
            }
        )

        # Render pie chart
        st.plotly_chart(fig)
