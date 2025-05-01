# Import python dependencies
from dotenv import load_dotenv
import plotly.express as px
import streamlit as st
import pandas as pd

# Import project dependencies
from streamlit_components.ui_components import (
    configure_page_config
)
from functions.data_functions import (
    CricketData,
    Variables
)
from functions.ui_components import (
    data_source_badge
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
        render_bowling_club_extras_analysis(data=bowling_data_df, vars=vars)

    # Render final tab
    with tabs[2]:

        # Create CricketData object and read in bowling_dismissals.csv data from blob
        dismissal_data_df = CricketData(blob_connection_string=vars.blob_connection_string,
                                        container_name='play-cricket',
                                        blob_name='bowling_dismissals.csv')

        # Render bowling wicket taking section
        render_bowling_club_wicket_taking(data=dismissal_data_df, vars=vars)

    # # Collect bowling data
    # bowling_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
    #                                      container_name='play-cricket',
    #                                      blob_name='bowling_data.csv')

    # # Collect match report data
    # bowling_match_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
    #                                            container_name='play-cricket',
    #                                            blob_name='bowling_match_data.csv')

    # # Collect bowling dismissal data
    # dismissal_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
    #                                        container_name='play-cricket',
    #                                        blob_name='bowling_dismissals.csv')

    # # Collect year from bowling match report data
    # bowling_match_data_df['DATE'] = pd.to_datetime(bowling_match_data_df['DATE'])
    # bowling_match_data_df['SEASON'] = bowling_match_data_df['DATE'].dt.year

    # # Collect unique season values from dataframes
    # seasons_overs = bowling_data_df['SEASON'].unique()
    # seasons_extras = list(bowling_match_data_df['SEASON'].unique())
    # seasons_dismissals = dismissal_data_df['SEASON'].unique()

    # # Perform transformations and append data to seasons lists
    # oldest_season = min(seasons_extras)
    # seasons_extras.append('ALL')
    # seasons_extras.reverse()

    # # Render streamlit tabs on page
    # tabs = st.tabs(tabs=['Bowling Effectiveness', 'Extras Analysis', 'Wicket Taking'])

    # # Render components within second tab
    # with tabs[1]:

    #     # Render columns
    #     cols = st.columns([2, 1, 1, 1])

    #     # Render components within first column
    #     with cols[0]:

    #         # Render selectbox for season metric
    #         season_extras = st.selectbox(label='Season',
    #                                      options=seasons_extras,
    #                                      key='selectbox-extras')

    #     # Render components within the second column
    #     with cols[2]:

    #         # Render metric pills
    #         metric_extras = st.pills(label='Metric',
    #                                  options=['WIDES', 'NO BALLS'],
    #                                  selection_mode='single',
    #                                  default='WIDES',
    #                                  key='pills-extras')

    #     # Render components within the 4th column
    #     with cols[3]:

    #         # Render normalise pill
    #         normalise_extras = st.pills(label='Normalise Data',
    #                                     options=[True, False],
    #                                     selection_mode='single',
    #                                     default=False,
    #                                     key='pills-extras-normalise')

    #     # Render data source metadata badge
    #     data_source_badge(blob_connection_string=vars.blob_connection_string,
    #                       file_name='bowling_match_data.csv',
    #                       additional_comments=f'Data dated back to {oldest_season} season')

    #     # Apply lambda function to calculate the number of ball delivered
    #     bowling_match_data_df['BALLS'] = \
    #         bowling_match_data_df['OVERS'] \
    #         .apply(lambda x: (int(str(x).split('.')[0]) * 6) + int(str(x).split('.')[1][0])
    #                if '.' in str(x) else int(x) * 6)

    #     # Aggregate all data
    #     all_data = bowling_match_data_df.groupby(['BOWLER', 'VENUE'], as_index=False)[
    #         ['BALLS', 'MAIDENS', 'WICKETS', 'RUNS', 'WIDES', 'NO BALLS']
    #     ].sum()

    #     # Add season column to aggregated dataframe
    #     all_data['SEASON'] = 'ALL'

    #     # Group data by bowler, season and venue
    #     bowling_match_data_df = bowling_match_data_df.groupby(['BOWLER', 'SEASON', 'VENUE'], as_index=False)[
    #         ['BALLS', 'MAIDENS', 'WICKETS', 'RUNS', 'WIDES', 'NO BALLS']
    #     ].sum()

    #     # Append aggregated data to dataframe
    #     bowling_match_data_df = pd.concat([bowling_match_data_df, all_data], ignore_index=True)

    #     # Filter bowling report data by season
    #     bowling_match_data_df = bowling_match_data_df[bowling_match_data_df['SEASON'] == season_extras]

    #     # Create dynamic metric column
    #     bowling_match_data_df['METRIC'] = bowling_match_data_df[metric_extras]

    #     # Normalise data by number of balls delivered if required
    #     y_axis_label = metric_extras.capitalize()
    #     if normalise_extras:
    #         bowling_match_data_df['METRIC'] = bowling_match_data_df['METRIC'] / (bowling_match_data_df['BALLS'] / 6)
    #         y_axis_label = f'{metric_extras.capitalize()} per Over'

    #     # Sort data by metric count
    #     bowling_match_data_df = bowling_match_data_df.sort_values(by='METRIC', ascending=False)

    #     # Calculate total metric per bowler (summing across all venues)
    #     df_sorted = bowling_match_data_df.groupby('BOWLER', as_index=False)['METRIC'].sum()

    #     # Sort by total metric (descending)
    #     df_sorted = df_sorted.sort_values(by='METRIC', ascending=False)

    #     # Merge sorted order back to original df_grouped
    #     bowling_match_data_df = bowling_match_data_df.set_index('BOWLER').loc[df_sorted['BOWLER']].reset_index()

    #     # Remove rows where metric is equal to zero
    #     bowling_match_data_df = bowling_match_data_df[bowling_match_data_df['METRIC'] != 0]

    #     # Configure bar chart
    #     fig = px.bar(
    #         bowling_match_data_df,
    #         x='BOWLER',
    #         y='METRIC',
    #         color='VENUE',
    #         barmode='group',
    #         title=f"{y_axis_label} Conceded by Bowlers at Different Venues",
    #         labels={'METRIC': y_axis_label},
    #         color_discrete_map={'Home': '#316151', 'Away': '#FFE31A'},
    #         hover_name='BOWLER',
    #         hover_data={
    #             'BALLS': True,
    #             metric_extras: True
    #         }
    #     )

    #     # Render bar chart
    #     st.plotly_chart(fig)
