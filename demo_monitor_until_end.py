#!/usr/bin/env python3
"""
Demonstration of monitoring live matches until they end
"""

from live_odds_monitor import LoLOddsMonitor
import time

def demo_monitor_until_end():
    print("=== Live Match Monitoring Until End Demo ===\n")
    
    monitor = LoLOddsMonitor()
    
    # First, show what matches are currently live
    print("Step 1: Checking for live matches...")
    live_matches = monitor.get_live_matches()
    
    if not live_matches:
        print("No live matches found. Start this demo when matches are live.")
        return
    
    print(f"Found {len(live_matches)} live matches:")
    for match in live_matches:
        match_id = match.get("PMatchNo")
        team1 = match.get("PHTName", "Team 1")
        team2 = match.get("PATName", "Team 2")
        score1 = match.get("PHTScore", 0)
        score2 = match.get("PATScore", 0)
        live_count = match.get("LiveCnt", 0)
        
        print(f"  Match {match_id}: {team1} vs {team2} ({score1}-{score2})")
        print(f"    Live games: {live_count}")
    
    print("\nStep 2: Starting monitoring until matches end...")
    print("The script will now:")
    print("1. Track these specific matches")
    print("2. Continue monitoring even if games pause between rounds")
    print("3. Stop only when ALL tracked matches have completely ended")
    print("4. Show live odds when games are active")
    print("5. Show status updates when games are between rounds")
    
    print("\nPress Ctrl+C to stop monitoring early, or let it run until matches end.\n")
    
    # Start monitoring (this will run until matches end)
    try:
        monitor.monitor_odds(interval=15)  # Check every 15 seconds
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

if __name__ == "__main__":
    demo_monitor_until_end()
