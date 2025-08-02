#!/usr/bin/env python3
"""
Simple Data Analysis Script for Live LoL Odds
(No external dependencies required)
"""

import json
import csv
import sqlite3
from pathlib import Path
from datetime import datetime
import argparse


class SimpleOddsAnalyzer:
    def __init__(self, data_path="./odds_data"):
        self.data_path = Path(data_path)
        
    def list_files(self):
        """List all available data files"""
        print("=== Available Data Files ===")
        
        if not self.data_path.exists():
            print(f"Data directory not found: {self.data_path}")
            return
        
        json_files = list(self.data_path.glob("*.json"))
        csv_files = list(self.data_path.glob("*.csv"))
        db_files = list(self.data_path.glob("*.db"))
        
        print(f"\nJSON files ({len(json_files)}):")
        for f in json_files:
            size = f.stat().st_size
            print(f"  {f.name} ({size} bytes)")
        
        print(f"\nCSV files ({len(csv_files)}):")
        for f in csv_files:
            size = f.stat().st_size
            print(f"  {f.name} ({size} bytes)")
        
        print(f"\nSQLite databases ({len(db_files)}):")
        for f in db_files:
            size = f.stat().st_size
            print(f"  {f.name} ({size} bytes)")
    
    def analyze_json_file(self, filename):
        """Analyze JSON data file"""
        file_path = self.data_path / filename
        
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return
            
        print(f"\n=== Analyzing {filename} ===")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Total records: {len(data)}")
        
        if not data:
            print("No data found")
            return
        
        # Extract basic statistics
        teams = set()
        odds_values = []
        match_ids = set()
        game_numbers = set()
        
        first_time = None
        last_time = None
        
        for record in data:
            timestamp = record.get('timestamp', '')
            if timestamp:
                if not first_time:
                    first_time = timestamp
                last_time = timestamp
            
            game_data = record.get('game_data', {})
            odds = game_data.get('odds', {})
            
            match_ids.add(game_data.get('match_id', 'unknown'))
            game_numbers.add(game_data.get('game_number', 0))
            
            for team, odd_value in odds.items():
                teams.add(team)
                odds_values.append(odd_value)
        
        print(f"Time range: {first_time} to {last_time}")
        print(f"Unique matches: {len(match_ids)}")
        print(f"Game numbers: {sorted(game_numbers)}")
        print(f"Teams: {list(teams)}")
        
        if odds_values:
            print(f"Odds range: {min(odds_values):.3f} to {max(odds_values):.3f}")
            print(f"Average odds: {sum(odds_values)/len(odds_values):.3f}")
        
        # Show odds changes
        print("\nOdds Timeline:")
        for i, record in enumerate(data):
            timestamp = record.get('timestamp', '')[:19]  # Remove microseconds
            game_data = record.get('game_data', {})
            odds = game_data.get('odds', {})
            
            print(f"  {i+1}. {timestamp}")
            for team, odd_value in odds.items():
                print(f"     {team}: {odd_value}")
    
    def analyze_csv_file(self, filename):
        """Analyze CSV data file"""
        file_path = self.data_path / filename
        
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return
            
        print(f"\n=== Analyzing {filename} ===")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"Total records: {len(rows)}")
        
        if not rows:
            print("No data found")
            return
        
        # Extract statistics
        teams = set()
        odds_values = []
        match_ids = set()
        
        for row in rows:
            match_ids.add(row.get('match_id', ''))
            
            team1 = row.get('team1', '')
            team2 = row.get('team2', '')
            if team1:
                teams.add(team1)
            if team2:
                teams.add(team2)
            
            try:
                team1_odds = float(row.get('team1_odds', 0))
                team2_odds = float(row.get('team2_odds', 0))
                if team1_odds > 0:
                    odds_values.append(team1_odds)
                if team2_odds > 0:
                    odds_values.append(team2_odds)
            except ValueError:
                pass
        
        print(f"Unique matches: {len(match_ids)}")
        print(f"Teams: {list(teams)}")
        
        if odds_values:
            print(f"Odds range: {min(odds_values):.3f} to {max(odds_values):.3f}")
            print(f"Average odds: {sum(odds_values)/len(odds_values):.3f}")
        
        # Show timeline
        print("\nOdds Timeline:")
        for i, row in enumerate(rows):
            timestamp = row.get('timestamp', '')[:19]  # Remove microseconds
            team1 = row.get('team1', '')
            team2 = row.get('team2', '')
            team1_odds = row.get('team1_odds', '')
            team2_odds = row.get('team2_odds', '')
            
            print(f"  {i+1}. {timestamp}")
            print(f"     {team1}: {team1_odds}")
            print(f"     {team2}: {team2_odds}")
    
    def analyze_sqlite_db(self, filename="live_odds.db"):
        """Analyze SQLite database"""
        file_path = self.data_path / filename
        
        if not file_path.exists():
            print(f"Database not found: {file_path}")
            return
            
        print(f"\n=== Analyzing {filename} ===")
        
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        
        # Get total records
        cursor.execute("SELECT COUNT(*) FROM live_odds")
        total_records = cursor.fetchone()[0]
        print(f"Total records: {total_records}")
        
        if total_records == 0:
            print("No data found")
            conn.close()
            return
        
        # Get basic statistics
        cursor.execute("SELECT COUNT(DISTINCT match_id) FROM live_odds")
        unique_matches = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(team1_odds), MAX(team1_odds), AVG(team1_odds) FROM live_odds WHERE team1_odds > 0")
        team1_stats = cursor.fetchone()
        
        cursor.execute("SELECT MIN(team2_odds), MAX(team2_odds), AVG(team2_odds) FROM live_odds WHERE team2_odds > 0")
        team2_stats = cursor.fetchone()
        
        print(f"Unique matches: {unique_matches}")
        
        if team1_stats[0] and team2_stats[0]:
            min_odds = min(team1_stats[0], team2_stats[0])
            max_odds = max(team1_stats[1], team2_stats[1])
            avg_odds = (team1_stats[2] + team2_stats[2]) / 2
            print(f"Odds range: {min_odds:.3f} to {max_odds:.3f}")
            print(f"Average odds: {avg_odds:.3f}")
        
        # Show recent data
        cursor.execute("""
            SELECT timestamp, team1, team2, team1_odds, team2_odds 
            FROM live_odds 
            ORDER BY timestamp 
            LIMIT 10
        """)
        
        print("\nRecent Records:")
        for i, row in enumerate(cursor.fetchall()):
            timestamp, team1, team2, team1_odds, team2_odds = row
            print(f"  {i+1}. {timestamp[:19]}")
            print(f"     {team1}: {team1_odds}")
            print(f"     {team2}: {team2_odds}")
        
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Simple odds data analyzer")
    parser.add_argument("--data-path", default="./odds_data", 
                       help="Path to data directory")
    parser.add_argument("--file", help="Specific file to analyze")
    parser.add_argument("--list", action="store_true", 
                       help="List available data files")
    
    args = parser.parse_args()
    
    analyzer = SimpleOddsAnalyzer(args.data_path)
    
    if args.list:
        analyzer.list_files()
        return
    
    if not args.file:
        analyzer.list_files()
        print("\nUse --file <filename> to analyze a specific file")
        print("Examples:")
        print("  python3 simple_analyze.py --file live_odds_20250803_001324.json")
        print("  python3 simple_analyze.py --file live_odds_20250803_001512.csv")
        print("  python3 simple_analyze.py --file live_odds.db")
        return
    
    # Analyze the specified file
    if args.file.endswith('.json'):
        analyzer.analyze_json_file(args.file)
    elif args.file.endswith('.csv'):
        analyzer.analyze_csv_file(args.file)
    elif args.file.endswith('.db'):
        analyzer.analyze_sqlite_db(args.file)
    else:
        print(f"Unsupported file format: {args.file}")


if __name__ == "__main__":
    main()
