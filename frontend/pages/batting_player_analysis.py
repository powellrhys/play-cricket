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
        cols = st.columns([2, 1, 2, 2])

        # Render components within first column
        with cols[0]:

            # Render selectbox for bowlers metric
            bowler = st.selectbox(label='Batter',
                                  options=batters,
                                  key='selectbox-batter')

        # Render components in the 3rd columns
        with cols[2]:
            plot_type = st.pills(label='Plot Type',
                                 options=['Bar', 'Area', 'Line'],
                                 default='Bar',
                                 key='batting-plot-type')

        # Render components within 4th column
        with cols[3]:

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

        # Melt the dataframe to long format
        how_out_df = how_out_df \
            .melt(id_vars=['SEASON', 'PLAYER'],
                  value_vars=[col for col in how_out_df.columns if col not in ['SEASON', 'PLAYER']],
                  var_name='Dismissal Type',
                  value_name='Dismissal Count')

        # Filter out NaN and data with zero records
        how_out_df['Dismissal Count'] = how_out_df['Dismissal Count'].fillna(0)
        how_out_df = how_out_df[how_out_df['Dismissal Count'] != 0.0]

        # Define plot colour scheme
        plot_colour_mapping = {
            'BOWLED': '#316151',
            'CAUGHT': '#FFE31A',
            'LBW': '#A63D40',
            'STUMPED': '#6495ED',
            'RUN OUT': '#D2B48C',
            'NOT OUT': '#E76F51',
            'DID NOT BAT': '#2A9D8F',
            'OTHER': '#E9C46A'
        }

        # Configure bar plot
        if plot_type == 'Bar':
            fig = px.bar(how_out_df,
                         x='SEASON',
                         y='Dismissal Count',
                         color='Dismissal Type',
                         barmode='group',
                         title='Dismissals by Type per Season',
                         color_discrete_map=plot_colour_mapping)

        # Configure areas plot
        if plot_type == 'Area':
            fig = px.area(how_out_df,
                          x='SEASON',
                          y='Dismissal Count',
                          color='Dismissal Type',
                          markers=True,
                          title='Dismissals by Type per Season (Line + Markers)',
                          color_discrete_map=plot_colour_mapping)

        # Configure line plot
        if plot_type == 'Line':
            fig = px.line(how_out_df,
                          x='SEASON',
                          y='Dismissal Count',
                          color='Dismissal Type',
                          markers=True,
                          title='Dismissals by Type per Season (Line + Markers)',
                          color_discrete_map=plot_colour_mapping)

        # Render plot
        st.plotly_chart(fig)
