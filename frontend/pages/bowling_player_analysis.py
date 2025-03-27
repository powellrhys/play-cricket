# Import python dependencies
from dotenv import load_dotenv
import plotly.express as px
import streamlit as st
from datetime import datetime

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
    st.title(f'{vars.club.capitalize()} CC Player Bowling Analysis')

    dismissal_data_df = read_csv_from_blob(connection_string=vars.blob_connection_string,
                                           container_name='play-cricket',
                                           blob_name='bowling_dismissals.csv')

    dismissal_data_df = dismissal_data_df[dismissal_data_df['SEASON'] != 'ALL']
    dismissal_data_df['SEASON'] = dismissal_data_df['SEASON'].astype(int)

    seasons_dismissals = dismissal_data_df['SEASON'].unique()
    bowlers = dismissal_data_df['PLAYER'].unique()

    tab1, tab2 = st.tabs(['Wicket Taking', 'Stats'])

    with tab1:

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:

            bowler = st.selectbox(label='Bowler',
                                  options=bowlers,
                                  key='selectbox-bowler')

        with col3:

            season = st.slider(label='Season Range',
                               min_value=datetime.now().year - 20,
                               max_value=datetime.now().year,
                               value=[datetime.now().year - 5, datetime.now().year])

        dismissal_data_df = \
            dismissal_data_df[
                (dismissal_data_df['SEASON'] >= season[0]) &
                (dismissal_data_df['SEASON'] <= season[1]) &
                (dismissal_data_df['PLAYER'] == bowler)]

        # Melt the dataframe to reshape it so 'bowled' and 'caught' are in a single column
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
                         'BOWLED': '#316151',   # Dark Green
                         'CAUGHT': '#FFE31A',   # Bright Yellow
                         'LBW': '#A63D40',  # Deep Red
                         'STUMPED': '#6495ED',    # Cornflower Blue
                         'Hit ROOF': '#D2B48C'})

        st.plotly_chart(fig)
        # st.dataframe(dismissal_data_df)
