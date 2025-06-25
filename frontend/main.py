# Import python dependencies
from dotenv import load_dotenv
import streamlit as st

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
load_dotenv()
generate_secrets_config_file()
vars = Variables()

# Ensure user is authenticated to use application
if not st.experimental_user.is_logged_in:
    st.login('auth0')

# Render application if user is logged in
if st.experimental_user.is_logged_in:
    pg = get_navigation(club=vars.club)
    pg.run()
