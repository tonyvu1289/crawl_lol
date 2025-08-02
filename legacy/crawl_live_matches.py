# Crawl all live match links using the same navigation as test_test.py, but loop through matches and get their links
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome WebDriver
options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument('--window-size=1920,800')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)


def navigate_to_match_list(driver, wait):
    driver.set_window_size(1920, 800)
    driver.get("https://esportsbet.io/esportsbull//esportsbull/")
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".lg_itmHdr > .lg_itmInfo"))).click()
    time.sleep(1)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".lg_itmHdr img"))).click()
    time.sleep(1)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".match_itm:nth-child(2) > div:nth-child(1)"))).click()
    time.sleep(2)

def crawl_and_save_match_links(save_path="crawled_match_links.txt"):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--window-size=1920,800')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    try:
        navigate_to_match_list(driver, wait)
        matches = driver.find_elements(By.CSS_SELECTOR, ".matchRowWrp .leagueName")
        num_matches = len(matches)
        match_links = []

        for i in range(1, num_matches + 1):
            try:
                navigate_to_match_list(driver, wait)
                selector = f".matchRowWrp:nth-child({i}) .leagueName"
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                elem.click()
                time.sleep(1)
                match_url = driver.current_url
                match_links.append(match_url)
            except Exception:
                continue

        # Save unique new match links to file
        try:
            with open(save_path, "r") as f:
                existing_links = set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            existing_links = set()

        new_links = [link for link in match_links if link not in existing_links]

        if new_links:
            with open(save_path, "a") as f:
                for link in new_links:
                    f.write(link + "\n")

        print("Found live match links:")
        for link in match_links:
            print(link)
        print(f"New links added: {len(new_links)}. Total in file: {len(existing_links) + len(new_links)}")
        return match_links, new_links
    finally:
        driver.quit()

if __name__ == "__main__":
    crawl_and_save_match_links()
