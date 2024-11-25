import csv
import os
import asyncio
from datetime import datetime
from passive.passive_tweet_generator import main as generate_tweet
from site_interactions import post
from pymongo import MongoClient
from bson.objectid import ObjectId


# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "bot_database"
COLLECTION_NAME = "bot_personas"

# MongoDB Initialization
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# CSV File Path
DAILY_SCHEDULE_FILE = "daily_schedule.csv"

async def process_tweets():
    """Continuously check and post tweets based on the schedule."""
    while True:
        now = datetime.now().strftime("%H:%M")

        # Check if the schedule file exists
        if not os.path.exists(DAILY_SCHEDULE_FILE):
            print(f"{now} - Schedule file not found. Retrying in 5 seconds...")
            await asyncio.sleep(5)
            continue

        tweet_processed = False  # Track if any tweets are processed in this loop
        new_schedule = []

        # Read the schedule file
        with open(DAILY_SCHEDULE_FILE, "r") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        # Process tweets
        for row in rows:
            tweet_time = row["time"]
            bot_id = row["bot_id"]
            post_type = row["post_type"]
            name = row["name"]  # Optional for logging/debugging

            # Check if the tweet is due
            if now >= tweet_time:
                tweet_processed = True

                # Fetch bot credentials
                bot = collection.find_one({"_id": ObjectId(bot_id)})
                if not bot:
                    print(f"{now} - Bot with ID {bot_id} ({name}) not found in database.")
                    continue

                username = bot["basic_metadata"]["username"]
                password = bot["password"]

                # Generate the tweet content
                try:
                    print("\n post type is", post_type)
                    content = generate_tweet(bot_id, post_type)
                except Exception as e:
                    print(f"{now} - Error generating tweet content for {name} ({bot_id}): {e}")
                    continue

                # Post the tweet
                try:
                    post(username, password, content)
                    print(f"{now} - Tweet posted by {name} ({username}): {content}")
                except Exception as e:
                    print(f"{now} - Failed to post tweet for {name} ({username}). Error: {e}")
            else:
                new_schedule.append(row)

        # Update the schedule file if any tweets were processed
        if tweet_processed:
            with open(DAILY_SCHEDULE_FILE, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["bot_id", "name", "post_type", "time"])
                writer.writeheader()
                writer.writerows(new_schedule)

        # Sleep briefly to avoid high CPU usage
        await asyncio.sleep(5)

def main():
    asyncio.run(process_tweets())

if __name__ == "__main__":
    main()
