from pipin import install_requirements
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from apscheduler.schedulers.background import BackgroundScheduler

class TwinkleTonesCLI:
    def __init__(self):
        self.base_dir = 'TwinkleTones'
        self.ensure_directories()
        self.load_data()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def ensure_directories(self):
        """
        Create all the necessary directories if they don't exist.
        """
        directories = ['quotes', 'text', 'symbols', 'deals', 'pictures']
        for directory in directories:
            dir_path = os.path.join(self.base_dir, directory)
            os.makedirs(dir_path, exist_ok=True)

        # Ensure JSON files exist for content directories
        self.ensure_json_file('quotes/quotes.json')
        self.ensure_json_file('text/text.json')
        self.ensure_json_file('symbols/symbols.json')
        self.ensure_json_file('deals/deals.json')

    def ensure_json_file(self, file_path):
        """
        Create a new empty JSON file if it doesn't exist.
        """
        full_path = os.path.join(self.base_dir, file_path)
        if not os.path.exists(full_path):
            with open(full_path, 'w') as file:
                json.dump([], file) if 'deals' not in file_path else json.dump({"deals": []}, file)
            print(f"Created new file: {full_path}")

    def load_data(self):
        self.quotes = self.load_json('quotes/quotes.json')
        self.texts = self.load_json('text/text.json')
        self.symbols = self.load_json('symbols/symbols.json')
        self.deals = self.load_json('deals/deals.json')
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
        3. Optionally, select a product deal to promote.
        4. After selection, review and modify your post.
        5. Finally, log in to your Facebook account to schedule or post directly.
        6. You can also add new content to specific directories.
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

        print("\nDeals:")
        for idx, deal in enumerate(self.deals['deals']):
            print(f"{idx + 1}: {deal['product']} - {deal['price']} ({deal['discount']})")

        print("\nPictures:")
        for idx, picture in enumerate(self.pictures):
            print(f"{idx + 1}: {picture}")

    def prompt_for_new_content(self):
        """
        Prompt the user to add new content if any categories are empty.
        """
        if not self.quotes:
            print("No quotes found. Please add a new quote.")
            self.add_new_content()

        if not self.texts:
            print("No texts found. Please add a new text.")
            self.add_new_content()

        if not self.symbols:
            print("No symbols found. Please add a new symbol.")
            self.add_new_content()

        if not self.deals['deals']:
            print("No deals found. Please add a new deal.")
            self.add_new_content()

        if not self.pictures:
            print("No pictures found. Please add a new picture.")
            self.add_new_content()

    def select_content(self):
        self.prompt_for_new_content()  # Ensure all categories are populated
        print("\nSelect a quote (number):")
        for i, quote in enumerate(self.quotes, 1):
            print(f"{i}. {quote}")
        quote_index = int(input("Enter your selection: ")) - 1  # Convert to 0-based index
        
        if quote_index < 0 or quote_index >= len(self.quotes):
            print("Invalid selection. Please select a valid quote number.")
            return "", None, None  # Return early if selection is invalid

        print("\nSelect a text (number):")
        for i, text in enumerate(self.texts, 1):
            print(f"{i}. {text}")
        text_index = int(input("Enter your selection: ")) - 1
        
        if text_index < 0 or text_index >= len(self.texts):
            print("Invalid selection. Please select a valid text number.")
            return "", None, None

        print("\nSelect a symbol (number):")
        for i, symbol in enumerate(self.symbols, 1):
            print(f"{i}. {symbol}")
        symbol_index = int(input("Enter your selection: ")) - 1
        
        if symbol_index < 0 or symbol_index >= len(self.symbols):
            print("Invalid selection. Please select a valid symbol number.")
            return "", None, None

        deal = None
        use_deal = input("Use a deal? (y/n): ").strip().lower()
        if use_deal == 'y':
            print("\nSelect a deal (number):")
            for i, deal_item in enumerate(self.deals, 1):
                print(f"{i}. {deal_item['name']} - {deal_item['price']} ({deal_item['discount']})")
            deal_index = int(input("Enter your selection (or skip by entering 0): ")) - 1

            if deal_index < 0 or deal_index >= len(self.deals):
                print("Invalid selection. No deal will be used.")
            else:
                deal = self.deals[deal_index]

        picture = None
        print("\nSelect a picture (number):")
        for i, picture_file in enumerate(self.pictures, 1):
            print(f"{i}. {picture_file}")
        picture_index = int(input("Enter your selection: ")) - 1

        if picture_index < 0 or picture_index >= len(self.pictures):
            print("Invalid selection. No picture will be used.")
        else:
            picture = self.pictures[picture_index]

        # Return selected content and deal
        selected_quote = self.quotes[quote_index]
        selected_text = self.texts[text_index]
        selected_symbol = self.symbols[symbol_index]

        return selected_quote, deal, picture


    def add_new_content(self):
        print("\nSelect the type of content to add:")
        print("1. Quote")
        print("2. Text")
        print("3. Symbol")
        print("4. Deal")
        print("5. Picture")
        content_type = input("Enter the number of your selection: ")

        if content_type == '1':
            new_quote = input("Enter the new quote: ")
            self.add_to_json('quotes/quotes.json', new_quote)
        elif content_type == '2':
            new_text = input("Enter the new text: ")
            self.add_to_json('text/text.json', new_text)
        elif content_type == '3':
            new_symbol = input("Enter the new symbol: ")
            self.add_to_json('symbols/symbols.json', new_symbol)
        elif content_type == '4':
            product = input("Enter the product name: ")
            price = input("Enter the price: ")
            discount = input("Enter the discount: ")
            link = input("Enter the product link: ")
            new_deal = {"product": product, "price": price, "discount": discount, "link": link}
            self.add_to_json('deals/deals.json', new_deal, key="deals")
        elif content_type == '5':
            picture_path = input("Enter the path of the picture: ")
            self.add_picture(picture_path)
        else:
            print("Invalid selection!")

    def add_to_json(self, file_path, data, key=None):
        try:
            full_path = os.path.join(self.base_dir, file_path)
            with open(full_path, 'r+') as file:
                json_data = json.load(file)
                if key:
                    json_data[key].append(data)
                else:
                    json_data.append(data)
                file.seek(0)
                json.dump(json_data, file, indent=4)
            print(f"Added new data to {file_path}")
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error adding data to {file_path}. Please check the file and format.")

    def add_picture(self, picture_path):
        if not os.path.exists(picture_path):
            print(f"File not found: {picture_path}")
            return
        if not picture_path.endswith(('.png', '.jpg', '.jpeg')):
            print(f"Invalid file format: {picture_path}. Please upload a .png, .jpg, or .jpeg file.")
            return
        try:
            picture_name = os.path.basename(picture_path)
            destination = os.path.join(self.base_dir, 'pictures', picture_name)
            os.rename(picture_path, destination)
            print(f"Picture successfully added to {destination}")
        except Exception as e:
            print(f"Error adding picture: {e}")

    def login_facebook(self, email, password):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        driver.get("https://www.facebook.com/")
        time.sleep(2)  # Wait for page to load

        try:
            driver.find_element(By.ID, "email").send_keys(email)
            driver.find_element(By.ID, "pass").send_keys(password)
            driver.find_element(By.NAME, "login").click()
            time.sleep(5)  # Wait for login to complete
            if "Facebook" not in driver.title:
                print("Login failed. Please check your credentials.")
                driver.quit()
                return None
            return driver
        except Exception as e:
            print(f"Error during login: {e}")
            driver.quit()
            return None

    def post_to_facebook(self, driver, content, picture):
        # Locate the post box and input content
        driver.find_element(By.XPATH, "//div[contains(@role,'textbox')]").send_keys(content)

        # Attach a picture if provided
        if picture:
            image_input = driver.find_element(By.XPATH, "//input[@type='file']")
            image_input.send_keys(os.path.abspath(os.path.join(self.base_dir, 'pictures', picture)))

        # Post the content
        driver.find_element(By.XPATH, "//button[contains(.,'Post')]").click()
        time.sleep(5)  # Wait for the post to complete
        print("Post submitted successfully!")

    def schedule_post(self, content, deal, picture):
        post_time = input("Enter the time to post (YYYY-MM-DD HH:MM): ")
        self.scheduler.add_job(self.execute_scheduled_post, 'date', run_date=post_time, args=[content, deal, picture])
        print(f"Post scheduled for {post_time}.")

    def execute_scheduled_post(self, content, deal, picture):
        print("Executing scheduled post...")
        email = input("Enter your Facebook email: ")
        password = input("Enter your Facebook password: ")
        driver = self.login_facebook(email, password)

        if driver:
            content_with_deal = self.generate_post_content(content, deal)
            self.post_to_facebook(driver, content_with_deal, picture)
            driver.quit()
        else:
            print("Failed to login for scheduled post.")

    def run(self):
        self.display_instructions()
        while True:
            self.display_options()
            content, deal, picture = self.select_content()
            action = input("Do you want to [1] Post Immediately, [2] Schedule a Post, or [3] Add New Content? ")

            if action == '1':
                email = input("Enter your Facebook email: ")
                password = input("Enter your Facebook password: ")
                driver = self.login_facebook(email, password)

                if driver:
                    content_with_deal = self.generate_post_content(content, deal)
                    self.post_to_facebook(driver, content_with_deal, picture)
                    driver.quit()
                else:
                    print("Failed to login for immediate post.")
            elif action == '2':
                self.schedule_post(content, deal, picture)
            elif action == '3':
                self.add_new_content()
            else:
                print("Invalid selection!")

if __name__ == "__main__":
    install_requirements()  # Ensure required packages are installed
    app = TwinkleTonesCLI()
    app.run()
