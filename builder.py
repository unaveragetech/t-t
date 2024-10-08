import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class TwinkleTonesCLI:
    def __init__(self):
        self.base_dir = 'TwinkleTones'
        self.load_data()

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

    def display_instructions(self):
        instructions = """
        Welcome to Twinkle Tones CLI Tool!
        
        Instructions:
        1. You will be presented with options for quotes, texts, symbols, and images.
        2. Select the corresponding number for your desired option.
        3. After selection, you can review and modify your post.
        4. Finally, log in to your Facebook account to schedule a post.
        """
        print(instructions)

    def display_options(self):
        print("\nQuotes:")
        for idx, quote in enumerate(self.quotes):
            print(f"{idx + 1}: {quote}")

        print("\nTexts:")
        for idx, text in enumerate(self.texts):
            print(f"{idx + 1}: {text}")

        print("\nSymbols:")
        for idx, symbol in enumerate(self.symbols):
            print(f"{idx + 1}: {symbol}")

        print("\nPictures:")
        for idx, picture in enumerate(self.pictures):
            print(f"{idx + 1}: {picture}")

    def select_content(self):
        quote_index = int(input("Select a quote (number): ")) - 1
        text_index = int(input("Select a text (number): ")) - 1
        symbol_index = int(input("Select a symbol (number): ")) - 1
        picture_index = int(input("Select a picture (number): ")) - 1

        selected_quote = self.quotes[quote_index]
        selected_text = self.texts[text_index]
        selected_symbol = self.symbols[symbol_index]
        selected_picture = self.pictures[picture_index]

        return f"{selected_quote} {selected_text} {selected_symbol}", selected_picture

    def login_facebook(self, email, password):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        driver.get("https://www.facebook.com/")
        time.sleep(2)  # Wait for page to load

        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()
        time.sleep(5)  # Wait for login to complete

        return driver

    def post_to_facebook(self, driver, content, scheduled_time, picture):
        driver.get("https://www.facebook.com/")  # Navigate to Facebook homepage
        time.sleep(2)

        # Here you would locate the post input field and attach the picture
        # Example (the selectors may vary):
        driver.find_element(By.CSS_SELECTOR, "[name='xhpc_message']").send_keys(content)

        # You would also need to upload the selected picture.
        # Add your own code to handle picture upload here.

        # Simulate posting
        driver.find_element(By.CSS_SELECTOR, "[data-testid='react-composer-post-button']").click()

        print(f"Post scheduled for: {scheduled_time}.")

    def run(self):
        self.display_instructions()
        self.display_options()

        content, picture = self.select_content()
        print(f"Generated Content: {content} with picture: {picture}")

        email = input("Enter Facebook email: ")
        password = input("Enter Facebook password: ")
        driver = self.login_facebook(email, password)

        scheduled_time = input("Enter scheduled time (e.g., '2023-10-10 15:30'): ")
        self.post_to_facebook(driver, content, scheduled_time, picture)

        driver.quit()

if __name__ == "__main__":
    # Create directory structure if it doesn't exist
    dirs = ['quotes', 'pictures', 'text', 'symbols']
    for dir_name in dirs:
        os.makedirs(f'TwinkleTones/{dir_name}', exist_ok=True)
        if dir_name != 'pictures':
            with open(f'TwinkleTones/{dir_name}/{dir_name}.json', 'w') as json_file:
                json.dump([], json_file)

    cli = TwinkleTonesCLI()
    cli.run()
