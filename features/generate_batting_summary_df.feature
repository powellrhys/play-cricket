Feature: Generate batting summary DataFrame
  As a user of the APIService class
  I want to generate a season-wise batting summary
  So that I can analyze players' seasonal performances

  Scenario: Summarizing batting stats from individual match data
    Given the following batting records for summary:
      | batsman_name | year | runs | fours | sixes | how_out       |
      | Alice        | 2023 | 0    | 0     | 0     | bowled        |
      | Alice        | 2023 | 65   | 10    | 1     | caught        |
      | Alice        | 2023 | 101  | 15    | 3     | lbw           |
      | Bob          | 2022 | 45   | 6     | 0     | caught        |
      | Bob          | 2022 | 60   | 8     | 1     | caught        |
    When I call generate_batting_summary_df
    Then summary_batting_df should contain the following data
      | PLAYER | SEASON | GAMES | INNS | RUNS | HIGH SCORE | 50s | 100s | 4s | 6s | DUCKS |
      | Alice  | 2023   | 3     | 3    | 166  | 101        | 1   | 1    | 25 | 4  | 1     |
      | Bob    | 2022   | 2     | 2    | 105  | 60         | 1   | 0    | 14 | 1  | 0     |
