# steps for generate_batting_summary_df
from behave import given, when, then
import pandas as pd
from backend.functions.data_functions import APIService, Variables

@given('the following batting records for summary')
def step_given_batting_records(context):
    # Initialize processor
    context.processor = APIService(api_token='abc', site_id=123, variables=Variables)

    # Convert table rows to dicts with correct types
    data = []
    for row in context.table:
        data.append({
            'batsman_name': row['batsman_name'],
            'year': int(row['year']),
            'runs': int(row['runs']),
            'fours': int(row['fours']),
            'sixes': int(row['sixes']),
            'how_out': row['how_out'].strip().title()
        })

    # Assign test DataFrame
    context.processor.all_batting_df = pd.DataFrame(data)

@when('I call generate_batting_summary_df')
def step_when_generate_summary(context):
    context.processor.generate_batting_summary_df()

@then('summary_batting_df should contain the following data')
def step_then_validate_summary(context):
    # Create expected DataFrame from table
    expected_data = []
    for row in context.table:
        expected_data.append({
            'PLAYER': row['PLAYER'],
            'SEASON': int(row['SEASON']),
            'GAMES': int(row['GAMES']),
            'INNS': int(row['INNS']),
            'RUNS': int(row['RUNS']),
            'HIGH SCORE': int(row['HIGH SCORE']),
            '50s': int(row['50s']),
            '100s': int(row['100s']),
            '4s': int(row['4s']),
            '6s': int(row['6s']),
            'DUCKS': int(row['DUCKS']),
        })

    expected_df = pd.DataFrame(expected_data)
    actual_df = context.processor.summary_batting_df

    # Sort for reliable comparison
    expected_df = expected_df.sort_values(by=['PLAYER', 'SEASON']).reset_index(drop=True)
    actual_df = actual_df.sort_values(by=['PLAYER', 'SEASON']).reset_index(drop=True)

    # Validate
    pd.testing.assert_frame_equal(
        actual_df[expected_df.columns],
        expected_df,
        check_dtype=False,
        check_like=True
    )
