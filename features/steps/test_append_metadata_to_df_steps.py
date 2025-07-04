# Import Python dependencies
from behave import given, when, then
import pandas as pd

# Import project dependencies
from backend.functions.data_functions import (
    APIService,
    Variables
)

@given('the following match DataFrame')
def step_given_match_dataframe(context):
    # Configure classes
    variables = Variables
    context.processor = APIService(api_token='abc', site_id=123, variables=variables)

    # Input data from feature file into dataframe
    data = []
    for row in context.table:
        data.append({
            'player': row['player'],
            'how_out': row['how_out']
        })

    # Store initial DataFrame
    context.input_df = pd.DataFrame(data)

@when('I append metadata with home_away "{home_away}", opponent "{opponent}", and match_date "{match_date}"')
def step_when_append_metadata(context, home_away, opponent, match_date):
    # Call append_metadata_to_df
    context.result_df = context.processor.append_metadata_to_df(
        df=context.input_df.copy(),
        home_away=home_away,
        opponent=opponent,
        match_date=match_date
    )

@then('the resulting DataFrame should be')
def step_then_result_should_be(context):
    # Build expected DataFrame
    expected_data = []
    for row in context.table:
        expected_data.append({
            'player': row['player'],
            'how_out': row['how_out'],
            'home_away': row['home_away'],
            'opponent': row['opponent'],
            'match_date': pd.to_datetime(row['match_date'], format='%d/%m/%Y'),
            'year': int(row['year']),
        })

    expected_df = pd.DataFrame(expected_data).sort_values(by='player').reset_index(drop=True)
    actual_df = context.result_df.sort_values(by='player').reset_index(drop=True)

    # Compare selected columns
    pd.testing.assert_frame_equal(actual_df[expected_df.columns], expected_df, check_dtype=False)
