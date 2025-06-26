# Import python dependencies
from dotenv import load_dotenv
import streamlit as st

from functions.data_functions import (
    Variables
)
from functions.navigation import (
    get_navigation
)
# from functions.config import (
#     generate_secrets_config_file
# )
# import time

load_dotenv()

# if 'secrets_initialized' not in st.session_state:
#     generate_secrets_config_file()
#     st.session_state['secrets_initialized'] = True
#     progress_text = 'Configuring application backend'
#     my_bar = st.progress(0, text=progress_text)
#     for percent_complete in range(100):
#         time.sleep(0.01)
#         my_bar.progress(percent_complete + 1, text=progress_text)
#     time.sleep(1)

# Load environment variables
load_dotenv()
vars = Variables()

# Ensure user is authenticated to use application
if not st.experimental_user.is_logged_in:
    st.login('auth0')

# Render application if user is logged in
if st.experimental_user.is_logged_in:
    pg = get_navigation(club=vars.club)
    pg.run()
