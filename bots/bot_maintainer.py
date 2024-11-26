import csv
import os
import asyncio
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from bots.passive.bot_actions.tweet import tweet
from bots.passive.bot_actions.comment import fetch_comment_to_reply_to_and_comment
from bots.passive.bot_actions.like import send_like_to_random_post
import pandas as pd

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "bot_database"
COLLECTION_NAME = "bot_personas"
HOST = "http://localhost:8000/"
# MongoDB Initialization
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# CSV File Path
DAILY_SCHEDULE_FILE = "daily_schedule.csv"

def remove_nth_line_csv(file_name, n):
    df = pd.read_csv(file_name, header=None)
    df.drop(df.index[n], inplace=True)
    df.to_csv(file_name, index=False, header=False)
    
async def process_interaction():
    """Continuously check and post tweets based on the schedule."""
    while True:
        now = datetime.now().strftime("%H:%M")

        # Check if the schedule file exists
        if not os.path.exists(DAILY_SCHEDULE_FILE):
            print(f"{now} - Schedule file not found. Retrying in 5 seconds...")
            await asyncio.sleep(5)
            continue

        # Read the schedule file
        with open(DAILY_SCHEDULE_FILE, "r") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        if not rows:
            print(f"{now} - Schedule is empty. Retrying in 5 seconds...")
            await asyncio.sleep(5)
            continue

        # Process the topmost tweet
        row = rows[0]
        interaction_time = row["time"]
        bot_id = row["bot_id"]
        interaction_type = row["post_type"]
        name = row["name"]  # Optional for logging/debugging

        # Check if the tweet is due
        if now >= interaction_time:
            try:
                # Fetch bot credentials
                bot = collection.find_one({"_id": ObjectId(bot_id)})
                if not bot:
                    print(f"{now} - Bot with ID {bot_id} ({name}) not found in database.")
                else:
                    username = bot["basic_metadata"]["username"]
                    password = bot["password"]

                    if interaction_type == "like":
                        send_like_to_random_post(HOST, username, password)
                    elif interaction_type == "comment":
                        fetch_comment_to_reply_to_and_comment(HOST, username, password, bot["basic_metadata"]["background"])
                    else:
                        tweet(interaction_type, now, name, bot_id, username, password)
            except Exception as e:
                print(f"{now} - Error processing interaction: {e}")
                # Wait and try again
                await asyncio.sleep(5)
                continue

            # After processing, remove the top row and update the schedule file
            new_schedule = rows[1:]  # Remove the first row
            with open(DAILY_SCHEDULE_FILE, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["bot_id", "name", "post_type", "time"])
                writer.writeheader()
                writer.writerows(new_schedule)
        else:
            # Sleep until the interaction time or 5 seconds, whichever is smaller
            time_to_wait = (datetime.strptime(interaction_time, "%H:%M") - datetime.now()).total_seconds()
            sleep_time = min(max(time_to_wait, 0), 5)
            await asyncio.sleep(sleep_time)


def main():
    asyncio.run(process_interaction())

if __name__ == "__main__":
    main()
