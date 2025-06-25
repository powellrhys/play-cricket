# Import python dependencies
from dotenv import load_dotenv
import streamlit as st
import os

from functions.data_functions import (
    Variables
)
from functions.navigation import (
    get_navigation
)
from functions.config import (
    generate_secrets_config_file
)

# Load environment variables
if os.getenv('environemnt') != 'PRD':
    load_dotenv()

if "secrets_initialized" not in st.session_state:
    generate_secrets_config_file()
    st.session_state.secrets_initialized = True

vars = Variables()

# Ensure user is authenticated to use application
if not st.experimental_user.is_logged_in:
    st.login('auth0')

# Render application if user is logged in
if st.experimental_user.is_logged_in:
    pg = get_navigation(club=vars.club)
    pg.run()
