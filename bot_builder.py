import requests
import json
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv
import os
import random
import secrets
import string

load_dotenv()


MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "bot_database"
COLLECTION_NAME = "bot_personas"

# MongoDB Initialization
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]



def generate_password():
    password_length = random.randint(12, 16)
    characters = string.ascii_letters + string.digits + "!@#$%^&*()_-+=<>?"
    password = ''.join(secrets.choice(characters) for _ in range(password_length))

    return password
        
def create_persona():
    
    #load prompt
    prompt = ""
    with open("persona_creation_prompt.txt","r") as prompt:
        prompt = prompt.read()
    

    client = OpenAI()

    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],

    )

    return completion.choices[0].message.content
    

def parse_api_response(response_content):
    # Remove code block markers (```json ... ```)
    cleaned_content = response_content.strip("```json\n").strip("```")
    # Parse the cleaned JSON string into a Python dictionary
    persona = json.loads(cleaned_content)
    return persona


def main():
    raw_response = create_persona()
    #print("raw response", raw_response)
    parsed_response = parse_api_response(raw_response)
    
    #print("parsed respose:", parsed_response)
    

    parsed_response["password"] = generate_password()
    collection.insert_one(parsed_response)
    print(f"New persona {parsed_response['basic_metadata']['name']} inserted")


    from bots.site_interactions import register_user
    
    print("now registering . . .")
    register_user(parsed_response["basic_metadata"]["username"], parsed_response["basic_metadata"]["username"]+"@gmail.com", parsed_response["password"])
    print("registered!")
    
    
if __name__ == "__main__":
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API Key is not set. Please check your .env file.")
    for i in range(400):
        main()




    