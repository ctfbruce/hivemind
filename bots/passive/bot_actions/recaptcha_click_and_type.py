from playwright.sync_api import sync_playwright
import math
import random
import time

def main(
    url,
    headers=None,
    user_agent=None,
    browser_args=None,
    action_type="move_and_click",
    target_role=None,
    target_name=None,
    viewport_width=1920,
    viewport_height=1080,
    headless=False,
    wait_until="domcontentloaded",
    css_selector = None,
    text = None,
    java_script_enabled=True,
    timeout=5000,
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
        
        print("idling a bit")
        time.sleep(5)
        page.screenshot(path="headless_debug.png", full_page=True)
        print("Page loaded successfully!")

        # Inject custom JavaScript to display the cursor if enabled
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

        # Locate the target element by role and name
        if target_role and target_name:
            print(f"Locating element with role='{target_role}' and name='{target_name}'...")
            target_element = page.get_by_role(target_role, name=target_name)
        elif css_selector:
            target_element = page.locator(css_selector)
        if target_element:
            # Perform the specified action on the target element
            if action_type in ("move_and_click", "move_and_type"):
                perform_action_on_target(page, target_element, action_type, text)
                page.screenshot(path="afteraction.png", full_page=True)
            else:
                print(f"Unknown action type: {action_type}")
        else:
            print("Target role and name must be provided to locate the element.")

        # Close the browser
        print("Process completed. Closing browser...")
        browser.close()


def perform_action_on_target(page, target_element, action_type, text=None):
    """
    Perform a specified action (move_and_click or move_and_type) on the target element.
    """
    bounding_box = target_element.bounding_box()
    if bounding_box:
        # Target coordinates
        target_x = bounding_box["x"] + bounding_box["width"] / 2
        target_y = bounding_box["y"] + bounding_box["height"] / 2

        # Perform pronounced random movements to simulate human behavior
        random_mouse_movements_to_target(page, 960, 540, target_x, target_y)

        page.screenshot(path="ontarget.png", full_page=True)

        # Perform the desired action
        if action_type == "move_and_click":
            page.mouse.click(target_x, target_y)
            print("Click performed successfully.")
        elif action_type == "move_and_type":
            page.mouse.click(target_x, target_y)
            for char in text:
                page.keyboard.type(char)
                delay = random.uniform(0.05, 0.3)  # Random delay between 50ms and 300ms
                time.sleep(delay)
            print("Typing performed successfully.")
    else:
        print("Could not determine bounding box for the target element.")


    """
    Perform the move_and_type action, typing each character of the text
    into the target element at random intervals to simulate human-like typing.
    """
    

        # Type each character with a random delay
    for char in text:
        page.keyboard.type(char)
        delay = random.uniform(0.05, 0.3)  # Random delay between 50ms and 300ms
        time.sleep(delay)






def random_mouse_movements_to_target(page, start_x, start_y, target_x, target_y):
    """
    Simulate pronounced, human-like mouse movements starting from the center of the screen
    and covering a wide area before reaching the target.
    """
    print("Simulating pronounced random mouse movements to the target...")
    steps = 10  # Total steps for the movement
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
    print("Adding sharp random movements near the target...")
    for _ in range(15):
        sharp_x = target_x + random.uniform(-50, 50)
        sharp_y = target_y + random.uniform(-50, 50)
        page.mouse.move(sharp_x, sharp_y, steps=random.randint(3, 10))
        time.sleep(random.uniform(0.01, 0.03))

    # Final precise movement to the target position
    page.mouse.move(target_x, target_y, steps=random.randint(8, 15))
    print("Mouse movement to the target completed.")


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
    
    main(
        url='http://127.0.0.1:8000/',
        action_type="move_and_type",
        #target_role="button",
        #target_name="Log In",
        css_selector="#id_username",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36", 
        browser_args=['--disable-blink-features=AutomationControlled'],
        viewport_width=1920,  # Browser viewport width
        viewport_height=1080,
        headless=False,
        text="your mom",
        wait_until="domcontentloaded",  # Wait condition for page navigation
        java_script_enabled=True,
        timeout=10000,  # Timeout for page load and wait operations
        cursor_enabled=True
)

""" the way this could work, is that you pass an array of actions, and it'll execute those because atm if you make diff calls, it resets each time"""