Feature: Generate HOW_OUT DataFrame summary
  As a user of the class
  I want to generate a summary DataFrame of how batsmen got out per season
  So that I can analyze player dismissals over time

  Scenario: Grouping and renaming how_out data from batting DataFrame
    Given the following all_batting_df data:
      | batsman_name | year | how_out    |
      | Player1      | 2023 | caught     |
      | Player1      | 2023 | bowled     |
      | Player1      | 2023 | caught     |
      | Player2      | 2022 | lbw        |
      | Player2      | 2022 | caught     |
      | Player2      | 2022 | caught     |
    When I call generate_how_out_df
    Then how_out_df should contain the following data:
      | PLAYER  | SEASON | CAUGHT | BOWLED | LBW |
      | Player1 | 2023   | 2      | 1      | 0   |
      | Player2 | 2022   | 2      | 0      | 1   |
