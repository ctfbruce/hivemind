import requests
from bs4 import BeautifulSoup
import random

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

def send_like_to_random_post(host, username, password):
    """
    Log in, fetch a post from the Discover or Trending tab, and send a like to it.
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
            print("used credentials", username, password)
            print("attempting to register again . . .")
            from bots.site_interactions import register_user
            register_user(username, username+"@gmail.com", password)

            raise Exception(f"Tab '{tab_id}' not found on the page. Could not like")

        # Find posts in the selected tab
        posts = tab_content.find_all("div", class_="card mb-3")
        if not posts:
            raise Exception(f"No posts found under the {tab_id} tab.")

        # Randomly select a post
        selected_post = random.choice(posts)

        # Extract the like form
        form = selected_post.find("form", {"hx-post": True})
        if not form:
            raise Exception("Like form not found in the selected post.")

        # Extract the hx-post URL and post ID
        hx_post_url = form.get("hx-post")
        if not hx_post_url:
            raise Exception("hx-post attribute not found in the like form.")

        # Extract post_id from hx-post URL, which is in format "/like/<post_id>/"
        post_id = hx_post_url.strip("/").split("/")[-1]

        # Extract CSRF token from the form
        csrf_token_input = form.find("input", {"name": "csrfmiddlewaretoken"})
        if not csrf_token_input:
            raise Exception("CSRF token input not found in like form.")

        csrf_token = csrf_token_input["value"]

        # Send the like
        like_url = f"{host}/like/{post_id}/"
        like_data = {
            "csrfmiddlewaretoken": csrf_token,
        }
        like_headers = {"Referer": main_page_url}

        like_response = session.post(like_url, data=like_data, headers=like_headers)

        if like_response.status_code == 200:
            print(f"Successfully liked post ID {post_id}.")
        else:
            raise Exception(f"Failed to like post. Status Code: {like_response.status_code}\nResponse text: {like_response.text}")



