# Import python dependencies
from dotenv import load_dotenv
import streamlit as st

# Import data functions
from functions.data_functions import (
    Variables
)

# Load environment variables
load_dotenv()
vars = Variables()

if not st.experimental_user.is_logged_in:
    st.login('auth0')

if st.experimental_user.is_logged_in:
    st.title('Home')
