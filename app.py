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
        self.load_data()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

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

    def select_content(self):
        quote_index = int(input("Select a quote (number): ")) - 1
        text_index = int(input("Select a text (number): ")) - 1
        symbol_index = int(input("Select a symbol (number): ")) - 1
        deal_index = int(input("Select a deal (number) (or skip by entering 0): ")) - 1 if input("Use a deal? (y/n): ").lower() == 'y' else None
        picture_index = int(input("Select a picture (number): ")) - 1

        selected_quote = self.quotes[quote_index]
        selected_text = self.texts[text_index]
        selected_symbol = self.symbols[symbol_index]
        selected_picture = self.pictures[picture_index]
        selected_deal = self.deals['deals'][deal_index] if deal_index is not None else None

        return f"{selected_quote} {selected_text} {selected_symbol}", selected_deal, selected_picture

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

        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()
        time.sleep(5)  # Wait for login to complete

        return driver

    def generate_post_content(self, content, deal):
        if deal:
            product_info = f"\n📢 Deal Alert! 📢\n\nGet our {deal['product']} now for just {deal['price']}! 🔥 That's {deal['discount']} off the original price.\n\n👉 Buy Now: {deal['link']}\n"
            return content + product_info + f"\n#Discount #BuyNow #{deal['product'].replace(' ', '')}"
        return content

    def post_to_facebook(self, driver, content, scheduled_time, picture):
        driver.get("https://www.facebook.com/")  # Navigate to Facebook homepage
        time.sleep(2)

        # Locate the post input field
        driver.find_element(By.CSS_SELECTOR, "[name='xhpc_message']").send_keys(content)

        # Handle image upload
        image_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='media-attachment-add-photo']")
        image_input.send_keys(os.path.join(self.base_dir, 'pictures', picture))

        # Simulate posting
        driver.find_element(By.CSS_SELECTOR, "[data-testid='react-composer-post-button']").click()

        print(f"Post scheduled for: {scheduled_time}.")

    def save_post(self, content, deal, picture, scheduled_time):
        saved_posts_file = os.path.join(self.base_dir, 'saved_posts.json')
        post = {
            'content': content,
            'deal': deal,
            'picture': picture,
            'scheduled_time': scheduled_time
        }

        try:
            with open(saved_posts_file, 'r+') as file:
                posts = json.load(file)
                posts.append(post)
                file.seek(0)
                json.dump(posts, file, indent=4)
        except FileNotFoundError:
            with open(saved_posts_file, 'w') as file:
                json.dump([post], file, indent=4)
        print(f"Post saved for reuse: {post['content']}")

    def run(self):
        self.display_instructions()

        while True:
            print("\n1. Create and post")
            print("2. Add new content")
            print("3. Exit")

            option = input("Select an option: ")

            if option == '1':
                self.display_options()
                content, deal, picture = self.select_content()
                email = input("Enter your Facebook email: ")
                password = input("Enter your Facebook password: ")

                driver = self.login_facebook(email, password)

                # Post content to Facebook
                post_time = time.strftime("%Y-%m-%d %H:%M:%S")
                post_content = self.generate_post_content(content, deal)
                self.post_to_facebook(driver, post_content, post_time, picture)
                self.save_post(post_content, deal, picture, post_time)

            elif option == '2':
                self.add_new_content()

            elif option == '3':
                print("Exiting...")
                break
            else:
                print("Invalid option. Please select again.")

if __name__ == "__main__":
    app = TwinkleTonesCLI()
    app.run()
