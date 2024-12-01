import asyncio
from bots.passive.bot_actions.action_utils_async import *
from bots.passive.passive_tweet_generator import main as generate_tweet

async def re_captcha_post(page, bot_id, tweet_type):
    await page.wait_for_load_state("load")
    await page.evaluate("""
        const cursor = document.createElement('div');
        cursor.id = 'custom-cursor';
        cursor.style.width = '10px';
        cursor.style.height = '10px';
        cursor.style.borderRadius = '50%';
        cursor.style.background = 'red';
        cursor.style.position = 'absolute';
        cursor.style.zIndex = '10000';
        cursor.style.pointerEvents = 'none';
        document.body.appendChild(cursor);

        document.addEventListener('mousemove', event => {
            cursor.style.left = `${event.pageX}px`;
            cursor.style.top = `${event.pageY}px`;
        });
    """)

    new_post_content = generate_tweet(bot_id, tweet_type)
    # new_post_content = f"This is not a generated post; would've passed args: {bot_id} and {tweet_type}"

    action_chain = [
        {
            "action": "move_and_click",
            "target_role": None,
            "target_name": None,
            "css_selector": "#new-post-button",
            "xpath": None,
            "text": None
        },
        {
            "action": "move_and_type",
            "target_role": None,
            "target_name": None,
            "css_selector": "#new-post-button",
            "xpath": "/html/body/div[2]/div/main/div[2]/form/p/textarea",
            "text": new_post_content
        },
        {
            "action": "move_and_click",
            "target_role": None,
            "target_name": None,
            "css_selector": None,
            "xpath": "//*[@id='new-post-form']/button",
            "text": None
        },
    ]

    for action in action_chain:
        target_element = await locate_target(
            page,
            css_selector=action["css_selector"],
            xpath=action["xpath"]
        )
        await perform_action_on_target(
            page,
            target_element,
            action_type=action["action"],
            text=action["text"]
        )
