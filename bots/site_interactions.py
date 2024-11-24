import requests
from bs4 import BeautifulSoup

# Base URL of the site
BASE_URL = "http://localhost:8000"

# Endpoints
LOGIN_ENDPOINT = "/users/login/"
REGISTER_ENDPOINT = "/users/register/"
POST_ENDPOINT = "/"


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

def register_user(username, email, password):
    """
    Register a user by fetching the CSRF token and sending a POST request with the user data.
    """
    with requests.Session() as session:

        register_url = BASE_URL + REGISTER_ENDPOINT
        csrf_token = extract_csrf_token(session, register_url)

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "username": username,
            "email": email,
            "password1": password,
            "password2": password
        }

        #necessary, else it breaks, due to django specifications
        headers = {"Referer": register_url}


        response = session.post(register_url, data=data, headers=headers)
        if response.status_code == 200:
            print("Registration successful!")
        else:
            print(f"Failed to register. Status Code: {response.status_code}")
            print(response.text)
            
def post(username, password, content):
    """
    Log in and post content using CSRF tokens and session cookies.
    """
    with requests.Session() as session:

        login_url = BASE_URL + LOGIN_ENDPOINT
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

        # Extract cookies for csrftoken and sessionid
        cookies = session.cookies.get_dict()
        csrftoken = cookies.get("csrftoken")
        sessionid = cookies.get("sessionid")

        if not csrftoken or not sessionid:
            raise Exception("CSRF token or session ID not found in login response.")

        print(f"Logged in with csrftoken={csrftoken}, sessionid={sessionid}")


        post_url = BASE_URL + POST_ENDPOINT
        post_csrf_token = extract_csrf_token(session, post_url)  # Fetch a new CSRF token for posting
        post_data = {
            "csrfmiddlewaretoken": post_csrf_token,
            "content": content,
        }
        post_headers = {
            "Referer": post_url,
            "Cookie": f"csrftoken={csrftoken}; sessionid={sessionid}",
        }
        post_response = session.post(post_url, data=post_data, headers=post_headers)

        if post_response.status_code == 200:
            print("Content posted successfully!")
        else:
            print(f"Failed to post content. Status Code: {post_response.status_code}")
            print(post_response.text)


