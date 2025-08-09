#!/usr/bin/env python3
"""
Live LoL Odds Monitor

This script monitors live odds for League of Legends matches using the
esportsmatrix API. It can track specific games (Game 1, Game 2, Game 3, etc.)
and monitor odds changes in real-time.

Usage:
    python live_odds_monitor.py --game 1 --interval 30
    python live_odds_monitor.py --all-games --interval 10
"""

import requests
import json
import time
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import logging
import csv
import os
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_odds_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LoLOddsMonitor:
    """
    League of Legends Live Odds Monitor
    
    A comprehensive monitoring system for tracking live LoL match betting odds
    using the esportsmatrix API. Supports real-time odds tracking, change detection,
    and multiple data storage formats.
    
    Features:
    - Real-time odds monitoring with configurable intervals
    - Game-specific filtering (Game 1, Game 2, etc.)
    - Match persistence through game breaks
    - Odds change detection and logging
    - Multiple storage formats (JSON, CSV, SQLite)
    - Crash-safe data storage with periodic saves
    
    Args:
        storage_format (str): Data storage format ("json", "csv", or "sqlite")
        storage_path (str): Directory path for storing data files
        
    Example:
        >>> monitor = LoLOddsMonitor(storage_format="json", storage_path="./data")
        >>> monitor.monitor_odds(target_game=1, interval=30)
    """
    def __init__(self, storage_format="json", storage_path="./odds_data"):
        self.base_url = "https://w2e-api.esportsmatrix.io/api/esbull/api"
        self.headers = {'Content-Type': 'application/json'}
        self.game_cat = 1  # League of Legends
        self.sport_id = 45  # LoL Sport ID
        self.timezone = "07:00:00"
        self.language = "eng"
        self.betting_channel = 1
        
        # Data storage configuration
        self.storage_format = storage_format.lower()
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize storage
        self._init_storage()
        
    def _init_storage(self):
        """Initialize storage system based on format"""
        if self.storage_format == "csv":
            self.csv_file = self.storage_path / f"live_odds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self._init_csv()
        elif self.storage_format == "sqlite":
            self.db_file = self.storage_path / "live_odds.db"
            self._init_database()
        elif self.storage_format == "json":
            self.json_file = self.storage_path / f"live_odds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.odds_history = []
            
    def _init_csv(self):
        """Initialize CSV file with headers"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'match_id', 'match_name', 'game_number', 
                'team1', 'team2', 'team1_odds', 'team2_odds', 'status',
                'league', 'series_score'
            ])
            
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS live_odds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                match_id INTEGER NOT NULL,
                match_name TEXT,
                game_number INTEGER,
                team1 TEXT,
                team2 TEXT,
                team1_odds REAL,
                team2_odds REAL,
                status TEXT,
                league TEXT,
                series_score TEXT,
                raw_data TEXT
            )
        ''')
        
        # Create index for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON live_odds(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_id ON live_odds(match_id)')
        
        conn.commit()
        conn.close()
        
    def get_current_timestamp(self) -> int:
        """Get current timestamp for API requests"""
        return int(time.time())
    
    def get_live_matches(self) -> List[Dict]:
        """Fetch all live LoL matches"""
        url = f"{self.base_url}/GetIndexMatchV2"
        
        payload = {
            "GameCat": self.game_cat,
            "SportBLFilter": [
                {
                    "SportId": self.sport_id,
                    "BaseLGIDs": [-99]
                }
            ],
            "MatchCnt": 50,
            "SortType": 1,
            "HasLive": True,  # Only get live matches
            "Token": None,
            "Language": self.language,
            "BettingChannel": self.betting_channel,
            "MatchFilter": -99,
            "Timezone": self.timezone,
            "Event": "",
            "TriggeredBy": 2,
            "TimeStamp": self.get_current_timestamp()
        }
        
        try:
            response = requests.post(
                url, headers=self.headers, data=json.dumps(payload)
            )
            response.raise_for_status()
            data = response.json()
            
            # Check if API call was successful (StatusCode 0 means success)
            if data.get("StatusCode") == 0:
                # Extract live matches from the nested structure
                live_matches = []
                sports = data.get("Sport", [])
                
                for sport in sports:
                    leagues = sport.get("LG", [])
                    for league in leagues:
                        # Extract league name from league context
                        league_name = (
                            league.get("BaseLGName") or
                            league.get("LGName") or
                            league.get("LName") or
                            league.get("Name") or ""
                        )
                        parent_matches = league.get("ParentMatch", [])
                        for parent_match in parent_matches:
                            # Only include matches that are actually live
                            # Check for HasLive and LiveCnt > 0 (has live
                            # games)
                            if (parent_match.get("HasLive") and
                                    parent_match.get("LiveCnt", 0) > 0):
                                # Attach league name so downstream consumers
                                # have access
                                pm = parent_match.copy()
                                pm['league_name'] = league_name
                                live_matches.append(pm)
                
                logger.info(f"Found {len(live_matches)} live matches")
                return live_matches
            else:
                logger.error(
                    f"API error: {data.get('StatusDesc', 'Unknown error')}"
                )
                return []
                
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return []
    
    def get_match_details(self, match_id: int) -> Optional[Dict]:
        """Get detailed odds for a specific match"""
        url = f"{self.base_url}/GetMatchDetailsByParentV2"
        
        payload = {
            "GameCat": self.game_cat,
            "PMatchNo": match_id,
            "Token": None,
            "Language": self.language,
            "BettingChannel": self.betting_channel,
            "Grp": -99,
            "GTGrpCnt": 20,
            "Timezone": self.timezone,
            "TimeStamp": self.get_current_timestamp()
        }
        
        try:
            response = requests.post(
                url, headers=self.headers, data=json.dumps(payload)
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("IsSuccess"):
                return data
            else:
                logger.error(
                    f"API error for match {match_id}: "
                    f"{data.get('Message', 'Unknown error')}"
                )
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request failed for match {match_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for match {match_id}: {e}")
            return None
    
    def extract_game_odds(
        self, match_details: Dict, target_game: Optional[int] = None
    ) -> List[Dict]:
        """Extract odds information for specific games from match details"""
        game_odds = []
        
        try:
            # For live matches, the structure is different
            # Check if this is a parent match with Match array
            if "Match" in match_details:
                matches = match_details.get("Match", [])
                parent_match = match_details
            else:
                # This is from get_match_details API call
                match_data = match_details.get("MatchData", [])
                if not match_data:
                    return game_odds
                matches = match_data
                parent_match = None
            
            for match in matches:
                game_info = {
                    "match_id": match.get("MatchNo") or match.get("MId"),
                    "match_name": match.get("GTName", ""),
                    "team1": "",
                    "team2": "",
                    "status": match.get("Status", ""),
                    "game_number": None,
                    "odds": {}
                }
                
                # Get team names from parent match if available
                if parent_match:
                    game_info["team1"] = parent_match.get("PHTName", "Team A")
                    game_info["team2"] = parent_match.get("PATName", "Team B")
                    # Attach league name so we can display it too
                    game_info["league"] = parent_match.get("league_name", "")
                else:
                    game_info["team1"] = match.get("TName1", "Team A")
                    game_info["team2"] = match.get("TName2", "Team B")
                
                # Extract game number from match name
                match_name = match.get("GTName", "") or match.get("MName", "")
                if "Game" in match_name:
                    try:
                        parts = match_name.split("Game")[1].strip().split()
                        game_num = int(parts[0])
                        game_info["game_number"] = game_num
                    except (IndexError, ValueError):
                        pass
                
                # If target_game is specified, only include that game
                if target_game and game_info["game_number"] != target_game:
                    continue
                
                # Extract odds from the Odds array
                odds_array = match.get("Odds", [])
                for odds_group in odds_array:
                    selections = odds_group.get("SEL", [])
                    for selection in selections:
                        team_code = selection.get("SCode")
                        team_name = selection.get("SName", "")
                        odds_value = selection.get("Odds", 0)
                        
                        # Map team codes to actual team names
                        if team_code == 1:
                            team_display = game_info["team1"]
                        elif team_code == 2:
                            team_display = game_info["team2"]
                        else:
                            team_display = team_name
                        
                        if team_display and odds_value:
                            game_info["odds"][team_display] = odds_value
                
                if game_info["game_number"] or game_info["odds"]:
                    game_odds.append(game_info)
        
        except Exception as e:
            logger.error(f"Error extracting game odds: {e}")
        
        return game_odds
    
    def format_odds_display(self, game_odds: List[Dict]) -> str:
        """Format odds information for display"""
        if not game_odds:
            return "No live games found"
        
        output = []
        output.append("=" * 80)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output.append(f"LIVE LOL ODDS - {timestamp}")
        output.append("=" * 80)
        
        for game in game_odds:
            game_num = game.get("game_number", "Unknown")
            team1 = game.get("team1", "Team 1")
            team2 = game.get("team2", "Team 2")
            status = game.get("status", "Unknown")
            league = game.get("league", "Unknown League")
            
            output.append(f"\nGame {game_num}: {team1} vs {team2}")
            output.append(f"Status: {status}")
            output.append(f"League: {league}")
            
            if game.get("odds"):
                output.append("Odds:")
                for team, odds in game["odds"].items():
                    output.append(f"  {team}: {odds}")
            else:
                output.append("No odds available")
            
            output.append("-" * 60)
        
        return "\n".join(output)
    
    def monitor_odds(
        self, 
        target_game: Optional[int] = None, 
        interval: int = 30, 
        max_iterations: Optional[int] = None
    ):
        """Monitor live odds for specified game(s) until matches end"""
        game_desc = target_game if target_game else 'ALL'
        logger.info(f"Starting odds monitoring for Game {game_desc}")
        logger.info(f"Update interval: {interval} seconds")
        
        iteration = 0
        previous_odds = {}
        tracked_matches = set()  # Track match IDs we're monitoring
        initial_scan = True
        
        try:
            while True:
                if max_iterations and iteration >= max_iterations:
                    logger.info(
                        f"Reached maximum iterations ({max_iterations})"
                    )
                    break
                
                # Get live matches
                live_matches = self.get_live_matches()
                
                # On first iteration, record all live matches to track
                if initial_scan:
                    if live_matches:
                        tracked_matches = {match.get("PMatchNo") for match in live_matches if match.get("PMatchNo")}
                        logger.info(f"Tracking {len(tracked_matches)} matches: {tracked_matches}")
                        initial_scan = False
                    else:
                        logger.warning("No live matches found to start monitoring")
                        time.sleep(interval)
                        iteration += 1
                        continue
                
                # Filter live matches to only those we're tracking
                current_live_matches = [
                    match for match in live_matches 
                    if match.get("PMatchNo") in tracked_matches
                ]
                
                # Check if all tracked matches have ended
                if not current_live_matches and not initial_scan:
                    logger.info("All tracked matches have ended. Monitoring complete.")
                    break
                
                all_game_odds = []
                
                # Process each tracked live match
                for match in current_live_matches:
                    match_id = match.get("PMatchNo")
                    if not match_id:
                        continue
                    
                    # Extract game odds directly from live match data
                    game_odds = self.extract_game_odds(match, target_game)
                    all_game_odds.extend(game_odds)
                    
                    # Store odds data if we have any
                    if game_odds:
                        # Pass along the match which already contains league_name
                        self.store_odds_data(game_odds, match)
                
                # Display current odds if we have any
                if all_game_odds:
                    odds_display = self.format_odds_display(all_game_odds)
                    print("\n" + odds_display)
                else:
                    # Show status of tracked matches even if no live games
                    print(f"\n{'='*60}")
                    print(f"Monitoring Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"{'='*60}")
                    
                    if current_live_matches:
                        print("Tracked matches still live but no games in progress:")
                        for match in current_live_matches:
                            team1 = match.get("PHTName", "Team 1")
                            team2 = match.get("PATName", "Team 2")
                            score1 = match.get("PHTScore", 0)
                            score2 = match.get("PATScore", 0)
                            league = match.get('league_name', 'Unknown League')
                            print(f"  {team1} vs {team2} ({score1}-{score2}) | League: {league}")
                    else:
                        print("Waiting for tracked matches to resume or end...")
                    print("-" * 60)
                
                # Check for odds changes
                current_odds = {}
                for game in all_game_odds:
                    match_id = game.get('match_id', 'unknown')
                    game_num = game.get('game_number', 'unknown')
                    game_key = f"{match_id}_{game_num}"
                    current_odds[game_key] = game.get('odds', {})
                
                if previous_odds:
                    for game_key, odds in current_odds.items():
                        if game_key in previous_odds:
                            prev_odds = previous_odds[game_key]
                            for team, current_odd in odds.items():
                                if team in prev_odds:
                                    if prev_odds[team] != current_odd:
                                        logger.info(
                                            f"ODDS CHANGE - {game_key} - "
                                            f"{team}: {prev_odds[team]} -> "
                                            f"{current_odd}"
                                        )
                
                previous_odds = current_odds
                
                # Wait before next check
                time.sleep(interval)
                iteration += 1
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            self.finalize_storage()
        except Exception as e:
            logger.error(f"Unexpected error during monitoring: {e}")
            self.finalize_storage()
        finally:
            # Ensure data is saved even on normal completion
            if hasattr(self, 'storage_format'):
                self.finalize_storage()
    
    def list_live_games(self):
        """List all currently live games"""
        live_matches = self.get_live_matches()
        
        if not live_matches:
            print("No live matches found")
            return
        
        print("Currently Live LoL Matches:")
        print("=" * 60)
        
        for match in live_matches:
            match_id = match.get("PMatchNo")
            team1 = match.get("PHTName", "Team 1")
            team2 = match.get("PATName", "Team 2")
            score1 = match.get("PHTScore", 0)
            score2 = match.get("PATScore", 0)
            league = match.get('league_name', 'Unknown League')
            
            print(f"Match ID: {match_id}")
            print(f"Match: {team1} vs {team2}")
            print(f"League: {league}")
            print(f"Score: {score1} - {score2}")
            
            # Show live games within this match
            games = match.get("Match", [])
            for game in games:
                if game.get("IsLive"):
                    game_name = game.get("GTName", "Unknown Game")
                    print(f"  Live Game: {game_name}")
            
            print("-" * 40)
    
    def store_odds_data(self, game_odds: List[Dict], parent_match: Dict = None):
        """Store odds data in the configured format"""
        if not game_odds:
            return
            
        timestamp = datetime.now().isoformat()
        
        for game in game_odds:
            # Extract data
            match_id = game.get('match_id', 'unknown')
            match_name = game.get('match_name', '')
            game_number = game.get('game_number', 0)
            team1 = game.get('team1', '')
            team2 = game.get('team2', '')
            status = game.get('status', '')
            odds = game.get('odds', {})
            
            # Get team odds
            team1_odds = odds.get(team1, 0) if team1 in odds else 0
            team2_odds = odds.get(team2, 0) if team2 in odds else 0
            
            # Get league and series info from parent match
            league = ''
            series_score = ''
            if parent_match:
                league = parent_match.get('league_name', '')
                score1 = parent_match.get('PHTScore', 0)
                score2 = parent_match.get('PATScore', 0)
                series_score = f"{score1}-{score2}"
            
            # Store based on format
            if self.storage_format == "csv":
                self._store_csv(timestamp, match_id, match_name, game_number,
                              team1, team2, team1_odds, team2_odds, status,
                              league, series_score)
            elif self.storage_format == "sqlite":
                self._store_database(timestamp, match_id, match_name, game_number,
                                   team1, team2, team1_odds, team2_odds, status,
                                   league, series_score, json.dumps(game))
            elif self.storage_format == "json":
                self._store_json(timestamp, game, parent_match)
                
    def _store_csv(self, timestamp, match_id, match_name, game_number,
                   team1, team2, team1_odds, team2_odds, status,
                   league, series_score):
        """Store data in CSV format"""
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, match_id, match_name, game_number,
                team1, team2, team1_odds, team2_odds, status,
                league, series_score
            ])
            
    def _store_database(self, timestamp, match_id, match_name, game_number,
                       team1, team2, team1_odds, team2_odds, status,
                       league, series_score, raw_data):
        """Store data in SQLite database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO live_odds 
            (timestamp, match_id, match_name, game_number, team1, team2,
             team1_odds, team2_odds, status, league, series_score, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, match_id, match_name, game_number, team1, team2,
              team1_odds, team2_odds, status, league, series_score, raw_data))
        
        conn.commit()
        conn.close()
        
    def _store_json(self, timestamp, game_data, parent_match):
        """Store data in JSON format"""
        record = {
            'timestamp': timestamp,
            'game_data': game_data,
            'parent_match_info': {
                'league': parent_match.get('league_name', '') if parent_match else '',
                'series_score': f"{parent_match.get('PHTScore', 0)}-{parent_match.get('PATScore', 0)}" if parent_match else '',
                'match_type': parent_match.get('MatchType', '') if parent_match else ''
            } if parent_match else {}
        }
        
        self.odds_history.append(record)
        
        # Save to file periodically (every 10 records) and at the end
        if len(self.odds_history) % 10 == 0:
            self._save_json_file()
            
    def _save_json_file(self):
        """Save JSON data to file"""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.odds_history, f, indent=2, ensure_ascii=False)
            
    def get_stored_data_summary(self):
        """Get summary of stored data"""
        if self.storage_format == "csv" and self.csv_file.exists():
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                return f"CSV: {len(rows) - 1} records stored in {self.csv_file}"
                
        elif self.storage_format == "sqlite" and self.db_file.exists():
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM live_odds")
            count = cursor.fetchone()[0]
            conn.close()
            return f"SQLite: {count} records stored in {self.db_file}"
            
        elif self.storage_format == "json":
            return f"JSON: {len(self.odds_history)} records (will be saved to {self.json_file})"
            
        return "No data stored yet"
    
    def _get_league_name(self, match):
        """Extract league name from match data structure"""
        # Prefer value attached during get_live_matches; fall back to common keys
        return (
            match.get('league_name') or
            match.get('BaseLGName') or
            match.get('LGName') or
            match.get('LName') or
            "Unknown League"
        )
    
    def finalize_storage(self):
        """Finalize storage and save any pending data"""
        if self.storage_format == "json":
            self._save_json_file()
            logger.info(f"Final data saved to {self.json_file}")
        
        # Show storage summary
        summary = self.get_stored_data_summary()
        logger.info(f"Data storage complete: {summary}")
        print(f"\nData Storage Summary: {summary}")


def main():
    parser = argparse.ArgumentParser(description="Monitor live LoL odds")
    parser.add_argument(
        "--game",
        type=int,
        help="Specific game number to monitor (1, 2, 3, etc.)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3,
        help="Update interval in seconds (default: 3)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        help="Maximum number of checks (default: unlimited)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List current live games and exit"
    )
    parser.add_argument(
        "--all-games",
        action="store_true",
        help="Monitor all games (default behavior)"
    )
    parser.add_argument(
        "--storage",
        choices=["json", "csv", "sqlite"],
        default="sqlite",
        help="Data storage format (default: json)"
    )
    parser.add_argument(
        "--storage-path",
        default="./odds_data",
        help="Path to store data files (default: ./odds_data)"
    )
    
    args = parser.parse_args()
    
    monitor = LoLOddsMonitor(
        storage_format=args.storage,
        storage_path=args.storage_path
    )
    
    if args.list:
        monitor.list_live_games()
        return
    
    target_game = args.game if not args.all_games else None
    
    monitor.monitor_odds(
        target_game=target_game,
        interval=args.interval,
        max_iterations=args.max_iterations
    )


if __name__ == "__main__":
    main()
