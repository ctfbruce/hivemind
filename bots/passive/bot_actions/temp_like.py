from bots.passive.bot_actions.action_utils import *
import re

def re_captcha_like(page, tab):
    time.sleep(1)
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
    
    nav_to_post(page, tab, post_id,
                xpath=f"//div[@id='{tab}']//div[@id='like-button-{post_id}']//form[@id='like-form-{post_id}']")
    
    action = {"action":"move_and_click", "target_role":None,"target_name":None, "css_selector":f"#like-form-{post_id}", "xpath":f"//div[@id='{tab}']//div[@id='like-button-{post_id}']//form[@id='like-form-{post_id}']", "text":None}
    perform_action_on_target(page,
                                 locate_target(page, 
                                               css_selector=action["css_selector"],
                                               xpath=action["xpath"]),
                                 action_type=action["action"],
                                 text=action["text"],
                                 )
    input("breaking")

    
    