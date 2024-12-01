from playwright.sync_api import sync_playwright
import math
import random
import time
from bots.passive.bot_actions.temp_comment import re_captcha_comment
from bots.passive.bot_actions.temp_post import re_captcha_post
from bots.passive.bot_actions.temp_like import re_captcha_like

from bots.passive.bot_actions.action_utils import *

def main(
    action,
    username,
    password,
    bot_id = None,
    tweet_type = None,
    persona_metadata = None,
    url='http://127.0.0.1:8000/',
    headers=None,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36", 
    browser_args=['--disable-blink-features=AutomationControlled'],
    viewport_width=1920,
    viewport_height=1080,
    headless=False,
    wait_until="domcontentloaded",
    java_script_enabled=True,
    timeout=10000,
    cursor_enabled=True
):
    with sync_playwright() as p:
        # Default browser arguments if not provided
        if browser_args is None:
            browser_args = ['--window-size=1920,1080', '--disable-blink-features=AutomationControlled']

        # Launch the browser
        browser = p.chromium.launch(headless=headless, args=browser_args)

        # Create a browser context with provided headers, user agent, and viewport
        context_args = {
            "viewport": {'width': viewport_width, 'height': viewport_height},
            "java_script_enabled": java_script_enabled,
        }
        if user_agent:
            context_args["user_agent"] = user_agent
        if headers:
            context_args["extra_http_headers"] = headers

        context = browser.new_context(**context_args)

        # Open a new page
        page = context.new_page()

        # Navigate to the target page
        print(f"Opening the page: {url}")
        page.goto(url, wait_until=wait_until, timeout=timeout)
        

        print("Page loaded successfully!")
        
        standard_log_in(page, username, password)
        
        if action == "post":
            re_captcha_post(page, bot_id, tweet_type)
        else:
            tab = "trending" if random.random() < 0.3 else "discover"
            if action == "comment":
                print("trying to comment")
                re_captcha_comment(page, tab, persona_metadata)
            elif action == "like":
                re_captcha_like(page, tab)
            else:
                raise KeyError("action not recognised")




if __name__ == '__main__':
    main("comment","theom","theom","is a tree lover", headless=False)
    #main("post", "theom", "theom", 3, "political", headless=False)
    #main("like", "theom", "theom", 3, headless=False)
"""

either only use Xpath or accept a locator object instead 
(in the main function for example, and pass that obj to the locate element function) 
of the individual locator things individually. 


right now, you call the function to get the comment id twice, 
once to find the box, and once to find the submit button. 
Problem is, that might result in two different IDs...... so you submit the wrong comment
Also, the scroll is not humanlike enough. its pretty shit...



"""