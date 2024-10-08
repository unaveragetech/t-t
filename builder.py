import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from apscheduler.schedulers.background import BackgroundScheduler
from getpass import getpass
import logging
import random

class TwinkleTonesCLI:
    def __init__(self):
        self.base_dir = 'TwinkleTones'
        self.load_data()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_data(self):
        self.quotes = self.load_json('quotes/quotes.json')
        self.texts = self.load_json('text/text.json')
        self.symbols = self.load_json('symbols/symbols.json')
        self.pictures = self.load_pictures()

    def load_json(self, filename):
        try:
            with open(os.path.join(self.base_dir, filename)) as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print(f"File not found: {filename}. Please ensure it exists.")
            return []

    def load_pictures(self):
        pictures_dir = os.path.join(self.base_dir, 'pictures')
        return [f for f in os.listdir(pictures_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    def configure_post_type(self):
        print("\nPost Type Selection:")
        print("1. Quote")
        print("2. Text")
        print("3. Symbol")
        print("4. Picture")
        print("5. All")
        selected_type = input("Select the post type (number): ")

        allowed_content = {}
        if selected_type == '1' or selected_type == '5':
            allowed_content['quotes'] = self.quotes
        if selected_type == '2' or selected_type == '5':
            allowed_content['texts'] = self.texts
        if selected_type == '3' or selected_type == '5':
            allowed_content['symbols'] = self.symbols
        if selected_type == '4' or selected_type == '5':
            allowed_content['pictures'] = self.pictures
        
        return allowed_content

    def auto_generate_post(self, allowed_content):
        # Create post based on allowed content types
        selected_quote = random.choice(allowed_content['quotes']) if 'quotes' in allowed_content and allowed_content['quotes'] else ""
        selected_text = random.choice(allowed_content['texts']) if 'texts' in allowed_content and allowed_content['texts'] else ""
        selected_symbol = random.choice(allowed_content['symbols']) if 'symbols' in allowed_content and allowed_content['symbols'] else ""
        selected_picture = random.choice(allowed_content['pictures']) if 'pictures' in allowed_content and allowed_content['pictures'] else None

        content = f"{selected_quote} {selected_text} {selected_symbol}"
        return content, selected_picture

    def save_auto_post(self, content, picture):
        post_data = {"content": content, "picture": picture}
        with open(os.path.join(self.base_dir, 'auto_posts.json'), 'a') as file:
            json.dump(post_data, file)
            file.write("\n")
        print("Auto-generated post saved.")

    def login_facebook(self, email, password):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        driver.get("https://www.facebook.com/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))

        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Account']")))
        time.sleep(3)  # Wait for login to complete

        return driver

    def post_to_facebook(self, driver, content, picture):
        driver.get("https://www.facebook.com/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[role='textbox']")))

        post_box = driver.find_element(By.CSS_SELECTOR, "[role='textbox']")
        post_box.send_keys(content)

        if picture:
            upload_element = driver.find_element(By.CSS_SELECTOR, "[type='file']")
            upload_element.send_keys(os.path.join(self.base_dir, 'pictures', picture))

        driver.find_element(By.CSS_SELECTOR, "[data-testid='react-composer-post-button']").click()
        logging.info("Post successfully made.")

    def read_facebook_notifications(self, driver):
        driver.get("https://www.facebook.com/notifications")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[role='feed']")))

        notifications = driver.find_elements(By.CSS_SELECTOR, "[role='feed'] [aria-live='polite']")
        notification_list = [notification.text for notification in notifications]

        # Save notifications to a file
        with open(os.path.join(self.base_dir, 'notifications.json'), 'w') as file:
            json.dump(notification_list, file)

        print(f"Notifications saved: {len(notification_list)} items.")

    def schedule_post(self, email, password, content, picture, scheduled_time):
        logging.info(f"Scheduling post for {scheduled_time}")
        self.scheduler.add_job(self.execute_post, 'date', run_date=scheduled_time, args=[email, password, content, picture])

    def execute_post(self, email, password, content, picture):
        driver = self.login_facebook(email, password)
        self.post_to_facebook(driver, content, picture)
        driver.quit()
        logging.info("Post successfully made.")

    def run_auto_posting(self, allowed_content):
        # Auto-generate and save posts at a regular interval (e.g., daily or weekly)
        content, picture = self.auto_generate_post(allowed_content)
        self.save_auto_post(content, picture)
        logging.info(f"Auto-post created: {content}")

    def run(self):
        auto_mode = input("Run in auto mode? (yes/no): ").lower()
        if auto_mode == 'yes':
            allowed_content = self.configure_post_type()
            interval = input("Enter auto-post interval in hours (e.g., 24 for daily): ")
            self.scheduler.add_job(self.run_auto_posting, 'interval', hours=int(interval), args=[allowed_content])

        else:
            allowed_content = self.configure_post_type()
            content, picture = self.auto_generate_post(allowed_content)
            print(f"Generated Content: {content} with picture: {picture}")

            email = input("Enter Facebook email: ")
            password = getpass("Enter Facebook password: ")

            scheduled_time = input("Enter scheduled time (e.g., '2024-10-10 15:30'): ")
            self.schedule_post(email, password, content, picture, scheduled_time)

            driver = self.login_facebook(email, password)
            self.read_facebook_notifications(driver)
            driver.quit()


if __name__ == "__main__":
    # Ensure directory structure exists
    dirs = ['quotes', 'pictures', 'text', 'symbols']
    for dir_name in dirs:
        os.makedirs(f'TwinkleTones/{dir_name}', exist_ok=True)
        if dir_name != 'pictures':
            with open(f'TwinkleTones/{dir_name}/{dir_name}.json', 'w') as json_file:
                json.dump([], json_file)

    cli = TwinkleTonesCLI()
    cli.run()
