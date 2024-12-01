from bots.passive.bot_actions.action_utils_async import *
import re
import asyncio  # Import asyncio to use await asyncio.sleep

async def re_captcha_like(page, tab):
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
    
    selected_post = await select_random_post(page, tab)
    
    # Get the <p> tag content within the selected post
    paragraph = await selected_post.query_selector("div > p")  # Adjust the selector if needed
    forms = await selected_post.query_selector_all("form")
    form = forms[1]
    post_action = await form.get_attribute("action")
    post_id_match = re.search(r'/comments/add/(\d+)/', post_action)
    post_id = post_id_match.group(1) if post_id_match else None

    if paragraph and post_id:
        post_content = await paragraph.text_content()
        print("Selected post content:", post_content, " on id ", post_id)
    else:
        print("Either <p> or id not found")
        return  # Exit the function if necessary elements are not found
    
    await nav_to_post(
        page,
        tab,
        css_selector=None,
        xpath=f"//div[@id='{tab}']//div[@id='like-button-{post_id}']//form[@id='like-form-{post_id}']"
    )
    
    action = {
        "action": "move_and_click",
        "target_role": None,
        "target_name": None,
        "css_selector": f"#like-form-{post_id}",
        "xpath": f"//div[@id='{tab}']//div[@id='like-button-{post_id}']//form[@id='like-form-{post_id}']",
        "text": None
    }
    
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
    
