# Import python dependencies
import streamlit as st
import pandas as pd

# Import project functions
from functions.data_functions import (
    list_blob_files,
    CricketData,
    Variables
)
from functions.plot_functions import (
    PlotlyPlotter
)
from functions.ui_components import (
    season_range_slider,
    data_source_badge
)
from functions.mapping import (
    batting_dismissal_colour_map
)

def render_extract_data(
    vars: Variables
) -> None:
    """
    """
    # Render page title
    st.title('Extract Club Data')

    # List all files in blob container
    files, _ = list_blob_files(connection_string=vars.blob_connection_string,
                               container_name='play-cricket')

    # Configure page columns
    cols = st.columns([2, 3])

    # Render components within the first column
    with cols[0]:
        # Render select box for downloadable files
        file = st.selectbox(label='File',
                            options=files)

        # Download file from csv
        df = CricketData(blob_connection_string=vars.blob_connection_string,
                         container_name='play-cricket',
                         blob_name=file).return_dataframe()

        # Render dataframe download button
        st.download_button(
            label="Download Data",
            data=df.to_csv().encode("utf-8"),
            file_name=file,
            mime="text/csv",
            icon=":material/download:"
        )

    # Render expander for dataframe preview
    with st.expander(label='Preview Data',
                     expanded=False):

        # Render data in dataframe format
        st.dataframe(df)

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

def render_batting_club_batting_overview(
    data: CricketData,
    vars: Variables
) -> None:
    """
    """
    # Collect unique drop down metrics
    seasons_overs = data.collect_unique_column_values('SEASON')

    # Render columns
    cols = st.columns([2, 1, 2])

    # Render season select box within first columns
    with cols[0]:
        season = st.selectbox(label='Season',
                              options=seasons_overs,
                              key='club-batting-overview-selectbox-overs')

    # Render metric pills within 3rd column
    with cols[2]:
        metric = st.pills(label='Metric',
                          options=['RUNS', 'HIGH SCORE', 'DUCKS'],
                          selection_mode='single',
                          default='RUNS',
                          key='club-batting-overview-metric-pills')

    # Render data source metadata badge
    data_source_badge(blob_connection_string=vars.blob_connection_string,
                      file_name='batting_data.csv')

    # Filter data by season and remove not out marker
    data.filter_by_column(column='SEASON', filter_value=season)
    data.remove_not_out_marker(column_name='HIGH SCORE')

    # Generate plotting object
    plt = PlotlyPlotter(df=data.return_dataframe(),
                        x="INNS",
                        y=metric,
                        title=f"{metric} vs Innings",
                        labels={"INNS": "Innings", "RUNS": "Runs"},
                        trendline='ols',
                        hover_data=["PLAYER", "AVG", "HIGH SCORE"]
                        )

    fig = plt.plot_scatter().update_traces(marker=dict(color='#316151'))

    # Render Scatter plot
    st.plotly_chart(fig)


def render_bowling_club_bowling_effectiveness(
    data: CricketData,
    vars: Variables
) -> None:
    # Collect unique seasons found in dataset
    seasons = data.collect_unique_column_values(column_name='SEASON')

    # Render streamlit columns
    cols = st.columns([2, 1, 1, 1])

    # Render components within first column
    with cols[0]:

        # Render season selectbox
        season = st.selectbox(label='Season',
                                    options=seasons,
                                    key='club-bowling-effectiveness-season-selectbox')

    # Render components within 3rd column
    with cols[2]:

        # Render metric pills
        metric = st.pills(label='Metric',
                          options=['WICKETS', 'RUNS'],
                          selection_mode='single',
                          default='WICKETS',
                          key='club-bowling-effectiveness-metric-pills')

    # Filter bowling data by season
    data.filter_by_column(column='SEASON', filter_value=season)

    # Render data source metadata badge
    data_source_badge(blob_connection_string=vars.blob_connection_string,
                      file_name='bowling_data.csv')

    # Generate plotting object
    plt = PlotlyPlotter(df=data.return_dataframe(),
                        x='OVERS',
                        y=metric,
                        hover_name='PLAYER',
                        trendline='ols',
                        title=f'{metric.capitalize()} for every over bowled')

    # Generate scatter plot
    fig = plt.plot_scatter().update_traces(marker=dict(color='#316151'))

    # Render scatter plot
    st.plotly_chart(fig)

def render_bowling_club_extras_analysis(
    data: CricketData,
    vars: Variables
) -> None:
    """
    """
    # Collect year from bowling match report data
    data.convert_column_to_datetime(column_name='DATE')
    data.create_year_column(date_column_name='DATE', year_column_name='SEASON')

    # Collect unique list of seasons
    seasons = data.collect_unique_column_values(column_name='SEASON')

    # Perform transformations and append data to seasons lists
    oldest_season = min(seasons)
    seasons.append('ALL')
    seasons.reverse()

    # Render columns
    cols = st.columns([2, 1, 1, 1])

    # Render season selectbox within first column
    with cols[0]:
        season = st.selectbox(label='Season',
                              options=seasons,
                              key='club-bowling-extras-season-selectbox')

    # Render metric pills within the second column
    with cols[2]:
        metric = st.pills(label='Metric',
                          options=['WIDES', 'NO BALLS'],
                          selection_mode='single',
                          default='WIDES',
                          key='club-bowling-extras-metric-pills')

    # Render normalise pill within the 4th column
    with cols[3]:
        normalise = st.pills(label='Normalise Data',
                             options=[True, False],
                             selection_mode='single',
                             default=False,
                             key='club-bowling-extras-normalise-pill')

    # Render data source metadata badge
    data_source_badge(blob_connection_string=vars.blob_connection_string,
                      file_name='bowling_match_data.csv',
                      additional_comments=f'Data dated back to {oldest_season} season')

    # Collect bowling data and convert to dataframe
    bowling_match_data_df = data.return_dataframe()

    # Apply lambda function to calculate the number of ball delivered
    bowling_match_data_df['BALLS'] = \
        bowling_match_data_df['OVERS'] \
        .apply(lambda x: (int(str(x).split('.')[0]) * 6) + int(str(x).split('.')[1][0])
               if '.' in str(x) else int(x) * 6)

    # Aggregate all data
    all_data = bowling_match_data_df.groupby(['BOWLER', 'VENUE'], as_index=False)[
        ['BALLS', 'MAIDENS', 'WICKETS', 'RUNS', 'WIDES', 'NO BALLS']
    ].sum()

    # Add season column to aggregated dataframe
    all_data['SEASON'] = 'ALL'

    # Group data by bowler, season and venue
    bowling_match_data_df = bowling_match_data_df.groupby(['BOWLER', 'SEASON', 'VENUE'], as_index=False)[
        ['BALLS', 'MAIDENS', 'WICKETS', 'RUNS', 'WIDES', 'NO BALLS']
    ].sum()

    # Append aggregated data to dataframe
    bowling_match_data_df = pd.concat([bowling_match_data_df, all_data], ignore_index=True)

    # Filter bowling report data by season
    bowling_match_data_df = bowling_match_data_df[bowling_match_data_df['SEASON'] == season]

    # Create dynamic metric column
    bowling_match_data_df['METRIC'] = bowling_match_data_df[metric]

    # Normalise data by number of balls delivered if required
    y_axis_label = metric.capitalize()
    if normalise:
        bowling_match_data_df['METRIC'] = bowling_match_data_df['METRIC'] / (bowling_match_data_df['BALLS'] / 6)
        y_axis_label = f'{metric.capitalize()} per Over'

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

    # Generate plotting object
    plt = PlotlyPlotter(df=bowling_match_data_df,
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
                            metric: True
                        })

    # Generate bar plot
    fig = plt.plot_bar()

    # Render figure
    st.plotly_chart(fig)


def render_bowling_club_wicket_taking(
    data: CricketData,
    vars: Variables
) -> None:
    """
    """
    # Collect a list of unique seasons from dataframe
    season = data.collect_unique_column_values(column_name='SEASON')

    # Render columns
    cols = st.columns([2, 1, 1, 1])

    # Render components within first column
    with cols[0]:

        # Render season select box
        season = st.selectbox(label='Season',
                              options=season,
                              key='club-bowling-wicket-season-selectbox')

    # Render data source metadata badge
    data_source_badge(blob_connection_string=vars.blob_connection_string,
                      file_name='bowling_dismissals.csv')

    # Filter data by season
    data.filter_by_column(column='SEASON', filter_value=season)

    # Group data by season and aggregate wicket taking types
    data.aggregate_dataframe(groupby_columns=['SEASON'],
                             agg_columns=['BOWLED', 'CAUGHT', 'LBW', 'STUMPED', 'HIT ROOF'],
                             agg_func='sum')

    # Collet dataframe, drop season column and sum each column, rename dataframe columns
    wicket_taking_df = data.return_dataframe()
    wicket_taking_df = wicket_taking_df.drop(columns=['SEASON']).sum().reset_index()
    wicket_taking_df.columns = ['Dismissal Type', 'Count']

    # Generate plotting object
    plt = PlotlyPlotter(df=wicket_taking_df,
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
                        })

    # Generate pie plot figure
    fig = plt.plot_pie()

    # Render pie chart
    st.plotly_chart(fig)
