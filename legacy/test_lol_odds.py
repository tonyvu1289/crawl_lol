
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

# Set up headless Chrome
def get_lol_odds_info(url):

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        driver.implicitly_wait(5)
        body_text = driver.find_element("tag name", "body").text

        # Check if match has ended
        ended = False
        if "Sorry, there is no market for this match" in body_text:
            ended = True

        # Extract tournament
        tournament = re.search(r"(LCP 2025 Season Finals)", body_text)
        tournament = tournament.group(1) if tournament else "Unknown"

        # Extract current game
        current_game_match = re.search(r"Game (\d+)", body_text)
        current_game = (
            f"Game {current_game_match.group(1)}" if current_game_match else "Unknown"
        )

        # Extract odds for the current game (flexible team names)
        odds_pattern = (
            r"Game (\d+) Win \(Live Odds\)\s*([A-Z0-9 .\-]+)\s*([\d.]+)\s*([A-Z0-9 .\-]+)\s*([\d.]+)"
        )
        odds_match = re.search(odds_pattern, body_text)
        if odds_match:
            team1 = odds_match.group(2).strip()
            team1_odds = odds_match.group(3)
            team2 = odds_match.group(4).strip()
            team2_odds = odds_match.group(5)
        else:
            team1 = team2 = team1_odds = team2_odds = "Unknown"

        print("Tournament:", tournament)
        print("Current game:", current_game)
        print(
            f"{current_game} odds - {team1}: {team1_odds}, {team2}: {team2_odds}"
        )
        if ended:
            print("Match has ended.")
    except Exception as e:
        print("An error occurred in get_lol_odds_info:", e)
    finally:
        driver.quit()


def main(url):
    last_game = None
    last_team1 = None
    last_team2 = None
    last_team1_odds = None
    last_team2_odds = None
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        driver.implicitly_wait(5)
        # Extract tournament name once after page load
        try:
            tournament_elem = driver.find_element(
                "xpath",
                "//*[contains(text(),'Split') or contains(text(),'Season') or contains(text(),'Cup') or contains(text(),'Finals') or contains(text(),'Championship') or contains(text(),'Masters') or contains(text(),'Series') or contains(text(),'League') or contains(text(),'LPL') or contains(text(),'LCK') or contains(text(),'LCS') or contains(text(),'Worlds')][1]"
            )
            tournament = tournament_elem.text.strip()
        except Exception:
            tournament = "Unknown"
        print(f"Tournament: {tournament}")
        while True:
            try:
                body_text = driver.find_element("tag name", "body").text

                # Check if match has ended
                if "Sorry, there is no market for this match" in body_text:
                    print("Match has ended.")
                    break

                # Extract current game
                current_game_match = re.search(r"Game (\d+)", body_text)
                current_game = (
                    f"Game {current_game_match.group(1)}" if current_game_match else "Unknown"
                )

                # Extract odds for the current game (flexible team names)
                odds_pattern = (
                    r"Game (\d+) Win \(Live Odds\)\s*([A-Z0-9 .\-]+)\s*([\d.]+)\s*([A-Z0-9 .\-]+)\s*([\d.]+)"
                )
                odds_match = re.search(odds_pattern, body_text)
                if odds_match:
                    team1 = odds_match.group(2).strip()
                    team1_odds = odds_match.group(3)
                    team2 = odds_match.group(4).strip()
                    team2_odds = odds_match.group(5)
                else:
                    team1 = team2 = team1_odds = team2_odds = "Unknown"

                changed = False
                from datetime import datetime
                if current_game != last_game:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Current game changed: {current_game}")
                    last_game = current_game
                    changed = True
                if (
                    team1 != last_team1
                    or team2 != last_team2
                    or team1_odds != last_team1_odds
                    or team2_odds != last_team2_odds
                ):
                    print(
                        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {current_game} odds changed - {team1}: {team1_odds}, {team2}: {team2_odds}"
                    )
                    last_team1 = team1
                    last_team2 = team2
                    last_team1_odds = team1_odds
                    last_team2_odds = team2_odds
                    changed = True
                if not changed:
                    # print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No change.")
                    pass
                sleep(5)
            except Exception as e:
                print("An error occurred:", e)
                break
    finally:
        driver.quit()

if __name__ == "__main__":
    url = (
        "https://esportsbet.io/esportsbull/OddsPage/35215574/45/LOLBetting-GENERATION-GAMING-KT-ROLSTER"
    )
    main(url)