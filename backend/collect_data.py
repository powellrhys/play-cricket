# Import python dependencies
from dotenv import load_dotenv

# Import data functions
from functions.data_functions import (
    write_df_to_blob,
    APIService,
    Variables
)

# Load environment variables
load_dotenv()
vars = Variables()

app = APIService(api_token=vars.api_token,
                 site_id=int(vars.site_id),
                 variables=vars)

app.collect_match_ids(seasons=[2024])

app.collect_match_data()

app.generate_how_out_df()

write_df_to_blob(df=app.how_out_df,
                 connection_string=vars.blob_connection_string,
                 container_name='play-cricket',
                 blob_name='batting_how_out.csv')

# write_df_to_blob(df=app.all_batting_df,
#                  connection_string=vars.blob_connection_string,
#                  container_name='play-cricket',
#                  blob_name='batting_data.csv')
