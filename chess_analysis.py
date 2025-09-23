import streamlit as st
import plotly.express as px
import pandas as pd
from PIL import Image
from datetime import datetime, timedelta


# ======================
# Helper functions
# ======================
def load_data(path="data/processed_games.csv"):
    return pd.read_csv(path)

def display_total_games(games):
    st.write(f"**Total Number of Games Analyzed:** {len(games)}")

def plot_rating_over_time(games):
    fig = px.line(games, x='date', y='my_rating', title='Rating Over Time')
    st.plotly_chart(fig)

def plot_wld_percentages(games):
    total_games = len(games)
    percentages = (games['W_L'].value_counts() / total_games) * 100
    data = pd.DataFrame({'Result': percentages.index, 'Percentage': percentages.values})
    fig = px.pie(data, values='Percentage', names='Result', title='Win/Loss/Draw Percentages')
    fig.update_layout(width=400, height=400)
    st.plotly_chart(fig)

def plot_avg_opponent_rating(games):
    avg_ratings = games.groupby('W_L')['opponent_rating'].mean().reset_index()
    fig = px.bar(avg_ratings, x='W_L', y='opponent_rating', color='W_L',
                 labels={'W_L': 'Result', 'opponent_rating': 'Average Opponent Rating'},
                 title='Average Opponent Rating by Result')
    fig.update_layout(width=500, height=400)
    st.plotly_chart(fig)

def plot_avg_moves(games):
    avg_moves = games.groupby('W_L')['Moves'].mean().reset_index()
    fig = px.bar(avg_moves, x='W_L', y='Moves', color='W_L',
                 labels={'W_L': 'Result', 'Moves': 'Average Number of Moves'},
                 title='Average Number of Moves by Result')
    fig.update_layout(width=500, height=400)
    st.plotly_chart(fig)


# ======================
# App Layout
# ======================
st.set_page_config(page_title="Chess Profile Analysis", layout="wide")

# Banner
st.markdown("""
<style>
.block-container { padding-top: 0rem; }
.banner img { max-height: 120px; object-fit: cover; }
</style>
""", unsafe_allow_html=True)
st.image("assets/img2.jpeg", use_container_width=True)

# Title
st.title("♟️ Chess Profile Analysis")
# Sidebar
st.sidebar.header("Filters")
st.sidebar.write("Use the dropdown below to select a time range.")
# Data loading
games = load_data()
games["date"] = pd.to_datetime(games["date"])
# Date filter
date_options = {
    "All Time": None,
    "Past Week": 7,
    "Past Month": 30,
    "Past 3 Months": 90,
    "Past 6 Months": 180,
    "Past Year": 365,
    "Past 2 Years": 730
}
selected_period = st.sidebar.selectbox(
    "📅 Date Range:",
    list(date_options.keys())
)

# Apply filter
if date_options[selected_period] is None:
    filtered_games = games  # Show all data
else:
    cutoff_date = datetime.now() - timedelta(days=date_options[selected_period])
    filtered_games = games[games["date"] >= cutoff_date]

# show charts
display_total_games(filtered_games)
plot_rating_over_time(filtered_games)
col1, col2 = st.columns(2)
with col1:
    plot_wld_percentages(filtered_games)
with col2:
    plot_avg_opponent_rating(filtered_games)
plot_avg_moves(filtered_games)



