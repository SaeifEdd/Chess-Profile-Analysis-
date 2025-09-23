import os
import pandas as pd
from io import StringIO
import datetime
import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#---------------------------
# CONFIG
#---------------------------
load_dotenv()
USERNAME = os.getenv("CUSERNAME")
PASSWORD = os.getenv("CPASSWORD")

LOGIN_URL = "https://www.chess.com/login_and_go?returnUrl=https://www.chess.com/"
now = datetime.datetime.now()

GAMES_URL = (
    f"https://www.chess.com/games/archive?gameOwner=other_game&username={USERNAME}"
    f"&gameType=live&gameResult=&opponent=&opening=&color=&gameTourTeam=&"
    f"timeSort=desc&rated=rated&startDate%5Bdate%5D=08%2F01%2F2013&endDate%5Bdate%5D="
    f"{str(now.month)}%2F{str(now.day)}%2F{str(now.year)}"
    f"&ratingFrom=&ratingTo=&page="
)

CSV_PATH = "data/games.csv"

def get_driver():
    """
    setup and configure chromedriver
    :return: a driver
    """
    options = webdriver.ChromeOptions()
    options.binary_location = "/snap/bin/chromium"
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    return webdriver.Chrome(service=Service("./chromedriver"), options=options)


def login(driver):
    """
    login to chess.com using credentials from .env file
    :param driver:
    :return:
    """
    driver.get(LOGIN_URL)
    username_field = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "login-username"))
    )
    username_field.send_keys(USERNAME)
    password_field = driver.find_element(By.ID, "login-password")
    password_field.send_keys(PASSWORD)
    login_button = driver.find_element(By.ID, "login")
    login_button.click()
    # Wait for login to complete
    time.sleep(20)



def scrape_games(driver, nb_pages=10):
    """
    scrape games from chess.com profile archive
    :param driver:
    :return: games data in pandas dataframe
    """
    tables = []
    for page_number in range(nb_pages):
        driver.get(GAMES_URL + str(page_number + 1))
        time.sleep(10)
        tables.append(
            pd.read_html(
                StringIO(str(driver.page_source)),
                attrs={'class': 'table-component table-hover archive-games-table'}
            )[0]
        )

    return pd.concat(tables)

def save_games(games):
    """
    save dataframe into a csv file
    :param games:
    :return:
    """
    games.insert(0, 'GameId', range(len(games)))
    csv_path = "data/games.csv"
    games.to_csv(csv_path, index=False)
    print(f"saved {len(games)} games into {CSV_PATH}")

def main():
    driver = get_driver()
    login(driver)
    games = scrape_games(driver, 20)
    save_games(games)
    driver.quit()

if __name__ == "__main__":
    main()
