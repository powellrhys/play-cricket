# Import python dependencies
from datetime import datetime
from typing import Tuple
import streamlit as st

def season_range_slider(
    key: str
) -> Tuple[float, float]:
    """
    Renders a Streamlit slider for selecting a range of seasons (years).

    The slider allows users to pick a year range within the last 20 years, defaulting to the last 5 years.
    It is useful for filtering data based on seasonal or yearly values.

    Args:
        key (str): A unique key to identify the widget in Streamlit and avoid conflicts.

    Returns:
        Tuple[float, float]: A tuple containing the selected start and end years as float values.
    """
    # Render season slider
    season = st.slider(label='Season Range',
                       min_value=datetime.now().year - 10,
                       max_value=datetime.now().year,
                       value=[datetime.now().year - 5, datetime.now().year],
                       key=key)

    return season
