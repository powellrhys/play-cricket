# Import python dependencies
from dotenv import load_dotenv
from datetime import datetime
import plotly.express as px
import streamlit as st

# Import data functions
from functions.data_functions import (
    CricketData,
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

# Import streamlit sections
from functions.ui_sections import (
    render_club_batting_runs_scored
)

# Import project mapping variables
from functions.mapping import (
    batting_dismissal_colour_map
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

    # Create CricketData object and read in batting_how_out.csv data from blob
    how_out_df = CricketData(blob_connection_string=vars.blob_connection_string,
                             container_name='play-cricket',
                             blob_name='batting_how_out.csv')

    # Create CricketData object and read in batting_how_out.csv data from blob
    batting_df = CricketData(blob_connection_string=vars.blob_connection_string,
                             container_name='play-cricket',
                             blob_name='batting_data.csv')

    # Collect unique drop down metrics
    batters_how_out = how_out_df.collect_unique_column_values('PLAYER')

    # Configure tab components
    tabs = st.tabs(['Runs Scored', 'How Out'])

    # Render components in the first tab
    with tabs[0]:

        # Render Club batting runs scored section
        render_club_batting_runs_scored(data=batting_df,
                                        vars=vars)

    # Render components in second tab
    with tabs[1]:

        # Render columns
        cols = st.columns([2, 1, 2, 2])

        # Render components within first column
        with cols[0]:

            # Render selectbox for bowlers metric
            batter = st.selectbox(label='Batter',
                                  options=batters_how_out,
                                  key='selectbox-batter')

        # Render components in the 3rd columns
        with cols[2]:

            # Create pills for different plot types
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
                               value=[datetime.now().year - 5, datetime.now().year],
                               key='season-slider-how-out')

        # Render data source metadata badge
        data_source_badge(blob_connection_string=vars.blob_connection_string,
                          file_name='batting_how_out.csv')

        # Filter dataframe by season range and player name
        how_out_df.remove_all_season_data()
        how_out_df.filter_data_by_player(player_name=batter)
        how_out_df.filter_data_by_season_range(season=season)

        # Melt the dataframe to long format
        how_out_df.melt_dataframe(
            id_vars=['SEASON', 'PLAYER'],
            value_vars=[col for col in how_out_df.return_dataframe_columns()
                        if col not in ['SEASON', 'PLAYER']],
            var_name='Dismissal Type',
            value_name='Dismissal Count'
        )

        # Filter out NaN and data with zero records
        how_out_df.fill_nan(columns=['Dismissal Count'])
        how_out_df.filter_out_data(column='Dismissal Count',
                                   filter_value=0.0)

        # Configure bar plot
        if plot_type == 'Bar':
            fig = px.bar(how_out_df.return_dataframe(),
                         x='SEASON',
                         y='Dismissal Count',
                         color='Dismissal Type',
                         barmode='group',
                         title='Dismissals by Type per Season',
                         color_discrete_map=batting_dismissal_colour_map)

        # Configure areas plot
        if plot_type == 'Area':
            fig = px.area(how_out_df.return_dataframe(),
                          x='SEASON',
                          y='Dismissal Count',
                          color='Dismissal Type',
                          markers=True,
                          title='Dismissals by Type per Season',
                          color_discrete_map=batting_dismissal_colour_map)

        # Configure line plot
        if plot_type == 'Line':
            fig = px.line(how_out_df.return_dataframe(),
                          x='SEASON',
                          y='Dismissal Count',
                          color='Dismissal Type',
                          markers=True,
                          title='Dismissals by Type per Season',
                          color_discrete_map=batting_dismissal_colour_map)

        fig.update_layout(xaxis=dict(type='category',
                                     categoryorder='array',
                                     categoryarray=sorted(how_out_df.return_dataframe()['SEASON'])),
                          uniformtext_minsize=8, uniformtext_mode='hide')

        # Render plot
        st.plotly_chart(fig)
