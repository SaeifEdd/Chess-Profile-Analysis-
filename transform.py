import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv


# ======================
# Helpers
# ======================
def extract_players_and_results(games: pd.DataFrame) -> pd.DataFrame:
    """Extract player names, ratings, and results from raw columns."""
    players = games['Players'].str.extract(
        r'(?P<white_player>.*?) \((?P<white_rating>\d+)\) (?P<black_player>.*?) \((?P<black_rating>\d+)\)'
    ).astype({"white_rating": int, "black_rating": int})

    results = (
        games['Result']
        .str.split("  ", expand=True)
        .rename(columns={0: "white_result", 1: "black_result"})
    )

    games = pd.concat([games, players, results], axis=1)

    return (
        games.assign(
            time=games["Unnamed: 0"],
            date=pd.to_datetime(
                games["Date"].str.replace(",", "") + " 00:00",
                format='%b %d %Y %H:%M',
            ),
        )
        .drop(columns=["Players", "Unnamed: 6", "Result", "Unnamed: 0"])
    )


def normalize_names(games: pd.DataFrame) -> pd.DataFrame:
    """Normalize player names to lowercase without spaces."""
    games["white_player"] = games["white_player"].str.strip().str.lower()
    games["black_player"] = games["black_player"].str.strip().str.lower()
    return games


def add_calculated_fields(games: pd.DataFrame, username: str) -> pd.DataFrame:
    """Add outcome, ratings, differences, and binary flags."""
    # check whether I was playing with B/W
    def is_me(col): return games[col] == username.lower()

    games = games.assign(
        # did I win, lose or draw
        W_L=np.select(
            [
                (is_me("white_player") & (games["white_result"] == "1")),
                (is_me("black_player") & (games["black_result"] == "1")),
                (is_me("white_player") & (games["white_result"] == "0")),
                (is_me("black_player") & (games["black_result"] == "0")),
            ],
            ["Win", "Win", "Loss", "Loss"],
            default="Draw",
        ),
        my_colour=np.where(is_me("white_player"), "White",
                 np.where(is_me("black_player"), "Black", None)),
        my_rating=np.where(is_me("white_player"), games["white_rating"], games["black_rating"]),
        opponent_rating=np.where(is_me("white_player"), games["black_rating"], games["white_rating"]),
    )

    games = games.assign(
        rating_difference=games["opponent_rating"] - games["my_rating"],
        win=((is_me("white_player") & (games["white_result"] == "1")) |
             (is_me("black_player") & (games["black_result"] == "1"))).astype(int),
        loss=((is_me("white_player") & (games["white_result"] == "0")) |
              (is_me("black_player") & (games["black_result"] == "0"))).astype(int),
        draw=((is_me("white_player") & (games["white_result"] == "½")) |
              (is_me("black_player") & (games["black_result"] == "½"))).astype(int),
        day=games["date"].dt.day,
        month=games["date"].dt.month,
        year=games["date"].dt.to_period("Y"),
        is_white=is_me("white_player").astype(int),
        is_black=is_me("black_player").astype(int),
    )

    return games


def reorder_columns(games: pd.DataFrame) -> pd.DataFrame:
    """Order columns: strings → numbers → binary → dates."""
    cols = ["GameId", "white_player", "black_player", "W_L", "my_colour",
            "Moves","Accuracy", "my_rating", "opponent_rating", "rating_difference",
            "white_rating", "black_rating","win", "loss", "draw", "is_white",
            "is_black", "white_result", "black_result", "date", "day", "month", "year"]

    ordered = cols
    return games[ordered]


def transform_games(games: pd.DataFrame, username: str) -> pd.DataFrame:
    """ transformation pipeline."""
    games = extract_players_and_results(games)
    games = normalize_names(games)
    games = add_calculated_fields(games, username)
    games = reorder_columns(games)
    return games


# ======================
# Main
# ======================
if __name__ == "__main__":
    load_dotenv()
    USERNAME = os.getenv("CUSERNAME")

    # Load raw
    games = pd.read_csv("data/games.csv")

    # Transform
    games = transform_games(games, USERNAME)

    # Save processed
    out_path = "data/processed_games.csv"
    games.to_csv(out_path, index=False)
    print(f"Processed games saved to {out_path}")
