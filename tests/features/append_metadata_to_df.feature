Feature: Append metadata to match DataFrame
  As a user of the APIService class
  I want to append match metadata to a DataFrame
  So that each row includes match context and cleaned dismissal info

  Scenario: Appending metadata and mapping dismissal types
    Given the following match DataFrame
      | player  | how_out   |
      | Alice   | b         |
      | Bob     | ct        |
      | Charlie | lbw       |
      | Dave    | run out   |
      | Emma    | unknown   |
    When I append metadata with home_away "Home", opponent "Rivals", and match_date "15/06/2023"
    Then the resulting DataFrame should be
      | player  | how_out   | home_away | opponent | match_date | year |
      | Alice   | Bowled    | Home      | Rivals   | 15/06/2023 | 2023 |
      | Bob     | Caught    | Home      | Rivals   | 15/06/2023 | 2023 |
      | Charlie | LBW       | Home      | Rivals   | 15/06/2023 | 2023 |
      | Dave    | Run Out   | Home      | Rivals   | 15/06/2023 | 2023 |
      | Emma    | Other     | Home      | Rivals   | 15/06/2023 | 2023 |
