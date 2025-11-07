# Import dependencies
from streamlit_components.ui_components import configure_page_config
from functions.ui_sections import render_extract_data
from functions.data_functions import Variables
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()
vars = Variables()

# Set page config
configure_page_config(repository_name='play-cricket',
                      page_icon='🏏')

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# If user logged in, render streamlit components
if st.user.is_logged_in:

    # Render extract data ui section
    render_extract_data(vars=vars)
