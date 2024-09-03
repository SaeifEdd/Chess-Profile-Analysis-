import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime

st.write(
    """
         # Chess Profile Analysis 
          
    """
)

games = pd.read_csv('data/processed/games_processed.csv')
total_games = len(games)
# title
st.write(f"Total Number of Games Analyzed: {total_games}")

# rating over time
fig = px.line(games, x='Date', y='My Rating', title='Rating Over Time')
st.plotly_chart(fig)

# percentages of w/l/d
percentages = (games['W/L'].value_counts() / total_games) * 100
data = pd.DataFrame({
    'Result': percentages.index,
    'Percentage': percentages.values
})
# Create the pie chart
fig = px.pie(data, values='Percentage', names='Result', title='Win/Loss/Draw Percentages')
# Adjust the size of the plot
fig.update_layout(
    width=400,  # Set the width
    height=400  # Set the height
)
st.plotly_chart(fig)

# avg opponent ratings for w/l/d
avg_ratings = games.groupby('W/L')['Opponent Rating'].mean().reset_index()
fig = px.bar(
    avg_ratings,
    x='W/L',
    y='Opponent Rating',
    color='W/L',
    labels={'W/L': 'Result', 'Opponent Rating': 'Average Opponent Rating'},
    title='Average Opponent Rating by Result'
)

# Adjust the size of the plot
fig.update_layout(
    width=500,
    height=400
)
st.plotly_chart(fig)

# avg number of moves for w/l/d
avg_nb_moves = games.groupby('W/L')['Moves'].mean().reset_index()
fig = px.bar(
    avg_nb_moves,
    x='W/L',
    y='Moves',
    color='W/L',
    labels={'W/L': 'Result', 'Number of moves': 'Average Number of Moves'},
    title='Average number of Moves by Result'
)

# Adjust the size of the plot
fig.update_layout(
    width=500,
    height=400
)
st.plotly_chart(fig)

