from pipin import install_requirements
import requests
import schedule
import time
from bs4 import BeautifulSoup

# Constants for Facebook API
APP_ID = None  # Will be set by user input
APP_SECRET = None  # Will be set by user input
PAGE_ID = None  # Will be set by user input
REDIRECT_URI = 'https://localhost/'  # Change to your redirect URI if needed

def clear_screen():
    print("\n" * 100)

def display_menu():
    clear_screen()
    print("==== Facebook Automation CLI ====")
    print("1. Set Up Facebook API Credentials")
    print("2. Fetch Short-lived Access Token")
    print("3. Fetch Long-lived Access Token")
    print("4. Save Tokens to a File")
    print("5. Send Text Post")
    print("6. Send Image Post")
    print("7. Schedule Posts")
    print("8. Exit")
    choice = input("Select an option (1-8): ")
    return choice

def set_up_credentials():
    global APP_ID, APP_SECRET, PAGE_ID
    APP_ID = input("Enter your Facebook App ID: ")
    APP_SECRET = input("Enter your Facebook App Secret: ")
    PAGE_ID = input("Enter your Facebook Page ID: ")
    print("Credentials saved!")
    print("You can access the Facebook Business login page here: https://business.facebook.com/business/loginpage/?next=https%3A%2F%2Fdevelopers.facebook.com%2F%3Fnav_ref%3Dbiz_unified_f3_login_page_to_dfc&app=436761779744620&login_options%5B0%5D=FB&login_options%5B1%5D=SSO&is_work_accounts=1&config_ref=biz_login_tool_flavor_dfc")

def fetch_short_lived_token():
    print("\n=== Fetching Short-lived Access Token ===")
    auth_url = f'https://www.facebook.com/dialog/oauth?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&scope=pages_show_list,pages_read_engagement,pages_manage_posts,public_profile'
    print("Please visit this URL to authorize the application:")
    print(auth_url)
    
    print("\nFollow these steps to fetch your short-lived access token:")
    print("1. Open the link above in your browser.")
    print("2. Authorize the application.")
    print("3. You will be redirected to the redirect URI with a code.")
    print("4. Copy that code and paste it below.")
    
    code = input("Enter the code from the URL: ")
    
    token_url = f'https://graph.facebook.com/v12.0/oauth/access_token?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&client_secret={APP_SECRET}&code={code}'
    
    response = requests.get(token_url)
    token_data = response.json()
    
    if 'access_token' in token_data:
        short_lived_token = token_data['access_token']
        print(f"Short-lived Access Token: {short_lived_token}")
        return short_lived_token
    else:
        print("Error fetching token:", token_data.get('error', 'Unknown error'))
        return None

def fetch_long_lived_token(short_lived_token):
    print("\n=== Fetching Long-lived Access Token ===")
    long_lived_url = f'https://graph.facebook.com/v12.0/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={short_lived_token}'
    
    response = requests.get(long_lived_url)
    long_lived_data = response.json()
    
    if 'access_token' in long_lived_data:
        long_lived_token = long_lived_data['access_token']
        print(f"Long-lived Access Token: {long_lived_token}")
        return long_lived_token
    else:
        print("Error fetching token:", long_lived_data.get('error', 'Unknown error'))
        return None

def save_tokens(short_lived_token, long_lived_token):
    with open('facebook_tokens.txt', 'w') as f:
        f.write(f'Short-lived Access Token: {short_lived_token}\n')
        f.write(f'Long-lived Access Token: {long_lived_token}\n')
    print("Tokens saved to facebook_tokens.txt.")

def send_text_post(access_token):
    message = input("Enter the message for the post: ")
    post_url = f'https://graph.facebook.com/{PAGE_ID}/feed'
    payload = {
        'message': message,
        'access_token': access_token
    }
    response = requests.post(post_url, data=payload)
    print('Text Post Response:', response.text)

def send_image_post(access_token):
    image_url = input("Enter the image URL to post: ")
    image_post_url = f'https://graph.facebook.com/{PAGE_ID}/photos'
    img_payload = {
        'url': image_url,
        'access_token': access_token
    }
    response = requests.post(image_post_url, data=img_payload)
    print('Image Post Response:', response.text)

def schedule_posts():
    facebook_access_token = input("Enter your long-lived access token: ")
    schedule.clear()  # Clear previous schedules
    while True:
        try:
            post_time = input("Enter the time to schedule the post (HH:MM format) or 'exit' to quit: ")
            if post_time.lower() == 'exit':
                break
            message = input("Enter the message for the scheduled post: ")
            schedule.every().day.at(post_time).do(send_text_post, access_token=facebook_access_token)
            print(f"Post scheduled at {post_time}.")
        except Exception as e:
            print("Error scheduling post:", e)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    while True:
        choice = display_menu()
        if choice == '1':
            set_up_credentials()
        elif choice == '2':
            short_lived_token = fetch_short_lived_token()
        elif choice == '3':
            if 'short_lived_token' in locals():
                long_lived_token = fetch_long_lived_token(short_lived_token)
            else:
                print("Please fetch the short-lived token first.")
        elif choice == '4':
            if 'short_lived_token' in locals() and 'long_lived_token' in locals():
                save_tokens(short_lived_token, long_lived_token)
            else:
                print("Please fetch both tokens first.")
        elif choice == '5':
            if 'long_lived_token' in locals():
                send_text_post(long_lived_token)
            else:
                print("Please fetch the long-lived token first.")
        elif choice == '6':
            if 'long_lived_token' in locals():
                send_image_post(long_lived_token)
            else:
                print("Please fetch the long-lived token first.")
        elif choice == '7':
            schedule_posts()
            print("Starting scheduler...")
            run_scheduler()
        elif choice == '8':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please select again.")

if __name__ == "__main__":
    install_requirements()
    main()
