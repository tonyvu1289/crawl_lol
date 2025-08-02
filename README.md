# Live LoL Odds Monitor

A Python script to monitor live odds for League of Legends matches using the esportsmatrix API. This tool can track specific games (Game 1, Game 2, Game 3, etc.) and monitor odds changes in real-time.

## Features

- Monitor live LoL match odds in real-time
- Track specific games (Game 1, 2, 3, etc.) or all games
- Detect and log odds changes
- Flexible monitoring intervals
- Command-line interface with various options
- Comprehensive logging to both console and file

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make the script executable (optional):
```bash
chmod +x live_odds_monitor.py
```

## Usage

### Command Line Options

```bash
# Monitor a specific game (e.g., Game 1) with 30-second intervals
python live_odds_monitor.py --game 1 --interval 30

# Monitor all live games with 10-second intervals
python live_odds_monitor.py --all-games --interval 10

# List all currently live games and exit
python live_odds_monitor.py --list

# Monitor for a limited number of iterations
python live_odds_monitor.py --game 2 --interval 15 --max-iterations 20

# Get help
python live_odds_monitor.py --help
```

### Examples

#### Monitor Game 1 Only
```bash
python live_odds_monitor.py --game 1 --interval 30
```

#### Monitor All Games
```bash
python live_odds_monitor.py --all-games --interval 15
```

#### List Live Games
```bash
python live_odds_monitor.py --list
```

### Programmatic Usage

You can also use the monitor programmatically:

```python
from live_odds_monitor import LoLOddsMonitor

# Create monitor instance
monitor = LoLOddsMonitor()

# List live games
monitor.list_live_games()

# Monitor Game 1 for 10 iterations with 30-second intervals
monitor.monitor_odds(target_game=1, interval=30, max_iterations=10)

# Monitor all games continuously
monitor.monitor_odds(target_game=None, interval=20)
```

## Output Example

```
================================================================================
LIVE LOL ODDS - 2025-01-15 14:30:25
================================================================================

Game 1: Team Liquid vs Cloud9
Status: Live
Odds:
  Team Liquid: 1.85
  Cloud9: 1.95

----------------------------------------------------------------

Game 2: Team Liquid vs Cloud9
Status: Not Started
Odds:
  Team Liquid: 1.90
  Cloud9: 1.90

----------------------------------------------------------------
```

## API Information

The script uses the esportsmatrix API with the following endpoints:

1. **GetIndexMatchV2** - Fetch live matches
2. **GetMatchDetailsByParentV2** - Get detailed odds for specific matches

### API Parameters

- `GameCat`: 1 (League of Legends)
- `SportId`: 45 (LoL Sport ID)
- `HasLive`: true (for live matches only)
- `Language`: "eng"
- `Timezone`: "07:00:00"

## Logging

The script logs to both console and a file (`live_odds_monitor.log`):

- Info: General monitoring information and odds changes
- Warning: Issues like no live matches found
- Error: API errors, request failures, etc.

## Files

- `live_odds_monitor.py` - Main monitoring script
- `example_usage.py` - Example usage demonstrations
- `requirements.txt` - Python dependencies
- `crawl_instruction.md` - Original API documentation
- `live_odds_monitor.log` - Log file (created when running)

## Error Handling

The script includes comprehensive error handling for:

- Network connectivity issues
- API rate limiting
- Invalid responses
- JSON parsing errors
- Missing data fields

## Limitations

- Requires active internet connection
- Dependent on esportsmatrix API availability
- May be subject to API rate limits
- Only supports League of Legends matches

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
