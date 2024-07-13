from playwright.sync_api import sync_playwright
import pandas as pd
import time
import random

user_data_dir = 'path'

# List of user agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:114.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
]

# For the "business" subject
subject = ("technology", "#ember195")

def login_and_save_state(playwright):
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    url = f'link'
    page = browser.new_page()
    page.goto(url)

    # Perform login steps
    time.sleep(60)

    print("Login state saved.")
    page.close()
    browser.close()

def reuse_saved_state_with_rotating_proxies(playwright):
    data = [] 
    ua = random.choice(user_agents)
    
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        args=['--disable-blink-features=AutomationControlled'],
        user_agent=ua,
    )
    
    new_url = f'topic-link'
    page = browser.new_page()
    page.goto(new_url)
    time.sleep(1)

    i = 500
    scroll_count = 0
    previous_scroll_position = 0
    max_element = 5000
    
    while i <= 1000000:
        page.evaluate(f'window.scrollBy({i}, {i+500})')
        sleep = random.uniform(1, 4)
        time.sleep(sleep)
        scroll_count += 1
        
        # Try to click the "Show More" button and handle the case where it is not visible
        try:
            if page.locator(f'{subject[1]}').is_visible():
                page.click(f'{subject[1]}')
                sleep1 = random.uniform(1, 5)
                time.sleep(sleep1)
        except Exception as e:
            print(f"Exception occurred while trying to click the 'Show More' button: {e}")
        
        topics = page.query_selector_all('//li[@class="topics-body__result-card"]')
        for topic in topics:
            course_name = topic.query_selector('//h3[@class="lls-card-detail-card-body__headline _bodyText_1e5nen _default_1i6ulk _sizeLarge_1e5nen _weightBold_1e5nen"]').inner_text().strip()
            course_link_elem = topic.query_selector('//a[@class="ember-view entity-link"]')
            course_link = 'https://www.examle.com' + course_link_elem.get_attribute('href').strip()

            instructor_elements = topic.query_selector_all('.lls-card-authors .li-i18n-linkto')
            instructor_names = [elem.inner_text().strip() for elem in instructor_elements]

            skill_elems = topic.query_selector_all('.lls-card-skills a[data-trk-control-name="card_skill_link"]')
            skill_names = [elem.inner_text().strip() for elem in skill_elems]

            release_date = topic.query_selector('//span[@class="lls-card-released-on"]').inner_text().strip()

            data.append({
                'Course Link': course_link,
                'Course Title': course_name,
                'Instructors': ', '.join(instructor_names),
                'Skills': ', '.join(skill_names),
                'Published On': release_date
            })
        
        # Check if we have reached the maximum number of elements
        if len(data) >= max_element:
            print(f"Maximum number of records ({max_element}) reached.")
            break

        time.sleep(1)
        if scroll_count >= 6:
            page.evaluate('document.querySelectorAll("li.topics-body__result-card").forEach(el => el.remove());')
            scroll_count = 0
        
        try:
            if page.locator(f'{subject[1]}').is_visible():
                page.click(f'{subject[1]}')
                sleep1 = random.uniform(1, 5)
                time.sleep(sleep1)
        except Exception as e:
            print(f"Exception occurred while trying to click the 'Show More' button: {e}")
        
        current_scroll_position = page.evaluate('window.scrollY')
        if current_scroll_position == previous_scroll_position:
            print("Reached the end of the page or scroll position stalled.")
            break
        
        previous_scroll_position = current_scroll_position  
    
    df = pd.DataFrame(data)
    df.to_excel(f'{subject[0]}links.xlsx', index=False)
    print(f"Data saved to {subject[0]}links.xlsx")                               
    page.close()
    browser.close()

with sync_playwright() as p:
    # Step 1: Log in and save the state
    login_and_save_state(p)
    
    # Step 2: Reuse saved state with rotating proxies and user agents
    reuse_saved_state_with_rotating_proxies(p)
