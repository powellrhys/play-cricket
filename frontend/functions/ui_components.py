# Import python dependencies
import streamlit as st
import warnings

def configure_page_config(
    initial_sidebar_state: str = "expanded",
    layout: str = "wide"
) -> None:
    """
    """
    # Set page config
    st.set_page_config(
        initial_sidebar_state=initial_sidebar_state,
        layout=layout,
        page_icon='🏏',
        menu_items={
            "Report a Bug": "https://github.com/powellrhys/play-cricket/issues"
        }
    )

    warnings.filterwarnings("ignore")
