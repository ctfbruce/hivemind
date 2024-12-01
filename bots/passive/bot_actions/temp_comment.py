

import requests
from bs4 import BeautifulSoup
import random
from bots.passive.passive_tweet_generator import generate_comment
import re
from bots.passive.bot_actions.action_utils import *


def post_comment(page,tab,id, text, css_selector = None, xpath=None):
    
    if tab in ("trending", "recommended"):
        css_selector = f"#{tab}-posts-container form[action='/comments/add/{id}/'] textarea"
    elif tab in ("discover"):
        css_selector = f"#discover form[action='/comments/add/{id}/'] textarea"
        
        
    action_chain = [{"action":"move_and_type", "target_role":None,"target_name":None, "css_selector":css_selector, "xpath":None, "text":text, "special":"comment"},
                {"action":"move_and_click", "target_role":None,"target_name":None, "css_selector":None, "xpath":f"//div[@id='{tab}']//form[@action='/comments/add/{id}/']//button[@type='submit']", "text":None},
                ]
    for action in action_chain:
        target_element = locate_target(page, css_selector=action["css_selector"], target_name=action["target_name"],target_role=action["target_role"], xpath=action["xpath"])
        perform_action_on_target(page, target_element, action_type=action["action"], text=action["text"])
  
def re_captcha_comment(page, tab, persona_metadata):
    page.evaluate("""
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
    
    

    selected_post = select_random_post(page, tab)
    
    # Get the <p> tag content within the selected post
    paragraph = selected_post.query_selector("div > p")  # Adjust the selector if needed
    form = selected_post.query_selector_all("form")[1]
    post_id = form.get_attribute("action")
    post_id = re.search(r'/comments/add/(\d+)/', post_id).group(1)

    if paragraph and post_id:
        post_content = paragraph.text_content()
        print("Selected post content:", post_content, " on id ", post_id)
    else:
        print("Either <p> or id not found")
        
    new_comment = generate_comment(persona_metadata, post_content)
    #new_comment = f"this is not a generated comment, would've used {persona_metadata}"
    print(new_comment)
    
    if tab in ("trending", "recommended"):
        css_selector = f"#{tab}-posts-container form[action='/comments/add/{post_id}/'] textarea"
    elif tab in ("discover"):
        css_selector = f"#discover form[action='/comments/add/{post_id}/'] textarea"
     
    
    nav_to_post(page, tab, css_selector=css_selector)
    print("navigated to post")
    post_comment(page, tab, post_id, new_comment)
    print("posted comment")
    
    return {"post_id":int(post_id), "post_content":post_content}

