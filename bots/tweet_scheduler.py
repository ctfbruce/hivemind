import random
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "bot_database"
COLLECTION_NAME = "bot_personas"

# MongoDB Initialization
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

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

def schedule_tweets():
    """Query all bots and generate their tweets for the day."""
    # Fetch all bots from the database
    bots = list(collection.find())

    tweet_schedule = []

    # Iterate through each bot
    for bot in bots:
        


        
        bot_id = bot["_id"]
        bot_name = bot["name"]
        post_timing_weights = bot.get("post_timing_weights", {})

        # Define time windows and weights
        windows = [
            {"start": "6:30", "end": "11:00", "weight": post_timing_weights.get("6:30-11:00", 0)},
            {"start": "11:00", "end": "16:00", "weight": post_timing_weights.get("11:00-16:00", 0)},
            {"start": "16:00", "end": "18:00", "weight": post_timing_weights.get("16:00-18:00", 0)},
            {"start": "18:00", "end": "23:00", "weight": post_timing_weights.get("18:00-23:00", 0)},
            {"start": "23:00", "end": "3:00", "weight": post_timing_weights.get("23:00-3:00", 0)},
        ]

        # Generate tweet times for all windows
        for window in windows:
            tweet_time = generate_tweet_time(window)
            if tweet_time:
        
                tweet_schedule.append({
                    "bot_id": str(bot_id),
                    "time": tweet_time,
                    "name": str(bot_name),
                    "post_type": random.choices(
                        list(bot["post_type_weights"].keys()),
                        list(bot["post_type_weights"].values())
                    )[0]  # Extract the selected value from random.choices
                })

    # Sort the tweet schedule by time
    tweet_schedule.sort(key=lambda x: datetime.strptime(x["time"], "%H:%M"))

    return tweet_schedule

def main():
    # Get today's tweet schedule
    schedule = schedule_tweets()

    # Print schedule in chronological order
    print("Today's Tweet Schedule:")
    for entry in schedule:
        print(f"Bot ID: {entry['bot_id']} - {entry['name']} - {entry['post_type']}- Time: {entry['time']}")

if __name__ == "__main__":
    main()
