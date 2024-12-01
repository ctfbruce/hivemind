import asyncio
from playwright.async_api import async_playwright
import math
import random
import re
from bots.passive.bot_actions.temp_comment_async import re_captcha_comment
from bots.passive.bot_actions.temp_post_async import re_captcha_post
from bots.passive.bot_actions.temp_like_async import re_captcha_like
from bots.passive.bot_actions.action_utils_async import *


async def main(
    action,
    username,
    password,
    bot_id=None,
    tweet_type=None,
    persona_metadata=None,
    url='http://127.0.0.1:8000/',
    headers=None,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36",
    browser_args=None,
    viewport_width=1920,
    viewport_height=1080,
    headless=True,
    wait_until="domcontentloaded",
    java_script_enabled=True,
    timeout=10000,
    cursor_enabled=True
):
    async with async_playwright() as p:
        # Default browser arguments if not provided
        if browser_args is None:
            browser_args = ['--window-size=1920,1080', '--disable-blink-features=AutomationControlled']

        # Launch the browser
        browser = await p.chromium.launch(headless=headless, args=browser_args)

        # Create a browser context with provided headers, user agent, and viewport
        context_args = {
            "viewport": {'width': viewport_width, 'height': viewport_height},
            "java_script_enabled": java_script_enabled,
        }
        if user_agent:
            context_args["user_agent"] = user_agent
        if headers:
            context_args["extra_http_headers"] = headers

        context = await browser.new_context(**context_args)

        # Open a new page
        page = await context.new_page()

        # Navigate to the target page
        print(f"Opening the page: {url}")
        await page.goto(url, wait_until=wait_until, timeout=timeout)

        print("Page loaded successfully!")

        await standard_log_in(page, username, password)

        if action == "post":
            await re_captcha_post(page, bot_id, tweet_type)
        else:
            tab = "trending" if random.random() < 0.3 else "discover"
            if action == "comment":
                print("Trying to comment")
                await re_captcha_comment(page, tab, persona_metadata)
            elif action == "like":
                await re_captcha_like(page, tab)
            else:
                raise KeyError("Action not recognized")

        await browser.close()





# if __name__ == '__main__':
#     asyncio.run(main("comment", "theom", "theom", persona_metadata="is a tree lover", headless=False))
#     # asyncio.run(main("post", "theom", "theom", bot_id=3, tweet_type="political", headless=False))
#     # asyncio.run(main("like", "theom", "theom", headless=False))
