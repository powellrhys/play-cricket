# Import python dependencies
from datetime import datetime
import plotly.express as px
import streamlit as st

# Import data functions
from functions.data_functions import (
    CricketData,
    Variables
)

# Import project ui components
from functions.ui_components import (
    data_source_badge
)

def render_club_batting_runs_scored(
    data: CricketData,
    vars: Variables
) -> None:
    """
    """
    # Collect unique drop down metrics
    batters = data.collect_unique_column_values('PLAYER')

    # Render columns
    cols = st.columns([2, 2, 2, 2])

    # Render components within first column
    with cols[0]:

        # Render selectbox for batters metric
        batter = st.selectbox(label='Batter',
                              options=batters,
                              key='selectbox-batter-runs')

    # Render components in the second column
    with cols[1]:

        # Render selectbox for batting metric
        batting_metric = st.selectbox(label='Metric',
                                      options=['RUNS', 'HIGH SCORE', '50s', '100s',
                                               '4s', '6s', 'DUCKS'],
                                      key='selectbox-batter-metric')

    # Render components within 4th column
    with cols[3]:

        # Render season slider
        season = st.slider(label='Season Range',
                           min_value=datetime.now().year - 20,
                           max_value=datetime.now().year,
                           value=[datetime.now().year - 5, datetime.now().year],
                           key='season-slider-runs')

    # Render data source metadata badge
    data_source_badge(blob_connection_string=vars.blob_connection_string,
                      file_name='batting_data.csv')

    # Transform season column to only include numeric values & remove not out marker
    data.remove_all_season_data()
    data.remove_not_out_marker()

    # Filter data based on streamlit inputs
    data.filter_data_by_player(player_name=batter)
    data.filter_data_by_season_range(season=season)

    # Plot desired data in a bar chart
    fig = px.bar(data_frame=data.return_dataframe(),
                 x='SEASON',
                 y=batting_metric,
                 title=f'{batting_metric.capitalize()} per Season - {batter}',
                 labels={'RUNS': 'Runs', 'SEASON': 'Season'},
                 text=batting_metric,
                 color='INNS',
                 color_continuous_scale='Greens')

    # Update bar chart settings
    fig.update_traces(textposition='outside')
    fig.update_layout(xaxis=dict(type='category',
                                 categoryorder='array',
                                 categoryarray=sorted(data.return_dataframe()['SEASON'])),
                      uniformtext_minsize=8, uniformtext_mode='hide')

    # Render bar plot
    st.plotly_chart(fig)
