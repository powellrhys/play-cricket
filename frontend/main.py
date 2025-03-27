# Import python dependencies
from dotenv import load_dotenv

from functions.data_functions import (
    Variables
)

from functions.navigation import (
    get_navigation
)

# Load environment variables
load_dotenv()
vars = Variables()

pg = get_navigation(club=vars.club)
pg.run()
