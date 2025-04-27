import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def get_pakistan_trending_searches(region):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        url = f"https://trends.google.com/trends/trendingsearches/daily?geo={region}"
        print(f"Navigating to: {url}")
        driver.get(url)
        
        print("Waiting for content to load...")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "DEQ5Hc")))
        time.sleep(2)  
        
        print("Extracting trending search data...")
        trending_searches = []
        soup = BeautifulSoup(driver.page_source, "html.parser")
        trends = soup.find_all(class_="mZ3RIc")
        for trend in trends:
            search_term = trend.get_text()
            traffic = trend.find_next(class_="lqv0Cb").get_text()
            trending_searches.append({"search_term": search_term, "traffic": traffic})
        
        df = pd.DataFrame(trending_searches)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #filename = f"pakistan_trending_searches_{timestamp}.csv"
        #df.to_csv(filename, index=False)
        #print(f"Data saved to {filename}")
        
        return df
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()
    
    finally:
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    trends_df = get_pakistan_trending_searches()