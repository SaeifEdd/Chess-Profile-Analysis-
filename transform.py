import numpy as np
import pandas as pd
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

load_dotenv()
USERNAME = os.getenv("CUSERNAME")
#print(USERNAME)
games = pd.read_csv("data/raw/games.csv")
# Split the 'Players' column into two parts: players and ratings
new = games['Players'].str.extract(r'(?P<White_Player>.*?) \((?P<White_Rating>\d+)\) (?P<Black_Player>.*?) \((?P<Black_Rating>\d+)\)')

# Convert the ratings to integers
new['White_Rating'] = new['White_Rating'].astype(int)
new['Black_Rating'] = new['Black_Rating'].astype(int)

# Add the new columns to the original DataFrame
games['White Player'] = new['White_Player']
games['White Rating'] = new['White_Rating']
games['Black Player'] = new['Black_Player']
games['Black Rating'] = new['Black_Rating']

# Add results
result = games.Result.str.split(" ", expand=True)
games['White Result'] = result[0]
games['Black Result'] = result[2]

# Drop unneccessary columns
games = games.rename(columns={"Unnamed: 0": "Time"})
games = games.drop(['Players', 'Unnamed: 6', 'Result', 'Accuracy'], axis=1)

# Add calculated columns for wins, losses, draws, ratings, year, game links
# Ensure the USERNAME and player names are in the same format
username = USERNAME.strip().lower()

# Normalize player names in the DataFrame
games['White Player'] = games['White Player'].str.strip().str.lower()
games['Black Player'] = games['Black Player'].str.strip().str.lower()

# Define conditions for win/loss/draw
conditions = [
    (games['White Player'] == username) & (games['White Result'] == '1'),
    (games['Black Player'] == username) & (games['Black Result'] == '1'),
    (games['White Player'] == username) & (games['White Result'] == '0'),
    (games['Black Player'] == username) & (games['Black Result'] == '0'),
]
choices = ["Win", "Win", "Loss", "Loss"]

# did I win or lost
games['W/L'] = np.select(conditions, choices, default="Draw")

# Am I playing with white or black
conditions = [
        (games['White Player'] == username),
        (games['Black Player'] == username)
        ]
choices = ["White", "Black"]
games['Colour'] = np.select(conditions, choices, default=None)

# my rating column
conditions = [
        (games['White Player'] == username),
        (games['Black Player'] == username)
        ]
choices = [games['White Rating'], games['Black Rating']]
games['My Rating'] = np.select(conditions, choices)

# opponent rating:
conditions = [
        (games['White Player'] != username),
        (games['Black Player'] != username)
        ]
choices = [games['White Rating'], games['Black Rating']]
games['Opponent Rating'] = np.select(conditions, choices)

# rating difference
games['Rating Difference'] = games['Opponent Rating'] - games['My Rating']

# win or not binary column
conditions = [
        (games['White Player'] == username) & (games['White Result'] == '1'),
        (games['Black Player'] == username) & (games['Black Result'] == '1')
        ]
choices = [1, 1]
games['Win'] = np.select(conditions, choices)

#lost or not binary column
conditions = [
        (games['White Player'] == username) & (games['White Result'] == '0'),
        (games['Black Player'] == username) & (games['Black Result'] == '0')
        ]
choices = [1, 1]
games['Loss'] = np.select(conditions, choices)

# draw or not binary column
conditions = [
        (games['White Player'] == username) & (games['White Result'] == '½'),
        (games['Black Player'] == username) & (games['Black Result'] == '½')
        ]
choices = [1, 1]
games['Draw'] = np.select(conditions, choices)

# day, month and year:
games['Day'] = pd.to_datetime(games['Date']).dt.day
games['Month'] = pd.to_datetime(games['Date']).dt.month

games['Year'] = pd.to_datetime(games['Date']).dt.to_period('Y')


# Optional calculated columns for indicating black or white pieces - uncomment if interested in these
games['Is_White'] = np.where(games['White Player']==username, 1, 0)
games['Is_Black'] = np.where(games['Black Player']==username, 1, 0)

# Correct date format
games["Date"] = pd.to_datetime(games["Date"].str.replace(",", "") + " 00:00", format = '%b %d %Y %H:%M')

csv_path = "data/processed/games_processed.csv"
if not os.path.exists(csv_path):
    games.to_csv(csv_path, index=False)
