import asyncio
import requests
from bs4 import BeautifulSoup
import random
import re
from bots.passive.passive_tweet_generator import generate_comment
from bots.passive.bot_actions.action_utils_async import *
    
async def post_comment(page, tab, id, text, css_selector=None, xpath=None):
    if tab in ("trending", "recommended"):
        css_selector = f"#{tab}-posts-container form[action='/comments/add/{id}/'] textarea"
    elif tab == "discover":
        css_selector = f"#discover form[action='/comments/add/{id}/'] textarea"
    
    action_chain = [
        {
            "action": "move_and_type",
            "target_role": None,
            "target_name": None,
            "css_selector": css_selector,
            "xpath": None,
            "text": text,
            "special": "comment"
        },
        {
            "action": "move_and_click",
            "target_role": None,
            "target_name": None,
            "css_selector": None,
            "xpath": f"//div[@id='{tab}']//form[@action='/comments/add/{id}/']//button[@type='submit']",
            "text": None
        },
    ]
    for action in action_chain:
        target_element = await locate_target(
            page,
            css_selector=action["css_selector"],
            target_name=action["target_name"],
            target_role=action["target_role"],
            xpath=action["xpath"]
        )
        await perform_action_on_target(
            page,
            target_element,
            action_type=action["action"],
            text=action["text"]
        )

async def re_captcha_comment(page, tab, persona_metadata):
    await page.wait_for_load_state("load")
    

    selected_post = await select_random_post(page, tab)
    
    # Get the <p> tag content within the selected post
    paragraph = await selected_post.query_selector("div > p")  # Adjust the selector if needed
    forms = await selected_post.query_selector_all("form")
    form = forms[1] if len(forms) > 1 else None
    if form:
        post_action = await form.get_attribute("action")
        post_id_match = re.search(r'/comments/add/(\d+)/', post_action)
        post_id = post_id_match.group(1) if post_id_match else None
    else:
        post_id = None

    if paragraph and post_id:
        post_content = await paragraph.text_content()
        print("Selected post content:", post_content, " on id ", post_id)
    else:
        print("Either <p> or id not found")
        return  # Exit the function if necessary elements are not found
    
    new_comment = generate_comment(persona_metadata, post_content)
    print(new_comment)
    
    if tab in ("trending", "recommended"):
        css_selector = f"#{tab}-posts-container form[action='/comments/add/{post_id}/'] textarea"
    elif tab == "discover":
        css_selector = f"#discover form[action='/comments/add/{post_id}/'] textarea"
     
    await nav_to_post(page, tab, css_selector=css_selector)
    print("Navigated to post")
    await post_comment(page, tab, post_id, new_comment)
    print("Posted comment")
    
    return {"post_id": int(post_id), "post_content": post_content}



