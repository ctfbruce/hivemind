import random
import numpy as np
from datetime import datetime, timedelta

# Define time windows and weights
windows = [
    {"start": "6:30", "end": "11:00", "weight": 0.3},
    {"start": "11:00", "end": "16:00", "weight": 0.4},
    {"start": "16:00", "end": "18:00", "weight": 0.1},
    {"start": "18:00", "end": "23:00", "weight": 0.15},
    {"start": "23:00", "end": "3:00", "weight": 0.05},
]

def time_to_float(t):
    """Convert time (HH:MM) to hours past midnight (as float)."""
    h, m = map(int, t.split(":"))
    return h + m / 60

def float_to_time(t):
    """Convert hours past midnight (float) to time (HH:MM)."""
    h = int(t)
    m = int((t - h) * 60)
    return f"{h:02}:{m:02}"

def generate_tweet_time(window):
    """Generate a random tweet time within a window based on its weight."""
    # Probability of tweeting in this window
    if random.random() > window["weight"]:
        return None  # No tweet in this window

    # Calculate window parameters
    start = time_to_float(window["start"])
    end = time_to_float(window["end"])
    if end < start:  # Handle windows crossing midnight
        end += 24

    mean = (start + end) / 2
    std_dev = (end - start) / 6  # Spread is 1/6th of the window

    # Sample a time from the normal distribution
    tweet_time = np.random.normal(mean, std_dev)

    # Clamp the time to stay within the window
    tweet_time = max(start, min(end, tweet_time))

    # Convert back to HH:MM format
    return float_to_time(tweet_time % 24)  # Handle overflow past midnight

# Simulate tweets for all windows
for window in windows:
    tweet_time = generate_tweet_time(window)
    if tweet_time:
        print(f"Tweet scheduled at {tweet_time} in window {window['start']}–{window['end']}")
