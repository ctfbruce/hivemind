import csv
import os
import asyncio
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from bots.passive.bot_actions.tweet import tweet
from bots.passive.bot_actions.comment import fetch_comment_to_reply_to_and_comment
from bots.passive.bot_actions.like import send_like_to_random_post

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

async def process_interaction():
    """Continuously check and post tweets based on the schedule."""
    while True:
        now = datetime.now().strftime("%H:%M")

        # Check if the schedule file exists
        if not os.path.exists(DAILY_SCHEDULE_FILE):
            print(f"{now} - Schedule file not found. Retrying in 5 seconds...")
            await asyncio.sleep(5)
            continue

        interaction_processed = False  # Track if any tweets are processed in this loop
        new_schedule = []

        # Read the schedule file
        with open(DAILY_SCHEDULE_FILE, "r") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        # Process tweets
        for row in rows:
            interaction_time = row["time"]
            bot_id = row["bot_id"]
            interaction_type = row["post_type"]
            name = row["name"]  # Optional for logging/debugging

            # Check if the tweet is due
            if now >= interaction_time:
                interaction_processed = True

                # Fetch bot credentials
                bot = collection.find_one({"_id": ObjectId(bot_id)})
                if not bot:
                    print(f"{now} - Bot with ID {bot_id} ({name}) not found in database.")
                    continue

                username = bot["basic_metadata"]["username"]
                password = bot["password"]

                if interaction_type == "like":
                    send_like_to_random_post(HOST, username,password)
                elif interaction_type == "comment":
                    fetch_comment_to_reply_to_and_comment(HOST, username,password, bot["basic_metadata"]["background"])
                else:
                    tweet(interaction_type, now, name, bot_id, username, password)
                
                
            else:
                new_schedule.append(row)

        # Update the schedule file if any tweets were processed
        if interaction_processed:
            with open(DAILY_SCHEDULE_FILE, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["bot_id", "name", "post_type", "time"])
                writer.writeheader()
                writer.writerows(new_schedule)

        # Sleep briefly to avoid high CPU usage
        await asyncio.sleep(5)

def main():
    asyncio.run(process_interaction())

if __name__ == "__main__":
    main()
