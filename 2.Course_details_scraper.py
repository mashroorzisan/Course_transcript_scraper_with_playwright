from playwright.sync_api import sync_playwright
import pandas as pd
import time
import random
import os


user_data_dir = 'path'

# List of user agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:114.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
]

def load_index_from_excel(filename):
    if os.path.exists(filename):
        df = pd.read_excel(filename)
        if 'Course Index' in df.columns:
            return df['Course Index'].max() + 1
    return 0

def scrape_url(page, data, scraped_urls, url, course_index):
    try:
        if url in scraped_urls:
            return False  # Skip already scraped URLs

        # Extracting course title
        course_title_elem = page.query_selector('div.classroom-nav__details h1.classroom-nav__title')
        course_title = course_title_elem.inner_text().strip() if course_title_elem else 'N/A'

        # Extracting instructor profile link
        profile = page.query_selector('.ember-view .instructor__link').get_attribute('href').strip()
        profile = 'https://www.example.com' + profile

        # Extracting instructor thumbnail
        thumb = page.query_selector('//img[@class="_entity_shcpvh _person_shcpvh _large_shcpvh"]').get_attribute('src')

        # Extracting course level
        level_elem = page.query_selector('//div[@class="classroom-workspace-overview__header"]//li[2]')
        level = level_elem.inner_text().strip() if level_elem else 'N/A'

        # Extracting course release date
        date_elem = page.query_selector('//div[@class="classroom-workspace-overview__header"]//li[3]')
        date = date_elem.inner_text().split(':')[1].strip() if date_elem else 'N/A'

        # Extracting course details
        details_elem = page.query_selector('//div[contains(@class, "classroom-workspace-overview__description")]')
        details = details_elem.inner_text() if details_elem else 'N/A'

        # Extracting instructor name
        instructor_elem = page.query_selector('div.instructor__name._bodyText_1e5nen._default_1i6ulk._sizeMedium_1e5nen')
        instructor_name = instructor_elem.inner_text().strip() if instructor_elem else 'N/A'

        # Extracting videos and quizzes
        sections = page.query_selector_all(
            'div.classroom-layout-sidebar-body[class*="classroom-body__sidebar-body"] section.classroom-toc-section')

        course_data = []  # Temporarily store data related to this course
        transcript_found = False  # Flag to track if any transcript is found

        for section in sections:
            # Get the section title
            section_title = section.query_selector('h2 .classroom-toc-section__toggle-title').inner_text().strip()

            # Get all video items in the section
            video_items = section.query_selector_all('ul.classroom-toc-section__items li')

            for video_item in video_items:
                j = 0 
                # Extract video title and duration or quiz information
                title_elem = video_item.query_selector('div.classroom-toc-item__title')
                title = title_elem.inner_text().strip() if title_elem else 'N/A'

                duration_elem = video_item.query_selector(
                    'div._bodyText_1e5nen._default_1i6ulk._sizeXSmall_1e5nen._lowEmphasis_1i6ulk span')
                duration = duration_elem.inner_text().strip() if duration_elem else 'N/A'

                # Extract the video or quiz link
                link_elem = video_item.query_selector('a.classroom-toc-item__link')
                video_link = link_elem.get_attribute('href').strip() if link_elem else 'N/A'
                video_link = f'https://www.example.com{video_link}' if video_link != 'N/A' else 'N/A'

                if "Chapter Quiz" in title:
                    course_data.append({
                        'Course Index': course_index,
                        'Course Link': url,
                        'Course Title': course_title,
                        'Instructor Name': instructor_name,
                        'Instructor Profile': profile,
                        'Instructor Thumbnail': thumb,
                        'Released Date': date,
                        'Level': level,
                        'Course Details': details,
                        'Section': section_title,
                        'Quiz Title': title,
                        'Quiz Link': video_link
                    })
                else:
                    transcript = ''
                    # Click on the video link to potentially play the video or interact with it
                    try:
                        link_elem.click()
                        time.sleep(random.uniform(2,4))
                        
                        if j == 0:
                            if page.locator('//button[@data-live-test-classroom-layout-tab="TRANSCRIPT"]').is_visible():
                                page.locator('//button[@data-live-test-classroom-layout-tab="TRANSCRIPT"]').click()
                                time.sleep(random.uniform(1,2))
                                j = 1

                        # Extract transcript without anchor tags
                        transcript = page.evaluate('''
                            () => {
                                const lines = document.querySelectorAll('div.classroom-transcript__lines a')
                                return Array.from(lines).map(line => line.innerText).join(' ')
                            }
                        ''')

                    except Exception as e:
                        print(f"Error clicking on video link for {title}: {e}")

                    # Only append the data if the transcript is not empty
                    if transcript:
                        transcript_found = True  # Mark that we found a transcript
                        course_data.append({
                            'Course Index': course_index,
                            'Course Link': url,
                            'Course Title': course_title,
                            'Instructor Name': instructor_name,
                            'Instructor Profile': profile,
                            'Instructor Thumbnail': thumb,
                            'Released Date': date,
                            'Level': level,
                            'Course Details': details,
                            'Section': section_title,
                            'Video Title': title,
                            'Video Link': video_link,
                            'Video Duration': duration,
                            'Transcript': transcript
                        })

        if transcript_found:
            data.extend(course_data)  # Only add course data if a transcript was found

        scraped_urls.add(url)  # Add to the set of scraped URLs

        return True
    except Exception as e:
        print(f"Error scraping URL: {e}")
        return False

def vid_scraper(playwright, url, data, scraped_urls, course_index):
    ua = random.choice(user_agents)

    browser = playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        args=['--disable-blink-features=AutomationControlled'],
        user_agent=ua,
    )
    
    page = browser.new_page()
    success = False
    try:
        page.goto(url)
        time.sleep(random.uniform(1,2))  # Adjust the sleep time as needed
        success = scrape_url(page, data, scraped_urls, url, course_index)  # scrape url
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    finally:
        page.close()
        browser.close()
    return success

def save_data(filename, data):
    # Check if the file exists
    if os.path.exists(filename):
        # Load existing data
        existing_df = pd.read_excel(filename)
        # Convert the current data to a DataFrame and append to existing data
        new_df = pd.DataFrame(data)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        # If the file doesn't exist, just use the current data
        combined_df = pd.DataFrame(data)
    
    # Save the combined data to the file
    combined_df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

def main(start_index, end_index, filename):
    data = []  # Initialize data list inside the function
    scraped_urls = set()  # Set to keep track of scraped URLs
    error_count = 0  # Initialize error counter

    file_path = 'excellinks.xlsx'
    df = pd.read_excel(file_path)

    column_name = 'Course Link'
    course_index = load_index_from_excel(filename)  

    with sync_playwright() as p:
        for i, url in enumerate(df[column_name][start_index:end_index]):
            try:
                time.sleep(random.uniform(1,2))  # Random delay between requests
                success = vid_scraper(p, url, data, scraped_urls, course_index)
                if success:
                    print(f'{i + start_index} - {df["Course Title"].iloc[i + start_index]}')
                    course_index += 1  # Increment course index after each successful course
                    error_count = 0  # Reset error count after successful scrape
                else:
                    error_count += 1  # Increment error count on failure
                    print(f"Error count: {error_count}")

                # Save data periodically to avoid losing progress
                if i % 5 == 0:  # Save every 10 URLs
                    save_data(filename, data)
                    data.clear()  # Clear data after saving

                # Break out of the loop if the same problem continues for 3 times
                if error_count >= 1:
                    print("Encountered errors for 3 consecutive items, exiting loop.")
                    break

            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                error_count += 1  # Increment error count on exception
                if error_count >= 1:
                    print("Encountered errors for 3 consecutive items, exiting loop.")
                    break

    # Save the collected data to an Excel file
    if data:  # Save remaining data if any
        save_data(filename, data)

def run_main():
    start = 0
    end = 100
    main(start, end+1, 'Scraped_courses.xlsx')


if __name__ == "__main__":
    run_main()
