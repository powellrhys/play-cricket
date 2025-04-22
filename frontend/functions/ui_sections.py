# Import python dependencies
import streamlit as st

# Import data functions
from functions.data_functions import (
    CricketData,
    Variables
)

# Import project ui components
from functions.ui_components import (
    season_range_slider,
    data_source_badge
)

# Import project mapping variables
from functions.mapping import (
    batting_dismissal_colour_map
)

# Import plotter class
from functions.plot_functions import (
    PlotlyPlotter
)

def render_batting_player_runs_scored(
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
        season = season_range_slider(key='player-batting-runs-season-slider')

    # Render data source metadata badge
    data_source_badge(blob_connection_string=vars.blob_connection_string,
                      file_name='batting_data.csv')

    # Transform season column to only include numeric values & remove not out marker
    data.remove_all_season_data()
    data.remove_not_out_marker()

    # Filter data based on streamlit inputs
    data.filter_data_by_player(player_name=batter)
    data.filter_data_by_season_range(season=season)

    # Generate plotting object
    plt = PlotlyPlotter(df=data.return_dataframe(),
                        x='SEASON',
                        y=batting_metric,
                        title=f'{batting_metric.capitalize()} per Season - {batter}',
                        labels={'RUNS': 'Runs', 'SEASON': 'Season'},
                        text=batting_metric,
                        color='INNS',
                        color_continuous_scale='Greens')

    # Generate bar plot and group x axis by season column
    plt.plot_bar()
    fig = plt.group_x_axis(groupby_metric='SEASON')

    # Render bar plot
    st.plotly_chart(fig)


def render_batting_player_how_out(
    data: CricketData,
    vars: Variables
) -> None:
    """
    """
    # Collect unique drop down metrics
    batters_how_out = data.collect_unique_column_values('PLAYER')

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

    # Render season slider within final column
    with cols[3]:
        season = season_range_slider(key='player-batting-howout-season-slider')

    # Render data source metadata badge
    data_source_badge(blob_connection_string=vars.blob_connection_string,
                      file_name='batting_how_out.csv')

    # Filter dataframe by season range and player name
    data.remove_all_season_data()
    data.filter_data_by_player(player_name=batter)
    data.filter_data_by_season_range(season=season)

    # Melt the dataframe to long format
    data.melt_dataframe(
        id_vars=['SEASON', 'PLAYER'],
        value_vars=[col for col in data.return_dataframe_columns()
                    if col not in ['SEASON', 'PLAYER']],
        var_name='Dismissal Type',
        value_name='Dismissal Count'
    )

    # Filter out NaN and data with zero records
    data.fill_nan(columns=['Dismissal Count'])
    data.filter_out_data(column='Dismissal Count',
                                filter_value=0.0)

    # Generate plotting object
    plt = PlotlyPlotter(df=data.return_dataframe(),
                        x='SEASON',
                        y='Dismissal Count',
                        color='Dismissal Type',
                        title='Dismissals by Type per Season',
                        color_discrete_map=batting_dismissal_colour_map)

    # Configure bar plot
    if plot_type == 'Bar':
        plt.plot_bar(barmode='group',)

    # Configure area plot
    if plot_type == 'Area':
        plt.plot_area()

    # Configure line plot
    if plot_type == 'Line':
        plt.plot_line()

    # Group X axis by Season column
    fig = plt.group_x_axis(groupby_metric='SEASON')

    # Render plot
    st.plotly_chart(fig)
