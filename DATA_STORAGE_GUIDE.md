# Data Storage and Analysis Guide

The Live LoL Odds Monitor now includes comprehensive data storage functionality to capture and analyze live odds data for later analysis.

## Storage Formats

### 1. JSON Format (Default)
- **File naming**: `live_odds_YYYYMMDD_HHMMSS.json`
- **Structure**: Rich nested format with full context
- **Best for**: Detailed analysis, preserving complete data structure
- **Example**:
```json
[
  {
    "timestamp": "2025-08-03T00:13:24.295620",
    "game_data": {
      "match_id": 35256636,
      "match_name": "Game 1 Win (Live Odds)",
      "team1": "Fnatic",
      "team2": "Team Heretics",
      "status": 1,
      "game_number": 1,
      "odds": {
        "Fnatic": 1.528,
        "Team Heretics": 2.464
      }
    },
    "parent_match_info": {
      "league": "LEC 2025 Summer",
      "series_score": "0-0",
      "match_type": "BO3"
    }
  }
]
```

### 2. CSV Format
- **File naming**: `live_odds_YYYYMMDD_HHMMSS.csv`
- **Structure**: Flat table format
- **Best for**: Excel analysis, simple data processing
- **Columns**: timestamp, match_id, match_name, game_number, team1, team2, team1_odds, team2_odds, status, league, series_score

### 3. SQLite Database
- **File naming**: `live_odds.db` (single database for all sessions)
- **Structure**: Relational database with indexes
- **Best for**: Complex queries, large datasets, performance
- **Table schema**: 
  - `id` (auto-increment primary key)
  - `timestamp`, `match_id`, `match_name`, `game_number`
  - `team1`, `team2`, `team1_odds`, `team2_odds`
  - `status`, `league`, `series_score`, `raw_data`

## Usage Examples

### Start Monitoring with Data Storage

```bash
# JSON storage (default)
python3 live_odds_monitor.py --all-games --storage json

# CSV storage
python3 live_odds_monitor.py --game 1 --storage csv --interval 15

# SQLite storage with custom path
python3 live_odds_monitor.py --all-games --storage sqlite --storage-path ./my_data

# Monitor specific game until series ends
python3 live_odds_monitor.py --game 1 --interval 10 --storage json
```

### Analyze Stored Data

```bash
# List all available data files
python3 simple_analyze.py --list

# Analyze specific files
python3 simple_analyze.py --file live_odds_20250803_001324.json
python3 simple_analyze.py --file live_odds_20250803_001512.csv
python3 simple_analyze.py --file live_odds.db

# Use custom data directory
python3 simple_analyze.py --data-path ./my_data --list
```

## Data Analysis Features

### Basic Statistics
- Total records and time range
- Unique matches and teams
- Odds range and averages
- Game numbers tracked

### Odds Timeline
- Chronological view of odds changes
- Team-by-team odds progression
- Timestamps for each data point

### Advanced Analysis (SQLite)
- Complex queries for specific patterns
- Historical data aggregation
- Performance optimized with indexes

## Example Analysis Output

```
=== Analyzing live_odds_20250803_001324.json ===
Total records: 3
Time range: 2025-08-03T00:13:24 to 2025-08-03T00:13:34
Unique matches: 1
Game numbers: [1]
Teams: ['Fnatic', 'Team Heretics']
Odds range: 1.528 to 2.464
Average odds: 1.977

Odds Timeline:
  1. 2025-08-03T00:13:24
     Fnatic: 1.528
     Team Heretics: 2.464
  2. 2025-08-03T00:13:29
     Fnatic: 1.567
     Team Heretics: 2.368
  3. 2025-08-03T00:13:34
     Fnatic: 1.567
     Team Heretics: 2.368
```

## Use Cases for Analysis

### 1. Odds Movement Patterns
- Track how odds change during live games
- Identify momentum shifts
- Analyze betting market reactions

### 2. Value Betting Opportunities
- Find patterns in odds swings
- Identify overreactions in live betting
- Historical comparison of similar matchups

### 3. Market Efficiency Analysis
- Compare odds changes to actual game events
- Measure how quickly odds adjust
- Identify predictable patterns

### 4. Team Performance Correlation
- Correlate odds changes with team performance
- Track favorites vs underdogs performance
- Analyze series score impact on game odds

## Data Export and Integration

### For Excel Analysis
1. Use CSV format for direct Excel import
2. Or export SQLite data using SQL queries
3. Create pivot tables for trend analysis

### For Programming Analysis
1. JSON format provides richest data structure
2. SQLite allows complex SQL queries
3. Easy integration with pandas, numpy, matplotlib

### For Real-time Dashboards
1. SQLite database for live data feeds
2. JSON for web application integration
3. CSV for simple chart generation

## Storage Management

- **Automatic timestamping**: Each session creates unique files
- **Incremental storage**: Data saved during monitoring, not just at end
- **Crash recovery**: Data preserved even if monitoring interrupted
- **Space efficiency**: Choose format based on analysis needs

The data storage feature transforms the live odds monitor from a simple display tool into a comprehensive data collection and analysis platform for serious LoL betting analysis.
