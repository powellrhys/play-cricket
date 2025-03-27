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
    configure_page_config
)

# Load environment variables
load_dotenv()
vars = Variables()

# Set page config
configure_page_config()

# Ensure user is authenticated to use application
if not st.experimental_user.is_logged_in:
    st.login('auth0')

if st.experimental_user.is_logged_in:

    # Render page title
    st.title(f'{vars.club.capitalize()} CC Bowling Analysis')

    bowling_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                         container_name='play-cricket',
                                         blob_name='bowling_data.csv')

    bowling_match_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                               container_name='play-cricket',
                                               blob_name='bowling_match_data.csv')

    bowling_match_data_df['DATE'] = pd.to_datetime(bowling_match_data_df['DATE'])
    bowling_match_data_df['SEASON'] = bowling_match_data_df['DATE'].dt.year

    seasons_overs = bowling_data_df['SEASON'].unique()
    seasons_extras = bowling_match_data_df['SEASON'].unique()

    tab1, tab2 = st.tabs(tabs=['Bowling Effectiveness', 'Extras Analysis'])

    with tab1:

        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:

            season_overs = st.selectbox(label='Season',
                                        options=seasons_overs,
                                        key='selectbox-overs')

        with col2:

            metric_overs = st.pills(label='Metric',
                                    options=['WICKETS', 'RUNS'],
                                    selection_mode='single',
                                    default='WICKETS',
                                    key='pills-overs')

        bowling_data_df = bowling_data_df[bowling_data_df['SEASON'] == season_overs]

        fig = px.scatter(data_frame=bowling_data_df,
                         x='OVERS',
                         y=metric_overs,
                         hover_name='PLAYER',
                         trendline='ols')

        st.plotly_chart(fig)

    with tab2:

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:

            season_extras = st.selectbox(label='Season',
                                         options=seasons_extras,
                                         key='selectbox-extras')

        with col3:

            metric_extras = st.pills(label='Metric',
                                     options=['WIDES', 'NO BALLS'],
                                     selection_mode='single',
                                     default='WIDES',
                                     key='pills-extras')

        with col4:

            normalise_extras = st.pills(label='Normalise Data',
                                        options=[True, False],
                                        selection_mode='single',
                                        default=False,
                                        key='pills-extras-normalise')

        bowling_match_data_df = bowling_match_data_df[bowling_match_data_df['SEASON'] == season_extras]

        # Apply lambda function to calculate the number of ball delivered
        bowling_match_data_df['BALLS'] = \
            bowling_match_data_df['OVERS'] \
            .apply(lambda x: (int(str(x).split('.')[0]) * 6) + int(str(x).split('.')[1][0])
                   if '.' in str(x) else int(x) * 6)

        bowling_match_data_df = bowling_match_data_df.groupby(['BOWLER', 'SEASON', 'VENUE'], as_index=False)[
            ['BALLS', 'MAIDENS', 'WICKETS', 'RUNS', 'WIDES', 'NO BALLS']
        ].sum()

        bowling_match_data_df['METRIC'] = bowling_match_data_df[metric_extras]

        y_axis_label = metric_extras.capitalize()
        if normalise_extras:
            bowling_match_data_df['METRIC'] = bowling_match_data_df['METRIC'] / (bowling_match_data_df['BALLS'] / 6)
            y_axis_label = f'{metric_extras.capitalize()} per Over'

        bowling_match_data_df = bowling_match_data_df.sort_values(by='METRIC', ascending=False)

        # Calculate total wides per bowler (summing across all venues)
        df_sorted = bowling_match_data_df.groupby('BOWLER', as_index=False)['METRIC'].sum()

        # Sort by total wides (descending)
        df_sorted = df_sorted.sort_values(by='METRIC', ascending=False)

        # Merge sorted order back to original df_grouped
        bowling_match_data_df = bowling_match_data_df.set_index('BOWLER').loc[df_sorted['BOWLER']].reset_index()

        bowling_match_data_df = bowling_match_data_df[bowling_match_data_df['METRIC'] != 0]

        fig = px.bar(
            bowling_match_data_df,
            x='BOWLER',
            y='METRIC',
            color='VENUE',
            barmode='group',
            title=f"{y_axis_label} Conceded by Bowlers at Different Venues",
            labels={'METRIC': y_axis_label},
            hover_name='BOWLER',
            hover_data={
                'BALLS': True,
                metric_extras: True
            }
        )
        st.plotly_chart(fig)
        # st.dataframe(bowling_match_data_df)
