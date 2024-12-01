from playwright.sync_api import sync_playwright
import math
import random
import time
from bots.passive.bot_actions.comment import re_captcha_comment


def select_sequence(username, password, tab, action,text=None,id = None):
    if action == "like":
        action_chain=[
                {"action":"move_and_type", "target_role":None,"target_name":None, "css_selector":"#id_username", "xpath":None, "text":username},
                {"action":"move_and_type", "target_role":None,"target_name":None, "css_selector":"#id_password", "xpath":None, "text":password},
                {"action":"move_and_click", "target_role":"button","target_name":"Log In", "css_selector":None, "xpath":None, "text":None},
                {"action":"move_and_click", "target_role":None,"target_name":None, "css_selector":f"#{tab}-tab", "xpath":None, "text":None},
                {"action":"move_and_click", "target_role":None,"target_name":None, "css_selector":"#like-form-{id}", "xpath":f"//div[@id='{tab}']//div[@id='like-button-{id}']//form[@id='like-form-{id}']", "text":None},
                ]
    elif action == "comment":
        action_chain=[
                {"action":"move_and_type", "target_role":None,"target_name":None, "css_selector":"#id_username", "xpath":None, "text":username},
                {"action":"move_and_type", "target_role":None,"target_name":None, "css_selector":"#id_password", "xpath":None, "text":password},
                {"action":"move_and_click", "target_role":"button","target_name":"Log In", "css_selector":None, "xpath":None, "text":None},
                {"action":"move_and_click", "target_role":None,"target_name":None, "css_selector":f"#{tab}-tab", "xpath":None, "text":None},
                {"action":"move_and_type", "target_role":None,"target_name":None, "css_selector":"#trending-posts-container form[action='/comments/add/{id}/'] textarea", "xpath":None, "text":"ooga", "special":"comment"},
                {"action":"move_and_click", "target_role":None,"target_name":None, "css_selector":None, "xpath":f"//div[@id='{tab}']//form[@action='/comments/add/{id}/']//button[@type='submit']", "text":None},
                ]
    elif action == "post":
        action_chain=[
                {"action":"move_and_type", "target_role":None,"target_name":None, "css_selector":"#id_username", "xpath":None, "text":username},
                {"action":"move_and_type", "target_role":None,"target_name":None, "css_selector":"#id_password", "xpath":None, "text":password},
                {"action":"move_and_click", "target_role":"button","target_name":"Log In", "css_selector":None, "xpath":None, "text":None},
                {"action":"move_and_click", "target_role":None,"target_name":None, "css_selector":"#new-post-button", "xpath":None, "text":None},
                {"action":"move_and_type", "target_role":None,"target_name":None, "css_selector":"#new-post-button", "xpath":"/html/body/div[2]/div/main/div[2]/form/p/textarea", "text":text},
                {"action":"move_and_click", "target_role":None,"target_name":None, "css_selector":None, "xpath":"""//*[@id="new-post-form"]/button""", "text":None},

                ]
    else:
        raise KeyError("action not recognised in select_sequence()")
    
    return action_chain


def main(
    action_chain,
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

        
        
            
        for action in action_chain:
            if cursor_enabled:
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
            if action.get("special") == "comment":
                random_id_and_content = re_captcha_comment(page, "trending")
                action["css_selector"] = action["css_selector"].format(id = random_id_and_content["post_id"])
                action["text"] = random_id_and_content["post_content"]
                print("now gonna type comment", action["css_selector"])
            
            target_element = locate_target(page, css_selector=action["css_selector"], target_name=action["target_name"],target_role=action["target_role"], xpath=action["xpath"])
            if action["action"] in ("move_and_click", "move_and_type"):
                perform_action_on_target(page, target_element, action["action"], text = action["text"])
                page.screenshot(path="afteraction.png", full_page=True)
            else:
                raise KeyError(f"Unknown action type: {action['action']}")


            # Close the browser
            #print(f"{action['action']} completed. Moving to next action...")
        input("hello")
        browser.close()


def locate_target(page,css_selector=None, target_role=None, target_name=None, xpath=None):
        # Locate the target element by role and name
        target_element = None
        if target_role and target_name:
            print(f"Locating element with role='{target_role}' and name='{target_name}'...")
            target_element = page.get_by_role(target_role, name=target_name)
        elif xpath:
            target_element = page.locator("xpath="+xpath)
        elif css_selector:
            target_element = page.locator(css_selector)
        
        if target_element:
            return target_element
        else:
            raise KeyError("element was not found, double check css_selector or target_role")
def human_like_scroll_to_element(page, target_element):
    """
    Scrolls the page from the top to the target element in a human-like fashion.
    """
    page.evaluate("window.scrollTo(0, 0)")  # Start from the top of the page

    # Get the target element's position
    bounding_box = target_element.bounding_box()
    if not bounding_box:
        print("Could not determine bounding box for the target element.")
        raise Exception("Bounding box is None for the target element.")

    target_y = bounding_box['y']

    # Calculate the total scroll distance
    total_scroll_distance = target_y

    # Set the initial scroll position
    current_scroll_position = 0

    # Define scrolling parameters
    average_step_size = 100  # Average pixels to scroll each step
    step_size_variability = 50  # Variability in step size
    min_delay = 0.05  # Minimum delay between scroll steps (in seconds)
    max_delay = 0.2   # Maximum delay between scroll steps (in seconds)

    # Scroll in steps until we reach or pass the target position
    while current_scroll_position < total_scroll_distance:
        # Calculate a random step size
        step_size = random.randint(
            average_step_size - step_size_variability,
            average_step_size + step_size_variability
        )

        # Ensure we don't scroll past the target
        if current_scroll_position + step_size > total_scroll_distance:
            step_size = total_scroll_distance - current_scroll_position

        # Scroll by the step size
        current_scroll_position += step_size
        page.evaluate(f"window.scrollBy(0, {step_size})")

        # Random delay between steps to mimic human scrolling speed variability
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

def perform_action_on_target(page, target_element, action_type, text=None):
    """
    Perform a specified action (move_and_click or move_and_type) on the target element.
    """
    human_like_scroll_to_element(page, target_element)

    bounding_box = target_element.bounding_box()
    if bounding_box:
        # Target coordinates
        target_x = bounding_box["x"] + bounding_box["width"] / 2
        target_y = bounding_box["y"] + bounding_box["height"] / 2

        # Perform pronounced random movements to simulate human behavior
        random_mouse_movements_to_target(page, 960, 540, target_x, target_y)

        if text in ("bruh", "hello world", "first evaded post"):

            print("at perform action")
            #input("hello0")
        else:
            print("no joy", text)

        # Perform the desired action
        if action_type == "move_and_click":
            page.mouse.click(target_x, target_y)
            #print("Click performed successfully.")
        elif action_type == "move_and_type":
            page.mouse.click(target_x, target_y)
            for char in text:
                print("typing ", char)
                page.keyboard.type(char)
                delay = random.uniform(0.05, 0.3)  # Random delay between 50ms and 300ms
                time.sleep(delay)
            #print("Typing performed successfully.")
        else:
            raise KeyError("unidentified action type")
    else:
        print("Could not determine bounding box for the target element.")





def random_mouse_movements_to_target(page, start_x, start_y, target_x, target_y):
    """
    Simulate pronounced, human-like mouse movements starting from the center of the screen
    and covering a wide area before reaching the target.
    """
    #print("Simulating pronounced random mouse movements to the target...")
    steps = 3  # Total steps for the movement
    duration = random.uniform(0.02, 0.05)  # Slightly longer duration for more pronounced movements

    # Wide Lissajous curve parameters for large sweeping motions
    a = random.randint(2, 6)  # Frequency on the x-axis
    b = random.randint(2, 6)  # Frequency on the y-axis
    delta = random.uniform(0, math.pi)  # Phase shift

    for i in range(steps):
        t = i / steps * 2 * math.pi  # Normalize time across steps
        # Wide sweeping motion with jitter
        intermediate_x = (
            start_x + random.randint(-800, 800) * math.sin(a * t + delta)  # Random amplitude
        )
        intermediate_y = (
            start_y + random.randint(-500, 500) * math.sin(b * t)  # Random amplitude
        )

        # Move the mouse to the intermediate point
        page.mouse.move(intermediate_x, intermediate_y, steps=random.randint(8, 15))  # Add variability in smoothness
        time.sleep(duration + random.uniform(0.005, 0.02))  # Add variability in speed

    # Sharp random movements near the target for realism
    #print("Adding sharp random movements near the target...")
    for _ in range(5):
        sharp_x = target_x + random.uniform(-50, 50)
        sharp_y = target_y + random.uniform(-50, 50)
        page.mouse.move(sharp_x, sharp_y, steps=random.randint(3, 10))
        time.sleep(random.uniform(0.01, 0.03))

    # Final precise movement to the target position
    page.mouse.move(target_x, target_y, steps=random.randint(8, 15))
    #print("Mouse movement to the target completed.")


if __name__ == '__main__':
    # main(
    #     url='http://127.0.0.1:8000/',
    #     action_type="move_and_click",
    #     target_role="button",
    #     target_name="Log In",
    #     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36", 
    #     browser_args=['--disable-blink-features=AutomationControlled'],
    #     viewport_width=1920,  # Browser viewport width
    #     viewport_height=1080,
    #     headless=True,
    #     wait_until="domcontentloaded",  # Wait condition for page navigation
    #     java_script_enabled=True,
    #     timeout=10000,  # Timeout for page load and wait operations
    #     cursor_enabled=True

    # )
    
#     main(
#         url='http://127.0.0.1:8000/',
#         action_type="move_and_type",
#         #target_role="button",
#         #target_name="Log In",
#         css_selector="#id_username",
#         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36", 
#         browser_args=['--disable-blink-features=AutomationControlled'],
#         viewport_width=1920,  # Browser viewport width
#         viewport_height=1080,
#         headless=False,
#         text="your mom",
#         wait_until="domcontentloaded",  # Wait condition for page navigation
#         java_script_enabled=True,
#         timeout=10000,  # Timeout for page load and wait operations
#         cursor_enabled=True
# )

    main(
        url='http://127.0.0.1:8000/',
        action_chain= select_sequence("theom", "theom", "trending", "comment", text="first evaded comment", id=101),
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36", 
        browser_args=['--disable-blink-features=AutomationControlled'],
        viewport_width=1920,  # Browser viewport width
        viewport_height=1080,
        headless=False,
        wait_until="domcontentloaded",  # Wait condition for page navigation
        java_script_enabled=True,
        timeout=10000,  # Timeout for page load and wait operations
        cursor_enabled=True
)

"""

either only use Xpath or accept a locator object instead 
(in the main function for example, and pass that obj to the locate element function) 
of the individual locator things individually. 


right now, you call the function to get the comment id twice, 
once to find the box, and once to find the submit button. 
Problem is, that might result in two different IDs...... so you submit the wrong comment
Also, the scroll is not humanlike enough. its pretty shit...



"""