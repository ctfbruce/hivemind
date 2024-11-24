import requests
import json
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()


MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "bot_database"
COLLECTION_NAME = "bot_personas"

# MongoDB Initialization
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

        
        
def create_credentials():
    return {"password":"fakepass",
            "username":"fakeuser"}

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
    
    #     # Add generated persona to MongoDB
    # credentials = create_credentials()
    # persona["credentials"] = credentials
    # collection.insert_one(persona)
    
    # return persona


def parse_api_response(response_content):
    # Remove code block markers (```json ... ```)
    cleaned_content = response_content.strip("```json\n").strip("```")
    # Parse the cleaned JSON string into a Python dictionary
    persona = json.loads(cleaned_content)
    return persona


def main():
    raw_response = create_persona()
    print("raw response", raw_response)
    parsed_response = parse_api_response(raw_response)
    
    print("parsed respose:", parsed_response)
    
    credentials = create_credentials()
    parsed_response["credentials"] = credentials
    collection.insert_one(parsed_response)

    print(f"New persona {parsed_response['name']} inserted")
if __name__ == "__main__":
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API Key is not set. Please check your .env file.")
    for i in range(4):
        main()




    