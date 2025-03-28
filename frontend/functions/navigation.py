# Import python dependencies
import streamlit as st

def get_navigation(
    club: str
) -> st.navigation:
    """
    Function to configure application navigation and connections between pages

    Args:
        club (str): Club name of application

    Raise:
        TypeError: If club input parameter not string

    Return:
        nav (st.navigation()): Streamlit navigation object

    """
    # Ensure club argument is string
    if not isinstance(club, str):
        raise TypeError(f'Argument club is type: {type(club)}, value should be string')

    # Construct pages dictionary
    pages = {
        f'{club.capitalize()} CC': [st.Page("pages/home.py", title="Home")],
        "Batting": [
            st.Page("pages/batting_overview.py", title="Batting Overview"),
            st.Page("pages/batting_dismissal_overview.py", title="Dismissal Overview")
        ],
        "Bowling": [
            st.Page("pages/bowling_club_analysis.py", title="Club Analysis"),
            st.Page("pages/bowling_player_analysis.py", title="Player Analysis")
        ],
        "Data": [
            st.Page("pages/extract_data.py", title="Extract & Download Data")
        ]
    }

    # Construct streamlit navigation object
    nav = st.navigation(pages)

    return nav
