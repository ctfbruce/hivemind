

import requests
from bs4 import BeautifulSoup
import random
from bots.passive.passive_tweet_generator import generate_comment
def extract_csrf_token(session, url):
    """
    Extract the CSRF token from the given URL using the provided session.
    """
    response = session.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to load page: {url} (Status Code: {response.status_code})")

    # Parse the response to find the CSRF token
    soup = BeautifulSoup(response.text, "html.parser")
    token = soup.find("input", {"name": "csrfmiddlewaretoken"})
    if not token:
        raise Exception("CSRF token not found on the page.")
    return token["value"]


def fetch_comment_to_reply_to_and_comment(host, username, password, persona_metadata):
    """
    Log in, fetch a post from the Discover or Trending tab, generate a comment, and post it.
    """
    with requests.Session() as session:
        # Log in
        login_url = f"{host}/users/login/"
        csrf_token = extract_csrf_token(session, login_url)

        login_data = {
            "csrfmiddlewaretoken": csrf_token,
            "username": username,
            "password": password,
        }
        login_headers = {"Referer": login_url}
        login_response = session.post(login_url, data=login_data, headers=login_headers)

        if login_response.status_code != 200:
            raise Exception(f"Login failed: {login_response.status_code}")

        # Fetch the main page
        main_page_url = f"{host}/"
        response = session.get(main_page_url)
        if response.status_code != 200:
            raise Exception(f"Failed to load the main page. Status Code: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")

        # Select Discover or Trending tab
        tab_id = "discover" if random.random() < 0.7 else "trending"
        tab_content = soup.find("div", {"id": tab_id})
        if not tab_content:
            raise Exception(f"Tab '{tab_id}' not found on the page.")

        # Find posts in the selected tab
        posts = tab_content.find_all("div", class_="card mb-3")
        if not posts:
            raise Exception(f"No posts found under the {tab_id} tab.")

        # Randomly select a post
        selected_post = random.choice(posts)

        # Extract comment content and post ID
        post_id = selected_post.find("form", {"action": True})["action"].split("/")[-2]
        post_content = selected_post.find("p").get_text(strip=True)

        # Generate a new comment
        new_comment = generate_comment(persona_metadata, post_content)

        # Post the comment
        comment_url = f"{host}/comments/add/{post_id}/"
        csrf_token = extract_csrf_token(session, f"{host}/")

        comment_data = {
            "csrfmiddlewaretoken": csrf_token,
            "content": new_comment,
        }
        comment_headers = {"Referer": comment_url}

        comment_response = session.post(comment_url, data=comment_data, headers=comment_headers)

        if comment_response.status_code == 200:
            print(f"Comment posted successfully on post ID {post_id}.")
        else:
            raise Exception(f"Failed to post comment. Status Code: {comment_response.text}")

# from pymongo import MongoClient
# from bson.objectid import ObjectId

# MONGO_URI = "mongodb://localhost:27017/"
# DB_NAME = "bot_database"
# COLLECTION_NAME = "bot_personas"

# # MongoDB Initialization
# client = MongoClient(MONGO_URI)
# db = client[DB_NAME]
# collection = db[COLLECTION_NAME]

# BASE_URL = "http://localhost:8000"

# bot = collection.find_one({"_id": ObjectId("674477f12e67252ec6cd7483")})

# fetch_comment_to_reply_to_and_comment(BASE_URL,bot["basic_metadata"]["username"], bot["password"], bot["basic_metadata"]["background"])