# League of Legends Live Odds Monitor

## Project Overview

This project provides a comprehensive solution for monitoring live League of Legends esports betting odds in real-time using the esportsmatrix API. The system can track specific games, detect odds changes, store historical data, and provide analysis tools for betting strategy development.

## 🎯 Key Features

### Core Monitoring
- **Real-time Odds Tracking**: Monitor live LoL match odds as they change
- **Game-Specific Filtering**: Track specific games (Game 1, Game 2, Game 3, etc.)
- **Match Persistence**: Continue monitoring until matches completely end
- **Odds Change Detection**: Real-time detection and logging of odds movements

### Data Storage & Analysis
- **Multiple Storage Formats**: JSON, CSV, and SQLite database options
- **Historical Data Collection**: Automatic storage of all odds data
- **Analysis Tools**: Built-in statistics and trend analysis
- **Export Capabilities**: Data export for external analysis tools

### User Interfaces
- **Command Line Interface**: Full CLI with comprehensive options
- **Programmatic API**: Python classes for integration into other tools
- **Logging System**: Detailed logging for debugging and monitoring

## 📁 Project Structure

```
crawl_lol/
├── 📋 Core Files
│   ├── live_odds_monitor.py     # Main monitoring application
│   ├── simple_analyze.py        # Data analysis tool (no dependencies)
│   ├── analyze_odds_data.py     # Advanced analysis (requires pandas)
│   └── example_usage.py         # Usage examples and demonstrations
│
├── 📊 Legacy/Reference Files
│   └── legacy/                  # Original scripts (moved for organization)
│       ├── crawl_live_matches.py    # Original scraping script (reference)
│       └── test_lol_odds.py         # Original testing script (reference)
│
├── 📖 Documentation
│   ├── README.md                # Main project documentation
│   ├── DATA_STORAGE_GUIDE.md    # Data storage and analysis guide
│   └── MONITORING_UNTIL_END.md  # Match persistence documentation
│
├── 📦 Configuration
│   └── requirements.txt         # Python dependencies
│
└── 📂 Data Directories
    └── odds_data/              # Default storage location (created automatically)
```

## 🚀 Quick Start

### 1. Installation
```bash
git clone <repository>
cd crawl_lol
pip install -r requirements.txt
```

### 2. Basic Usage
```bash
# List currently live matches
python3 live_odds_monitor.py --list

# Monitor all live games until they end
python3 live_odds_monitor.py --all-games

# Monitor specific game with data storage
python3 live_odds_monitor.py --game 1 --interval 15 --storage json

# Analyze stored data
python3 simple_analyze.py --list
python3 simple_analyze.py --file <data_file>
```

### 3. Advanced Usage
```bash
# Monitor with custom storage location
python3 live_odds_monitor.py --all-games --storage sqlite --storage-path ./my_data

# Monitor until specific match ends with CSV export
python3 live_odds_monitor.py --game 1 --storage csv --interval 10
```

## 🔧 Technical Architecture

### API Integration
- **esportsmatrix API**: Primary data source for live LoL matches
- **Robust Error Handling**: Request retries, JSON parsing, API status validation
- **Rate Limiting**: Configurable update intervals to respect API limits

### Data Processing Pipeline
1. **Live Match Detection**: Identifies currently active LoL matches
2. **Game Filtering**: Extracts specific games from match series
3. **Odds Extraction**: Parses team odds from nested API responses
4. **Change Detection**: Compares current vs previous odds for changes
5. **Data Storage**: Saves to chosen format (JSON/CSV/SQLite)

### Storage Architecture
- **JSON**: Rich nested structure preserving full context
- **CSV**: Flat table format for spreadsheet analysis
- **SQLite**: Relational database with indexes for complex queries

## 📊 Data Analysis Capabilities

### Real-time Analysis
- Live odds change detection and alerting
- Momentum shift identification
- Market reaction timing analysis

### Historical Analysis
- Odds movement patterns over time
- Value betting opportunity identification
- Team performance correlation analysis
- Market efficiency measurement

### Export & Integration
- Excel-compatible CSV exports
- JSON for web applications
- SQLite for data science workflows
- Programmatic access via Python API

## 🛠️ Development History

### Phase 1: Basic Monitoring (Initial)
- Created basic odds monitoring script
- Implemented API integration with esportsmatrix
- Added CLI interface for basic usage

### Phase 2: Enhanced Monitoring
- Fixed live match detection logic
- Added game-specific filtering capabilities
- Implemented odds change detection and logging

### Phase 3: Match Persistence
- Added "monitor until end" functionality
- Implemented match tracking across game breaks
- Enhanced status reporting during pauses

### Phase 4: Data Storage & Analysis
- Implemented multiple storage formats (JSON, CSV, SQLite)
- Created comprehensive analysis tools
- Added data export and visualization capabilities

## 🎮 Use Cases

### For Bettors
- **Live Betting**: Real-time odds monitoring for in-game betting
- **Value Detection**: Identify odds discrepancies and value bets
- **Pattern Recognition**: Learn from historical odds movements

### For Analysts
- **Market Research**: Study betting market efficiency
- **Data Collection**: Gather datasets for machine learning models
- **Performance Analysis**: Correlate odds with actual game outcomes

### For Developers
- **API Integration**: Use as foundation for betting applications
- **Data Pipeline**: Incorporate into larger data processing systems
- **Research Platform**: Base for esports analytics development

## 🔍 AI Agent Notes

### Key Implementation Details
1. **API Structure**: The esportsmatrix API uses nested JSON with `StatusCode`, `Sport`, `LG`, `ParentMatch`, and `Match` hierarchy
2. **Live Detection**: Matches are considered live when `HasLive=true` AND `LiveCnt > 0`
3. **Game Identification**: Games are identified by parsing "Game X" from the `GTName` field
4. **Odds Mapping**: Team codes (1,2) are mapped to actual team names from parent match data

### Common Pitfalls Avoided
- **GameStatus Confusion**: Don't rely only on `GameStatus=2`; use `LiveCnt` instead
- **Match Persistence**: Track specific match IDs to continue through game breaks
- **Data Loss**: Implement crash-safe storage with periodic saves
- **API Changes**: Built robust parsing to handle API structure variations

### Extension Points
- **Additional Sports**: Framework supports other esports (change `sport_id`)
- **More Analytics**: Analysis framework ready for ML model integration
- **Real-time Alerts**: Logging system ready for notification extensions
- **Web Interface**: Core classes ready for web application integration

## 🏁 Project Status & Handoff Notes

### ✅ Completed Features
- **Core Monitoring System**: Fully functional real-time odds monitoring with robust match detection
- **Data Storage**: Complete implementation of JSON, CSV, and SQLite storage with crash-safe operations
- **Analysis Tools**: Both basic (no dependencies) and advanced (pandas/matplotlib) analysis scripts
- **CLI Interface**: Comprehensive command-line interface with all major options
- **Documentation**: Extensive documentation for users, developers, and future AI agents
- **Project Organization**: Clean structure with legacy files moved to separate directory

### 🧪 Testing Status
- **Live Monitoring**: Tested and confirmed working with real matches
- **Data Storage**: All three storage formats tested and validated
- **Odds Detection**: Change detection and logging verified
- **Analysis Scripts**: Both analysis tools tested with sample data
- **CLI Options**: All command-line options tested and documented

### 📊 Data Quality
- **Storage Location**: `/odds_data/` contains example data files
- **Format Validation**: All storage formats produce valid, readable output
- **Data Integrity**: Crash-safe storage prevents data corruption
- **Analysis Ready**: Stored data works seamlessly with analysis tools

### 🔧 Future Enhancement Opportunities
1. **Machine Learning Integration**: Framework ready for predictive models
2. **Web Dashboard**: Core classes can be easily wrapped in web interface
3. **Real-time Alerts**: Logging system ready for notification extensions
4. **Multi-Sport Support**: Easy to extend to other esports
5. **Advanced Analytics**: More sophisticated statistical analysis tools

### 📋 For Future AI Agents
- **Entry Point**: Start with `README.md` for usage, then `PROJECT_OVERVIEW.md` for architecture
- **Core Logic**: Main monitoring logic is in `LoLOddsMonitor` class in `live_odds_monitor.py`
- **Extension Points**: Well-documented extension points for new features
- **Dependencies**: Minimal core dependencies, optional advanced dependencies clearly marked
- **Testing**: Use `example_usage.py` to understand programmatic usage patterns

**Status**: ✅ **COMPLETE AND READY FOR PRODUCTION USE**
