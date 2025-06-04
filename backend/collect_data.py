# Import python dependencies
from dotenv import load_dotenv
from datetime import datetime

# Import project dependencies
from functions.data_functions import (
    write_df_to_blob,
    APIService,
    Variables
)
from functions.logging_functions import (
    logger
)

# Load environment variables
load_dotenv()
vars = Variables()

app = APIService(api_token=vars.api_token,
                 site_id=int(vars.site_id),
                 variables=vars)

print(datetime.now().year)

seasons = list(range(int(datetime.now().year), int(datetime.now().year)-11, -1))

app.collect_match_ids(seasons=seasons)

app.collect_match_data()

app.generate_how_out_df()

app.generate_batting_summary_df()

app.generate_bowling_summary_df()

app.generate_bowling_dismissals_summary_df()

logger.info('Writing batting_how_out.csv to blob...')
write_df_to_blob(df=app.how_out_df,
                 connection_string=vars.blob_connection_string,
                 container_name='play-cricket',
                 blob_name='batting_how_out.csv')
logger.info('batting_how_out.csv written to blob \n')

logger.info('Writing batting_data.csv to blob...')
write_df_to_blob(df=app.summary_batting_df,
                 connection_string=vars.blob_connection_string,
                 container_name='play-cricket',
                 blob_name='batting_data.csv')
logger.info('batting_how_out.csv written to blob \n')

logger.info('Writing bowling_data.csv to blob...')
write_df_to_blob(df=app.summary_bowling_df,
                 connection_string=vars.blob_connection_string,
                 container_name='play-cricket',
                 blob_name='bowling_data.csv')
logger.info('batting_how_out.csv written to blob \n')

logger.info('Writing bowling_dismissals.csv to blob...')
write_df_to_blob(df=app.bowling_dismissal_summary_df,
                 connection_string=vars.blob_connection_string,
                 container_name='play-cricket',
                 blob_name='bowling_dismissals.csv')
logger.info('batting_how_out.csv written to blob \n')
