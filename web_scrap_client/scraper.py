from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from datetime import datetime, date
import re
import time
import sys

def parse_relative_date(date_str: str) -> date:
    today = date.today()
    date_str = date_str.strip()
    
    # 2024년 1월 28일
    match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', date_str)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    # 2024. 1. 28.
    match = re.search(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})', date_str)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    if '전' in date_str or 'ago' in date_str:
         return today
         
    print(f"Warning: Could not parse date '{date_str}', fallback to today.")
    return today

def fetch_reviews(app_id: str, target_date: date, lang: str = 'ko', country: str = 'kr') -> list:
    url = f"https://play.google.com/store/apps/details?id={app_id}&hl={lang}&gl={country}"
    
    # print(f"Initializing Selenium to fetch {url}...")

    chrome_options = Options()
    chrome_options.add_argument("--headless") # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Add fake user agent to avoid being blocked slightly less
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Failed to initialize Chrome Driver: {e}")
        return []

    parsed_reviews = []

    try:
        driver.get(url)
        
        # 1. Click "See all reviews" button
        # print("Looking for 'See all reviews' button...")
        
        # Wait for button
        wait = WebDriverWait(driver, 10)
        
        buttons = driver.find_elements(By.CSS_SELECTOR, "button.VfPpkd-Bz112c-LgbsSe.yHy1rc.eT1oJ.QDwDD.mN1ivc.VxpoF")
        
        review_button = None
        for btn in buttons:
            txt = btn.text
            aria = btn.get_attribute("aria-label")
            if (txt and "리뷰" in txt) or (aria and "리뷰" in aria) or (aria and "reviews" in aria.lower()):
                review_button = btn
                break
        
        if not review_button:
            if buttons:
                review_button = buttons[-1] # Fallback to last button of this class

        if review_button:
            # print(f"Clicking button: {review_button.text or 'Icon Button'}")
            driver.execute_script("arguments[0].click();", review_button)
            
            # 2. Wait for Modal
            # print("Waiting for modal...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.jgIq1")))
            
            # Allow some time for content load
            time.sleep(2) 
            
            # 3. Find Review Items
            review_items = driver.find_elements(By.CSS_SELECTOR, "div.RHo1pe")
            
            for item in review_items:
                try:
                    # Date: .bp9Aid
                    date_elem = item.find_element(By.CSS_SELECTOR, ".bp9Aid")
                    date_text = date_elem.text
                    
                    # Content: .h3YV2d
                    content_text = ""
                    try:
                        content_elem = item.find_element(By.CSS_SELECTOR, ".h3YV2d")
                        content_text = content_elem.text
                    except:
                        content_text = item.text


                    # Username
                    user_name = "User"
                    try:
                        user_elem = item.find_element(By.CSS_SELECTOR, ".X43Kjb")
                        user_name = user_elem.text
                    except:
                        pass

                    review_date = parse_relative_date(date_text)
                    
                    # [User Request] Removed scraping logs
                    # print(f"[Scraped Item] Date: {review_date} ({date_text}) | User: {user_name} | Content: {content_text[:50]}...")

                    if review_date >= target_date:
                        parsed_reviews.append({
                            'userName': user_name,
                            'at': datetime.combine(review_date, datetime.min.time()),
                            'score': 5,
                            'content': content_text
                        })
                except Exception as e:
                    # Silence parsing errors unless critical
                    continue

        else:
            print("Button not found.")

    except Exception as e:
        print(f"Selenium Error: {e}")
    finally:
        driver.quit()

    return parsed_reviews
