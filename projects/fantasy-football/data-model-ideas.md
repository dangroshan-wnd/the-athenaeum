# 🏈 Fantasy Football Data Models Reference
# Notes (ctrl+shft+v for md view)

### `player_attributes`
| Complete? | Raw Source | Column Name | Description | Usefulness Rank |
|---|---|---|---|---|
| ❌ | | `age` | Player age at draft | 10 |
| ❌ | | `is_rookie` | Rookie flag | 10 |
| ❌ | | `injury_risk_score` | Weighted score based on past games missed | 10 |
| ✅ | core.appearances | `team_id` | Current NFL team | 9 |
| ✅ | core.appearances | `position` | Player position | 9 |
| ❌ | | `depth_chart_slot` | Expected role on depth chart (e.g., WR2) | 8 |
| ❌ | | `usage_slope` | Trend of touches/snaps over past year | 7 |
| ❌ | | `new_team_flag` | Changed teams this offseason | 7 |
| ❌ | | `contract_year_flag` | Is in a contract year | 6 |
| ✅ | core.appearances | `player_id` | 🔒 Primary Key | 5 |

### `team_attributes`
| Complete? | Raw Source | Column Name | Description | Usefulness Rank |
|---|---|---|---|---|
| ❌ | | `vegas_projected_ppg` | Vegas projected points per game | 10 |
| ❌ | | `avg_ppg_last_season` | Historical points per game | 9 |
| ❌ | | `pass_play_pct` | Pass play rate | 8 |
| ❌ | | `rush_play_pct` | Rush play rate | 8 |
| ❌ | | `targets_per_game` | Estimated target volume | 7 |
| ❌ | | `rb_touches_per_game` | Estimated RB usage | 7 |
| ❌ | | `offensive_line_rank` | O-line strength (e.g., PFF rank) | 6 |
| ❌ | | `neutral_script_rate` | Rate of play calls in neutral game scripts | 6 |
| ✅ | core.appearances | `team_id` | 🔒 Primary Key | 5 |
| ✅ | marts.draft_picks | `season` | 🔒 Primary Key | 5 |

### `draft_entry_metadata`
| Complete? | Raw Source | Column Name | Description | Usefulness Rank |
|---|---|---|---|---|
| ❌ | | `roster_structure_tags` | Tagged roster shape (e.g., 2QB) | 10 |
| ✅ | core__ud__draft_entries | `points_scored` | Total season points | 10 |
| ✅ | core__ud__draft_entries | `placement` | Final placement (1-12) | 9 |
| ❌ | | `cutline_diff` | Points above/below 3rd place cutline | 9 |
| ❌ | | `positional_spread` | Counts of players by position | 8 |
| ✅ | core__ud__draft_entry_picks | `selection_vs_adp_delta` | Reach or faller flag | 8 |
| ❌ | | `player_bye_week_spread_score` | Bye week overlap risk score | 7 |
| ❌ | | `team_stack_score` | Number of stacked teammates | 6 |
| ✅ | core__ud__draft_entries | `draft_entry_id` | 🔒 Primary Key | 5 |
| ✅ | core__ud__drafts | `draft_id` | Draft group identifier | 4 |
