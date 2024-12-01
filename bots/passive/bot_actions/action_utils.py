import math
import random
import time

def standard_log_in(page, username, password):
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
    action_chain = [{"action":"move_and_type", "target_role":None,"target_name":None, "css_selector":"#id_username", "xpath":None, "text":username},
                {"action":"move_and_type", "target_role":None,"target_name":None, "css_selector":"#id_password", "xpath":None, "text":password},
                {"action":"move_and_click", "target_role":"button","target_name":"Log In", "css_selector":None, "xpath":None, "text":None},]
    for action in action_chain:
        target_element = locate_target(page, css_selector=action["css_selector"], target_name=action["target_name"],target_role=action["target_role"], xpath=action["xpath"])
        perform_action_on_target(page, target_element, action_type=action["action"], text=action["text"])
    time.sleep(1)

def nav_to_post(page, tab, css_selector=None, xpath=None):
    # if tab in ("trending", "recommended"):
    #     css_selector = f"#{tab}-posts-container form[action='/comments/add/{id}/'] textarea"
    # elif tab in ("discover"):
    #     css_selector = f"#discover form[action='/comments/add/{id}/'] textarea"
      
    action_chain = [{"action":"move_and_click", "target_role":None,"target_name":None, "css_selector":f"#{tab}-tab", "xpath":None, "text":None},
                    {"action":"move_and_click", "target_role":None,"target_name":None, "css_selector":css_selector, "xpath":xpath, "text":None},]
    # for action in action_chain:
    #     target_element = locate_target(page, css_selector=action["css_selector"], target_name=action["target_name"],target_role=action["target_role"], xpath=action["xpath"])
    #     perform_action_on_target(page, target_element, action_type=action["action"], text=action["text"])
    #     time.sleep(1)
    
    print("trying to nav to post")
    perform_action_on_target(page, 
                             locate_target(page, css_selector=action_chain[0]["css_selector"], target_name=action_chain[0]["target_name"],target_role=action_chain[0]["target_role"], xpath=action_chain[0]["xpath"]), 
                             action_type=action_chain[0]["action"], text=action_chain[0]["text"])
    time.sleep(1)
    
    print("successfully navigated, now going to scroll")
    human_like_scroll_to_element(page,
                                locate_target(page, css_selector=action_chain[1]["css_selector"], target_name=action_chain[1]["target_name"],target_role=action_chain[1]["target_role"], xpath=action_chain[1]["xpath"]))
    
    print("successfully scrolled")
    # perform_action_on_target(page, 
    #                          locate_target(page, css_selector=action_chain[1]["css_selector"], target_name=action_chain[1]["target_name"],target_role=action_chain[1]["target_role"], xpath=action_chain[1]["xpath"]), 
    #                          action_type=action_chain[1]["action"], text=action_chain[1]["text"])
    
        
        
def human_like_scroll_to_element(page, target_element):
    """
    Scrolls the page from the top to the target element in a human-like fashion.
    """
    page.evaluate("window.scrollTo(0, 0)")  # Start from the top of the page

    # Get the target element's position
    bounding_box = target_element.bounding_box()
    if not bounding_box:
        print("Could not determine bounding box for the target element. In HS")
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

def perform_action_on_target(page, target_element, action_type, text=None):
    """
    Perform a specified action (move_and_click or move_and_type) on the target element.
    """


    bounding_box = target_element.bounding_box()
    if bounding_box:
        print("valid target looks like", target_element)
        # Target coordinates
        target_x = bounding_box["x"] + bounding_box["width"] / 2
        target_y = bounding_box["y"] + bounding_box["height"] / 2

        # Perform pronounced random movements to simulate human behavior
        random_mouse_movements_to_target(page, 960, 540, target_x, target_y)





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
        if target_element:
            print("Could not determine bounding box for the target element. in PA")
            print("target was", target_element)
        else:
            print("no target element given")
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

def select_random_post(page, tab):
    if tab == "discover": tab_id = "[aria-labelledby=discover-tab]> div"
    elif tab == "trending": tab_id = "[aria-labelledby=trending-tab] > div > div"
    
    print("made it here")
    posts = page.query_selector_all(tab_id)

    print("made it past first query call")
    post_count = len(posts)

    if post_count == 0:
        raise Exception(f"No posts found under the tab.")

    # Randomly select a post
    selected_index = random.randint(0, post_count - 1)
    selected_post = posts[selected_index]
    return selected_post