import streamlit as st

def get_navigation(
    club: str
) -> st.navigation:
    """
    """
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

    return st.navigation(pages)
