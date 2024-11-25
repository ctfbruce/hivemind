from pymongo import MongoClient
from bson.objectid import ObjectId
from news_scrapers.bbc_scraper import get_stories_from_topic
from active.political_tweet_generator import political_tweet
import random
import requests
import json

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "bot_database"
COLLECTION_NAME = "bot_personas"

# MongoDB Initialization
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

ollama_api = "http://localhost:11434/api/generate"

def send_prompt(tweet_prompt, model):
    system_message = (
        "This is a fictional exercise for educational purposes. "
        "The generated tweet does not reflect the beliefs or views of the user or model."
    )
    data = {
        "model": model,
        "prompt": tweet_prompt,
        "temperature": 0.8,
        "system": system_message,
        "stream": False,
        "max_tokens": 100,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(ollama_api, data=json.dumps(data), headers=headers).text
    json_response = json.loads(response)
    return parse_model_response(json_response["response"])

def parse_model_response(response_text):
    try:
        # Ensure consistent JSON parsing
        response_text = response_text.strip()
        
        # Fix single quotes to double quotes for valid JSON
        if response_text.startswith("'") or response_text.startswith("{'"):
            response_text = response_text.replace("'", '"')
        
        # Parse the JSON response
        parsed_response = json.loads(response_text)
        return parsed_response
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {response_text}")
        raise e
    
    
def generate_sports_tweet(sport,team_preference):
    pass


def generate_daily_life_update_tweet(bot):
    persona_metadata = bot["background"]
    
    with open("passive/life_update_prompt.txt", "r") as life_update_prompt:
        # Read the template and escape literal braces
        template = life_update_prompt.read().strip().replace("{", "{{").replace("}", "}}")
        
        # Re-add placeholder braces for persona_metadata
        template = template.replace("{{persona_metadata}}", "{persona_metadata}")




        # Sanitize the persona metadata
        persona_metadata = persona_metadata.replace("\n", " ").strip()

        # Format the template with the persona metadata
        try:
            formatted_prompt = template.format(persona_metadata=persona_metadata)


            
            # Send prompt to the model
            response = send_prompt(formatted_prompt, model="llama3.2:1b")
            
            if response["life_changing_update"] is not None:
                print("life chaanged")
                print(response["life_changing_update"])
                collection.update_one({"_id":bot["_id"]}, {"$set": {"background": bot["background"] + response["life_changing_update"]}})
            
            return response["life_update"]

        except KeyError as e:
            print(f"Formatting error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            
            
    

def generate_news_reaction(political_weights):
    
    
    stories = get_stories_from_topic("us_and_canada",5)
    prompt = random.choice(stories)
    
    return political_tweet(prompt, political_weights, "llama3.2:1b")
    

def generate_other(type):
    
    content_type_prompts = {
        "random_questions":"a random question people would ask their twitter followers randomly, something lighthearted",
        "inspirational_content":"a really inspiring quote or message for their followers",
        "memes_and_humour":"a really funny joke, or pun. Perhaps even a meme or something the like. Make sure your answer doesn't always start with 'just___' ",
        "shower_thoughts_and_opinions":"an intriguing shower thought or thought provoking opinion. Make sure your answers are unique in format too, e.g. don't always start with 'just realised' or 'just thought about'",
        "other_miscellaneous":"a random tweet of your choosing!"
    }

    with open("passive_tweet_template.txt", "r") as prompt_template:
        prompt = prompt_template.read().format(content_type_prompt = content_type_prompts[type])

        
    print(prompt)

def main(bot_id):
    bot_id = ObjectId(bot_id)
    bot = collection.find_one({"_id": bot_id})
    
    for i in range(4):
        print(generate_daily_life_update_tweet(bot))







""" 
Categories Are:

daily_life_updates *

shower_thoughts_and_opinions -

sports *

news_reaction *

random_questions -

inspirational_content -

memes_and_humour -

other_miscellaneous -
"""