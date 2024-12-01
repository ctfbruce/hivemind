import csv
import os
import asyncio
import sys
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from bots.passive.bot_actions.temp_recaptcha_click_and_type_async import main as re_captcha_action
from rich.logging import RichHandler
import logging

# Configure rich logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(levelname)s - %(task_id)s - %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "bot_database"
BOT_COLLECTION_NAME = "bot_personas"
SCHEDULE_COLLECTION_NAME = "interaction_schedule"
HOST = "http://localhost:8000/"

# MongoDB Initialization
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
bot_collection = db[BOT_COLLECTION_NAME]
schedule_collection = db[SCHEDULE_COLLECTION_NAME]

# CSV File Path
DAILY_SCHEDULE_FILE = "daily_schedule.csv"


class TaskAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return msg, dict(kwargs, extra={'task_id': self.extra['task_id']})



async def process_interaction(interaction, semaphore):
    """Process a single interaction with concurrency control."""
    async with semaphore:
        task_id = interaction.get('name', 'Unknown')
        logger = TaskAdapter(logging.getLogger(__name__), {'task_id': task_id})

        now = datetime.now().strftime("%H:%M")
        interaction_time = interaction["time"]
        bot_id = interaction["bot_id"]
        interaction_type = interaction["post_type"]
        name = interaction["name"]  # Optional for logging/debugging

        try:
            # Fetch bot credentials
            bot = bot_collection.find_one({"_id": ObjectId(bot_id)})
            if not bot:
                logger.error(f"{now} - Bot with ID {bot_id} ({name}) not found in database.")
            else:
                username = bot["basic_metadata"]["username"]
                password = bot["password"]
                
                logger.info(f"Starting {interaction_type} interaction.")

                if interaction_type == "like":
                    await re_captcha_action(
                        "like",
                        username,
                        password,
                    )
                elif interaction_type == "comment":
                    await re_captcha_action(
                        "comment",
                        username,
                        password,
                        persona_metadata=bot["basic_metadata"]["background"]
                    )
                else:
                    await re_captcha_action(
                        "post",
                        username,
                        password,
                        bot_id=bot_id,
                        tweet_type=interaction_type
                    )
                logger.info(f"Completed {interaction_type} interaction.")

        except Exception as e:
            logger.error(f"{now} - Error processing interaction: {e}")

async def main(max_concurrent_tasks):
    # At the start, read the CSV file and insert interactions into MongoDB
    if os.path.exists(DAILY_SCHEDULE_FILE):
        with open(DAILY_SCHEDULE_FILE, "r") as file:
            reader = csv.DictReader(file)
            interactions = list(reader)
            # Insert interactions into MongoDB
            for interaction in interactions:
                # Convert interaction_time to datetime
                interaction_time_str = interaction["time"]
                interaction_time = datetime.strptime(interaction_time_str, "%H:%M")
                interaction_time = interaction_time.replace(
                    year=datetime.now().year, month=datetime.now().month, day=datetime.now().day
                )
                interaction["interaction_time"] = interaction_time
                # Insert into MongoDB
                schedule_collection.insert_one(interaction)
    else:
        print("Schedule file not found.")

    # Remove the CSV file since the schedule is now in MongoDB
    if os.path.exists(DAILY_SCHEDULE_FILE):
        os.remove(DAILY_SCHEDULE_FILE)

    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    while True:
        now = datetime.now()
        # Find all due interactions
        due_interactions = schedule_collection.find({
            "interaction_time": {"$lte": now}
        })

        tasks = []
        for interaction in due_interactions:
            # Atomically remove the interaction from the collection
            result = schedule_collection.find_one_and_delete({
                "_id": interaction["_id"]
            })
            if result:
                tasks.append(asyncio.create_task(process_interaction(result, semaphore)))

        if tasks:
            await asyncio.gather(*tasks)

        # Sleep until the next interaction is due or 5 seconds
        next_interaction = schedule_collection.find_one(
            {},
            sort=[("interaction_time", 1)]
        )
        if next_interaction:
            next_interaction_time = next_interaction["interaction_time"]
            time_to_wait = (next_interaction_time - datetime.now()).total_seconds()
            sleep_time = max(time_to_wait, 0)
        else:
            # No interactions left, sleep for 5 seconds
            sleep_time = 5

        await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    # Default maximum number of concurrent tasks
    DEFAULT_MAX_CONCURRENT_TASKS = 10

    # Get the max concurrent tasks from command-line arguments
    if len(sys.argv) > 1:
        try:
            max_concurrent_tasks = int(sys.argv[1])
        except ValueError:
            print("Invalid concurrency limit provided. Using default value.")
            max_concurrent_tasks = DEFAULT_MAX_CONCURRENT_TASKS
    else:
        max_concurrent_tasks = DEFAULT_MAX_CONCURRENT_TASKS

    print(f"Running with a maximum of {max_concurrent_tasks} concurrent tasks.")
    asyncio.run(main(max_concurrent_tasks))
