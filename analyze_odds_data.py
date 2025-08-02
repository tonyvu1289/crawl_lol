#!/usr/bin/env python3
"""
Data Analysis Script for Live LoL Odds

This script demonstrates how to analyze the stored odds data
for insights and patterns.
"""

import json
import csv
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import argparse


class OddsDataAnalyzer:
    def __init__(self, data_path="./odds_data"):
        self.data_path = Path(data_path)
        
    def load_json_data(self, filename):
        """Load data from JSON file"""
        file_path = self.data_path / filename
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return []
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_csv_data(self, filename):
        """Load data from CSV file"""
        file_path = self.data_path / filename
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return pd.DataFrame()
            
        return pd.read_csv(file_path)
    
    def load_sqlite_data(self, db_filename="live_odds.db", query=None):
        """Load data from SQLite database"""
        db_path = self.data_path / db_filename
        if not db_path.exists():
            print(f"Database not found: {db_path}")
            return pd.DataFrame()
        
        if query is None:
            query = "SELECT * FROM live_odds ORDER BY timestamp"
            
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def analyze_odds_changes(self, data_source):
        """Analyze odds changes over time"""
        print("=== Odds Change Analysis ===")
        
        if isinstance(data_source, str) and data_source.endswith('.json'):
            # JSON data analysis
            data = self.load_json_data(data_source)
            if not data:
                return
                
            # Extract odds changes
            odds_timeline = []
            for record in data:
                timestamp = record['timestamp']
                game_data = record['game_data']
                
                for team, odds in game_data.get('odds', {}).items():
                    odds_timeline.append({
                        'timestamp': timestamp,
                        'team': team,
                        'odds': odds,
                        'game_number': game_data.get('game_number', 0),
                        'match_id': game_data.get('match_id', 'unknown')
                    })
            
            df = pd.DataFrame(odds_timeline)
            
        elif isinstance(data_source, str) and data_source.endswith('.csv'):
            # CSV data analysis
            df = self.load_csv_data(data_source)
            if df.empty:
                return
                
        else:
            # SQLite data analysis
            df = self.load_sqlite_data()
            if df.empty:
                return
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Basic statistics
            print(f"Total records: {len(df)}")
            print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
            
            if 'odds' in df.columns:
                print(f"Odds range: {df['odds'].min():.3f} to {df['odds'].max():.3f}")
                print(f"Average odds: {df['odds'].mean():.3f}")
            
            # Unique matches and teams
            if 'match_id' in df.columns:
                print(f"Unique matches: {df['match_id'].nunique()}")
            if 'team' in df.columns:
                print(f"Unique teams: {df['team'].nunique()}")
                print("Teams:", df['team'].unique().tolist())
    
    def find_biggest_odds_swings(self, data_source, min_change=0.1):
        """Find the biggest odds swings"""
        print(f"\n=== Biggest Odds Swings (min change: {min_change}) ===")
        
        if data_source.endswith('.db'):
            query = """
            SELECT match_id, team1, team2, team1_odds, team2_odds, timestamp
            FROM live_odds 
            ORDER BY match_id, timestamp
            """
            df = self.load_sqlite_data(query=query)
        else:
            # For JSON/CSV, implement similar logic
            print("Odds swing analysis currently supports SQLite format")
            return
        
        if df.empty:
            return
            
        # Group by match and track odds changes
        swings = []
        for match_id in df['match_id'].unique():
            match_data = df[df['match_id'] == match_id].sort_values('timestamp')
            
            if len(match_data) < 2:
                continue
                
            # Track team1 odds changes
            team1_odds = match_data['team1_odds'].dropna()
            if len(team1_odds) >= 2:
                max_change = abs(team1_odds.max() - team1_odds.min())
                if max_change >= min_change:
                    swings.append({
                        'match_id': match_id,
                        'team': match_data.iloc[0]['team1'],
                        'min_odds': team1_odds.min(),
                        'max_odds': team1_odds.max(),
                        'change': max_change
                    })
            
            # Track team2 odds changes
            team2_odds = match_data['team2_odds'].dropna()
            if len(team2_odds) >= 2:
                max_change = abs(team2_odds.max() - team2_odds.min())
                if max_change >= min_change:
                    swings.append({
                        'match_id': match_id,
                        'team': match_data.iloc[0]['team2'],
                        'min_odds': team2_odds.min(),
                        'max_odds': team2_odds.max(),
                        'change': max_change
                    })
        
        # Sort by biggest changes
        swings.sort(key=lambda x: x['change'], reverse=True)
        
        print(f"Found {len(swings)} significant odds swings:")
        for swing in swings[:10]:  # Top 10
            print(f"  {swing['team']}: {swing['min_odds']:.3f} → {swing['max_odds']:.3f} "
                  f"(change: {swing['change']:.3f})")
    
    def generate_odds_timeline(self, data_source, output_file="odds_timeline.png"):
        """Generate a timeline chart of odds changes"""
        print(f"\n=== Generating Odds Timeline: {output_file} ===")
        
        try:
            import matplotlib.pyplot as plt
            
            if data_source.endswith('.db'):
                df = self.load_sqlite_data()
            elif data_source.endswith('.csv'):
                df = self.load_csv_data(data_source)
            else:
                print("Timeline generation requires CSV or SQLite data")
                return
            
            if df.empty:
                return
                
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create timeline plot
            plt.figure(figsize=(12, 8))
            
            if 'team1_odds' in df.columns and 'team2_odds' in df.columns:
                # Plot team odds
                for match_id in df['match_id'].unique():
                    match_data = df[df['match_id'] == match_id].sort_values('timestamp')
                    
                    if len(match_data) > 1:
                        team1_name = match_data.iloc[0]['team1']
                        team2_name = match_data.iloc[0]['team2']
                        
                        plt.plot(match_data['timestamp'], match_data['team1_odds'], 
                                label=f"{team1_name} (Match {match_id})", marker='o')
                        plt.plot(match_data['timestamp'], match_data['team2_odds'], 
                                label=f"{team2_name} (Match {match_id})", marker='s')
            
            plt.xlabel('Time')
            plt.ylabel('Odds')
            plt.title('Live Odds Timeline')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            output_path = self.data_path / output_file
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to: {output_path}")
            
        except ImportError:
            print("Matplotlib not available. Install with: pip install matplotlib")
    
    def list_available_data(self):
        """List all available data files"""
        print("=== Available Data Files ===")
        
        if not self.data_path.exists():
            print(f"Data directory not found: {self.data_path}")
            return
        
        json_files = list(self.data_path.glob("*.json"))
        csv_files = list(self.data_path.glob("*.csv"))
        db_files = list(self.data_path.glob("*.db"))
        
        print(f"JSON files ({len(json_files)}):")
        for f in json_files:
            print(f"  {f.name}")
        
        print(f"CSV files ({len(csv_files)}):")
        for f in csv_files:
            print(f"  {f.name}")
        
        print(f"SQLite databases ({len(db_files)}):")
        for f in db_files:
            print(f"  {f.name}")


def main():
    parser = argparse.ArgumentParser(description="Analyze stored odds data")
    parser.add_argument("--data-path", default="./odds_data", 
                       help="Path to data directory")
    parser.add_argument("--file", help="Specific file to analyze")
    parser.add_argument("--list", action="store_true", 
                       help="List available data files")
    parser.add_argument("--swings", action="store_true", 
                       help="Analyze odds swings")
    parser.add_argument("--timeline", action="store_true", 
                       help="Generate timeline chart")
    
    args = parser.parse_args()
    
    analyzer = OddsDataAnalyzer(args.data_path)
    
    if args.list:
        analyzer.list_available_data()
        return
    
    if not args.file:
        # Auto-detect latest file
        analyzer.list_available_data()
        print("\nPlease specify a file with --file <filename>")
        return
    
    # Run analysis
    analyzer.analyze_odds_changes(args.file)
    
    if args.swings:
        analyzer.find_biggest_odds_swings(args.file)
    
    if args.timeline:
        analyzer.generate_odds_timeline(args.file)


if __name__ == "__main__":
    main()
