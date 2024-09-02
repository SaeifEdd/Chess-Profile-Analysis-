import numpy as np
import pandas as pd
from io import StringIO
import datetime
import time
import hashlib
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
now = datetime.datetime.now()

USERNAME = os.getenv("CUSERNAME")
PASSWORD = os.getenv("CPASSWORD")

GAMES_URL = "https://www.chess.com/games/archive?gameOwner=other_game&username=" + USERNAME + \
"&gameType=live&gameResult=&opponent=&opening=&color=&gameTourTeam=&" + \
"timeSort=desc&rated=rated&startDate%5Bdate%5D=08%2F01%2F2013&endDate%5Bdate%5D=" +  \
str(now.month) + "%2F" + str(now.day) + "%2F" + str(now.year) + \
"&ratingFrom=&ratingTo=&page="
LOGIN_URL = "https://www.chess.com/login"

service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)
driver.get(LOGIN_URL)

#print(driver.page_source)
# Wait until the username field is visible and interactable
username_field = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Username or Email']"))
)
username_field.send_keys(USERNAME)

# Wait until the password field is visible and interactable
password_field = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Password']"))
)
password_field.send_keys(PASSWORD)

# Wait until the login button is clickable
login_button = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.ID, "login"))
)
login_button.click()

time.sleep(15)

# print("login ok")

tables = []
game_links = []

for page_number in range(8):
    driver.get(GAMES_URL + str(page_number + 1))
    time.sleep(5)
    tables.append(
        pd.read_html(
            StringIO(str(driver.page_source)),
            attrs={'class': 'table-component table-hover archive-games-table'}
        )[0]
    )

    table_user_cells = driver.find_elements(By.CLASS_NAME, 'archive-games-user-cell')
    for cell in table_user_cells:
        link = cell.find_elements(By.TAG_NAME, 'a')[0]
        game_links.append(link.get_attribute('href'))

driver.quit()

games = pd.concat(tables)

identifier = pd.Series(
    games['Players'] + str(games['Result']) + str(games['Moves']) + games['Date']
).apply(lambda x: x.replace(" ", ""))

games.insert(
    0,
    'GameId',
    identifier.apply(lambda x: hashlib.sha1(x.encode("utf-8")).hexdigest())
)

# load raw data into csv file
csv_path = "data/raw/games.csv"
if not os.path.exists(csv_path):
    games.to_csv(csv_path, index=False)

