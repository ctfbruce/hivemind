import math
import random
import time
import asyncio

# Import necessary Playwright modules
from playwright.async_api import Page, Locator

async def standard_log_in(page: Page, username: str, password: str):
    action_chain = [
        {
            "action": "move_and_type",
            "css_selector": "#id_username",
            "text": username
        },
        {
            "action": "move_and_type",
            "css_selector": "#id_password",
            "text": password
        },
        {
            "action": "move_and_click",
            "target_role": "button",
            "target_name": "Log In"
        },
    ]
    for action in action_chain:
        target_element = await locate_target(
            page,
            css_selector=action.get("css_selector"),
            target_name=action.get("target_name"),
            target_role=action.get("target_role"),
            xpath=action.get("xpath"),
        )
        await perform_action_on_target(
            page,
            target_element,
            action_type=action["action"],
            text=action.get("text")
        )
    await page.wait_for_timeout(1000)  # Wait for 1 second

async def nav_to_post(page: Page, tab: str, css_selector=None, xpath=None):
    print("Trying to navigate to post...")
    tab_selector = f"#{tab}-tab"
    await page.click(tab_selector)
    print("Successfully navigated to tab, now scrolling...")

    if css_selector:
        target_element = await locate_target(page, css_selector=css_selector)
    elif xpath:
        target_element = await locate_target(page, xpath=xpath)
    else:
        raise ValueError("No selector provided for target element")

    await human_like_scroll_to_element(page, target_element)
    print("Successfully scrolled to element.")

async def human_like_scroll_to_element(page: Page, target_element: Locator):
    """
    Scrolls the page to the target element in a human-like fashion.
    """

    # Get the target element's position using JavaScript
    element_position = await target_element.evaluate("""
        (element) => {
            const rect = element.getBoundingClientRect();
            return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
        }
    """)

    if not element_position:
        print("Could not determine position for the target element.")
        raise Exception("Element position is None.")

    target_y = element_position['y'] + element_position['height'] / 2

    # Get the current scroll position
    current_scroll_position = await page.evaluate("() => window.scrollY")

    # Calculate the total scroll distance
    total_scroll_distance = target_y - current_scroll_position

    # Define scrolling parameters
    average_step_size = 100  # Average pixels to scroll each step
    step_size_variability = 50  # Variability in step size
    min_delay = 0.05  # Minimum delay between scroll steps (in seconds)
    max_delay = 0.2   # Maximum delay between scroll steps (in seconds)

    # Determine the direction of scrolling
    scroll_direction = 1 if total_scroll_distance > 0 else -1

    scrolled_distance = 0

    # Scroll in steps until we reach or pass the target position
    while abs(scrolled_distance) < abs(total_scroll_distance):
        # Calculate a random step size
        step_size = random.randint(
            average_step_size - step_size_variability,
            average_step_size + step_size_variability
        )

        # Ensure we don't scroll past the target
        remaining_distance = abs(total_scroll_distance) - abs(scrolled_distance)
        if step_size > remaining_distance:
            step_size = remaining_distance

        # Scroll by the step size
        await page.evaluate(f"window.scrollBy(0, {scroll_direction * step_size})")
        scrolled_distance += scroll_direction * step_size

        # Random delay between steps to mimic human scrolling speed variability
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)

async def locate_target(page: Page, css_selector=None, target_role=None, target_name=None, xpath=None) -> Locator:
    # Locate the target element by role and name
    if target_role and target_name:
        print(f"Locating element with role='{target_role}' and name='{target_name}'...")
        target_element = page.get_by_role(target_role, name=target_name)
    elif xpath:
        target_element = page.locator("xpath="+xpath)
    elif css_selector:
        target_element = page.locator(css_selector)
    else:
        raise ValueError("No valid selector provided")

    # Wait for the element to be visible
    await target_element.wait_for(state="visible", timeout=10000)
    return target_element

async def perform_action_on_target(page: Page, target_element: Locator, action_type: str, text=None):
    """
    Perform a specified action (move_and_click or move_and_type) on the target element.
    """

    # Scroll element into view if needed
    await target_element.scroll_into_view_if_needed()

    # Perform the desired action
    if action_type == "move_and_click":
        await human_like_mouse_move_to_element(page, target_element)
        await target_element.click()
        print("Click performed successfully.")
    elif action_type == "move_and_type":
        await human_like_mouse_move_to_element(page, target_element)
        await target_element.click()
        await human_like_type(page, text)
        print("Typing performed successfully.")
    else:
        raise KeyError("Unidentified action type")

async def human_like_mouse_move_to_element(page: Page, target_element: Locator):
    """
    Simulate human-like mouse movements to the target element.
    """

    # Get the current mouse position (assuming starting from center)
    viewport_size = page.viewport_size
    if not viewport_size:
        viewport_size = {'width': 1280, 'height': 720}  # Default size

    start_x = viewport_size['width'] / 2
    start_y = viewport_size['height'] / 2

    # Get the target element's position
    element_position = await target_element.evaluate("""
        (element) => {
            const rect = element.getBoundingClientRect();
            return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
        }
    """)

    if not element_position:
        print("Could not determine position for the target element.")
        raise Exception("Element position is None.")

    target_x = element_position['x']
    target_y = element_position['y']

    # Simulate pronounced random movements to the target
    await random_mouse_movements_to_target(page, start_x, start_y, target_x, target_y)

async def random_mouse_movements_to_target(page: Page, start_x, start_y, target_x, target_y):
    """
    Simulate pronounced, human-like mouse movements starting from the current position
    and moving to the target.
    """

    steps = random.randint(10, 20)  # Total steps for the movement
    duration = random.uniform(0.5, 1.5)  # Total duration in seconds

    # Generate intermediate points using Bezier curves
    control_points = generate_bezier_control_points(start_x, start_y, target_x, target_y)

    path = compute_bezier_path(control_points, steps)

    # Move the mouse along the path
    for point in path:
        await page.mouse.move(point[0], point[1])
        await asyncio.sleep(duration / steps)

async def human_like_type(page: Page, text: str):
    """
    Simulate human-like typing with random delays between keystrokes.
    """
    for char in text:
        await page.keyboard.type(char)
        delay = random.uniform(0.05, 0.3)  # Random delay between 50ms and 300ms
        await asyncio.sleep(delay)

def generate_bezier_control_points(start_x, start_y, target_x, target_y):
    """
    Generate control points for a Bezier curve between the start and target positions.
    """
    cp1_x = start_x + (target_x - start_x) * random.uniform(0.25, 0.5)
    cp1_y = start_y + (target_y - start_y) * random.uniform(0.1, 0.3)

    cp2_x = start_x + (target_x - start_x) * random.uniform(0.5, 0.75)
    cp2_y = start_y + (target_y - start_y) * random.uniform(0.7, 0.9)

    return [(start_x, start_y), (cp1_x, cp1_y), (cp2_x, cp2_y), (target_x, target_y)]

def compute_bezier_path(control_points, steps):
    """
    Compute points along a cubic Bezier curve defined by the control points.
    """
    path = []
    for t in [i / steps for i in range(steps + 1)]:
        x = (
            (1 - t) ** 3 * control_points[0][0] +
            3 * (1 - t) ** 2 * t * control_points[1][0] +
            3 * (1 - t) * t ** 2 * control_points[2][0] +
            t ** 3 * control_points[3][0]
        )
        y = (
            (1 - t) ** 3 * control_points[0][1] +
            3 * (1 - t) ** 2 * t * control_points[1][1] +
            3 * (1 - t) * t ** 2 * control_points[2][1] +
            t ** 3 * control_points[3][1]
        )
        path.append((x, y))
    return path

async def select_random_post(page: Page, tab: str):
    if tab == "discover":
        tab_id = "[aria-labelledby=discover-tab] > div"
    elif tab == "trending":
        tab_id = "[aria-labelledby=trending-tab] > div > div"
    else:
        raise ValueError(f"Invalid tab name: {tab}")

    print("Selecting random post...")

    posts = await page.query_selector_all(tab_id)

    post_count = len(posts)

    if post_count == 0:
        raise Exception(f"No posts found under the tab.")

    # Randomly select a post
    selected_index = random.randint(0, post_count - 1)
    selected_post = posts[selected_index]
    return selected_post
