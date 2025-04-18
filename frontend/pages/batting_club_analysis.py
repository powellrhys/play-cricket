# Import python dependencies
from dotenv import load_dotenv
import plotly.express as px
import streamlit as st

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
    st.title(f'{vars.club.capitalize()} CC Batting  Analysis')

    # Read batting data dataframe from blob
    batting_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                    container_name='play-cricket',
                                    blob_name='batting_data.csv')

    # Collect unique drop down metrics
    seasons_overs = batting_df['SEASON'].unique()

    # Configure tab components
    tabs = st.tabs(['Club Batting Overview'])

    # Render components in the first tab
    with tabs[0]:

        # Render columns
        cols = st.columns([2, 1, 2])

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
                                    options=['RUNS',
                                             'HIGH SCORE',
                                             'DUCKS'],
                                    selection_mode='single',
                                    default='RUNS',
                                    key='pills-overs')

        # Render data source metadata badge
        data_source_badge(blob_connection_string=vars.blob_connection_string,
                          file_name='batting_data.csv')

        # Filter batting data by season and change high score data type
        batting_df = batting_df[batting_df['SEASON'] == season_overs]
        batting_df['HIGH SCORE'] = batting_df['HIGH SCORE'].str.replace('*', '', regex=False).astype('float')

        # Create scatter plot
        fig = px.scatter(
            batting_df,
            x="INNS",
            y=metric_overs,
            title=f"{metric_overs} vs Innings",
            labels={"INNS": "Innings", "RUNS": "Runs"},
            trendline='ols',
            hover_data=["PLAYER", "AVG", "HIGH SCORE"]
        )

        # Set all points to color #316151
        fig.update_traces(marker=dict(color='#316151'))

        # Render Scatter plot
        st.plotly_chart(fig)
