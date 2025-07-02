# Import python dependencies
from behave import given, when, then
import pandas as pd

# Import project dependencies
from backend.functions.data_functions import (
    APIService,
    Variables
)

@given('the following all_batting_df data')
def step_given_all_batting_df(context):

    # Configure classes
    variables = Variables
    context.processor = APIService(api_token='abc',
                                   site_id=123,
                                   variables=variables)

    # Input data from feature file into dataframe
    data = []
    for row in context.table:
        data.append({
            'batsman_name': row['batsman_name'],
            'year': int(row['year']),
            'how_out': row['how_out']
        })

    # Store data as dataframe object within class
    context.processor.all_batting_df = pd.DataFrame(data)

@when('I call generate_how_out_df')
def step_when_call_generate(context):
    # Execute generate how out function
    context.processor.generate_how_out_df()

@then('how_out_df should contain the following data')
def step_then_check_how_out_df(context):
    # Generate expected data dataframe
    expected_data = []
    for row in context.table:
        row_dict = {k: (int(v) if v.isdigit() else v) for k, v in row.items()}
        expected_data.append(row_dict)
    expected_df = pd.DataFrame(expected_data)

    # Sort columns and rows for reliable comparison
    expected_df = expected_df.sort_values(by=['PLAYER', 'SEASON']).reset_index(drop=True)
    actual_df = context.processor.how_out_df.sort_values(by=['PLAYER', 'SEASON']).reset_index(drop=True)

    # Compare DataFrames ignoring column order differences
    pd.testing.assert_frame_equal(actual_df[expected_df.columns], expected_df)
