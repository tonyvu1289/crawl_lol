#!/usr/bin/env python3
"""
Example usage of the Live LoL Odds Monitor

This script demonstrates different ways to use the live odds monitor.
"""

from live_odds_monitor import LoLOddsMonitor


def example_monitor_game_1():
    """Example: Monitor only Game 1 odds"""
    print("=== Monitoring Game 1 Only ===")
    monitor = LoLOddsMonitor()
    
    # Monitor Game 1 for 5 iterations with 10-second intervals
    monitor.monitor_odds(target_game=1, interval=10, max_iterations=5)


def example_monitor_all_games():
    """Example: Monitor all live games"""
    print("=== Monitoring All Games ===")
    monitor = LoLOddsMonitor()
    
    # Monitor all games for 3 iterations with 15-second intervals
    monitor.monitor_odds(target_game=None, interval=15, max_iterations=3)


def example_list_live_games():
    """Example: List all currently live games"""
    print("=== Listing Live Games ===")
    monitor = LoLOddsMonitor()
    monitor.list_live_games()


def example_single_check():
    """Example: Single check of current odds"""
    print("=== Single Check Example ===")
    monitor = LoLOddsMonitor()
    
    # Get live matches
    live_matches = monitor.get_live_matches()
    
    if not live_matches:
        print("No live matches found")
        return
    
    print(f"Found {len(live_matches)} live matches")
    
    # Check odds for the first match
    first_match = live_matches[0]
    match_id = first_match.get("MId")
    
    if match_id:
        print(f"Getting details for match {match_id}")
        match_details = monitor.get_match_details(match_id)
        
        if match_details:
            # Extract odds for all games in this match
            game_odds = monitor.extract_game_odds(match_details)
            
            # Display formatted odds
            display = monitor.format_odds_display(game_odds)
            print(display)


if __name__ == "__main__":
    print("Live LoL Odds Monitor Examples")
    print("=" * 50)
    
    # Choose which example to run
    examples = {
        "1": ("List live games", example_list_live_games),
        "2": ("Single check", example_single_check),
        "3": ("Monitor Game 1", example_monitor_game_1),
        "4": ("Monitor all games", example_monitor_all_games),
    }
    
    print("\nAvailable examples:")
    for key, (description, _) in examples.items():
        print(f"{key}. {description}")
    
    choice = input("\nEnter example number (1-4): ").strip()
    
    if choice in examples:
        description, func = examples[choice]
        print(f"\nRunning: {description}")
        print("-" * 30)
        func()
    else:
        print("Invalid choice. Running single check example...")
        example_single_check()
