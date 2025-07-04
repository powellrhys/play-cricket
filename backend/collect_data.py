# Import python dependencies
from dotenv import load_dotenv
from datetime import datetime

# Import project dependencies
from backend.functions.data_functions import (
    write_df_to_blob,
    APIService,
    Variables
)
from backend.functions.logging_functions import (
    logger
)

# Load environment variables
load_dotenv()
vars = Variables()

# Generate API service class
app = APIService(api_token=vars.api_token,
                 site_id=int(vars.site_id),
                 variables=vars)

# Specify season data to collect
seasons = list(range(int(datetime.now().year), int(datetime.now().year)-11, -1))

# Collect match ids from seasons specified
app.collect_match_ids(seasons=seasons)

# Collect match report data
app.collect_match_data()

# Generate how out dataframe
app.generate_how_out_df()

# Generate batting summary dataframe
app.generate_batting_summary_df()

# Generate bowling summary dataframe
app.generate_bowling_summary_df()

# Generate bowling dismissals summary dataframe
app.generate_bowling_dismissals_summary_df()

# Write how out dataframe to blob
logger.info('Writing batting_how_out.csv to blob...')
write_df_to_blob(df=app.how_out_df,
                 connection_string=vars.blob_connection_string,
                 container_name='play-cricket',
                 blob_name='batting_how_out.csv')
logger.info('batting_how_out.csv written to blob \n')

# Write batting data summary to blob
logger.info('Writing batting_data.csv to blob...')
write_df_to_blob(df=app.summary_batting_df,
                 connection_string=vars.blob_connection_string,
                 container_name='play-cricket',
                 blob_name='batting_data.csv')
logger.info('batting_data.csv written to blob \n')

# Write bowling data summary to blob
logger.info('Writing bowling_data.csv to blob...')
write_df_to_blob(df=app.summary_bowling_df,
                 connection_string=vars.blob_connection_string,
                 container_name='play-cricket',
                 blob_name='bowling_data.csv')
logger.info('bowling_data.csv written to blob \n')

# Write bowling dismissals dataframe to blob
logger.info('Writing bowling_dismissals.csv to blob...')
write_df_to_blob(df=app.bowling_dismissal_summary_df,
                 connection_string=vars.blob_connection_string,
                 container_name='play-cricket',
                 blob_name='bowling_dismissals.csv')
logger.info('bowling_dismissals.csv written to blob \n')
