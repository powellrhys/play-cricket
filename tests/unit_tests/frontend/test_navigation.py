# Import dependencies
from frontend.functions.navigation import get_navigation
from unittest.mock import patch
import pytest

def test_get_navigation_returns_nav_object():
    """
    Test that `get_navigation` returns a navigation object
    and correctly initializes Streamlit pages.

    The test ensures `get_navigation` properly builds and returns a navigation
    structure when provided with a valid club name.
    """
    with patch("frontend.functions.navigation.st.Page") as \
            mock_page, patch("frontend.functions.navigation.st.navigation") as mock_nav:

        mock_page.return_value = "page_obj"
        mock_nav.return_value = "nav_obj"

        nav = get_navigation("testclub")

        # Check if st.Page was called with correct arguments
        mock_page.assert_any_call("pages/home.py", title="Home")
        mock_page.assert_any_call("pages/batting_club_analysis.py", title="Club Analysis")
        mock_page.assert_any_call("pages/batting_player_analysis.py", title="Player Analysis")
        mock_page.assert_any_call("pages/bowling_club_analysis.py", title="Club Analysis")
        mock_page.assert_any_call("pages/bowling_player_analysis.py", title="Player Analysis")
        mock_page.assert_any_call("pages/extract_data.py", title="Extract & Download Data")

        # Check if st.navigation was called with the pages dictionary
        mock_nav.assert_called_once()

        # Ensure the function returns what st.navigation returns
        assert nav == "nav_obj"

def test_get_navigation_raises_typeerror():
    """
    Test that `get_navigation` raises a TypeError when provided
    with an invalid argument type.

    Ensures the function validates input types correctly.
    """
    with pytest.raises(TypeError):
        get_navigation(123)
