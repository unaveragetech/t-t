----
[Contact me](https://formsubmit.co/el/sumuhu) 
----
# TwinkleTonesCLI

**TwinkleTonesCLI** is a Python-based command-line interface (CLI) tool designed to simplify the process of generating and scheduling Facebook posts. It allows users to create posts using a variety of content types such as quotes, texts, symbols, and images. With additional features like optional auto-generated posts, Facebook navigation via Selenium, and notification reading, this tool streamlines content management and scheduling.

## Features

- **Manual Post Creation**: Choose quotes, texts, symbols, and images for your Facebook posts.
- **Auto-Generated Posts** (Optional): Automatically generate posts using random content and schedule them.
- **Post Scheduling**: Schedule posts using the APScheduler module to publish at a specified time.
- **Facebook Login Automation**: Automates Facebook login using Selenium WebDriver.
- **File Upload**: Upload images along with text posts.
- **Notification Fetching**: Fetch Facebook notifications and save them to a file for later review.
- **Post Reuse**: Save auto-generated posts to a JSON file for future use.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.6+
- Google Chrome (for Selenium WebDriver)
- ChromeDriver (managed automatically with `webdriver-manager`)

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/TwinkleTonesCLI.git
cd TwinkleTonesCLI
```

### 2. Install Dependencies
Install the required Python packages using the following command:
```bash
pip install -r requirements.txt
```

### 3. Directory Structure

Ensure that the following directory structure exists:

```
TwinkleTones/
│
├── quotes/
│   └── quotes.json
├── text/
│   └── text.json
├── symbols/
│   └── symbols.json
├── pictures/
    └── <image files>.png/.jpg/.jpeg
```

**Note**: You can populate the JSON files with your content, or the script will handle empty files gracefully.

## Usage

### Running TwinkleTonesCLI

Run the script from the command line using:

```bash
python twinkletonescli.py
```

### Options

Once the script starts, you will be given the option to:

- Run in **Auto Mode**: This will automatically generate posts at scheduled intervals based on the content available in the JSON files.
- Run in **Manual Mode**: Manually create and schedule posts by selecting quotes, texts, symbols, and images.

### 1. Auto Mode

In auto mode, the script will ask for the type of content to use (quotes, texts, symbols, pictures). You can also specify the interval (in hours) for generating and scheduling posts.

**Example**:

```bash
Run in auto mode? (yes/no): yes
Post Type Selection:
1. Quote
2. Text
3. Symbol
4. Picture
5. All
Select the post type (number): 5
Enter auto-post interval in hours (e.g., 24 for daily): 24
```

This will generate and schedule posts daily with a random combination of quotes, texts, symbols, and pictures.

### 2. Manual Mode

In manual mode, you will manually select the content for your post and schedule it for a specific time.

**Example**:

```bash
Run in auto mode? (yes/no): no
Post Type Selection:
1. Quote
2. Text
3. Symbol
4. Picture
5. All
Select the post type (number): 1

Generated Content: "Success is not final, failure is not fatal." with picture: success.jpg

Enter Facebook email: your-email@example.com
Enter Facebook password: *********
Enter scheduled time (e.g., '2024-10-10 15:30'): 2024-10-10 15:30
```

### 3. Facebook Notifications

The script also provides functionality to fetch your latest Facebook notifications and save them to a file. After you log in, notifications are retrieved automatically and saved in `notifications.json`.

## Configuration

### JSON Files

- **quotes.json**: A list of inspirational quotes.
- **text.json**: Text snippets or custom content for posts.
- **symbols.json**: A list of emojis or other symbols to include in posts.
- **pictures/**: A folder containing `.png`, `.jpg`, or `.jpeg` image files to be included in posts.

### Example JSON (`quotes/quotes.json`)

```json
[
    "Success is not final, failure is not fatal.",
    "Your limitation—it’s only your imagination.",
    "Sometimes later becomes never. Do it now."
]
```

### Example JSON (`text/text.json`)

```json
[
    "Remember to stay positive!",
    "Happy Monday everyone!",
    "It's time to shine!"
]
```

### Scheduler

**APScheduler** is used to schedule posts for future dates. When a post is scheduled, the script will automatically post it at the specified time.

You can modify the interval or set a specific date and time using the following format:

```bash
Enter scheduled time (e.g., '2024-10-10 15:30'): YYYY-MM-DD HH:MM
```

## Facebook Automation

### Facebook Login

The script uses Selenium to automate the login process. To protect your credentials:

1. **Email**: Enter your Facebook email address when prompted.
2. **Password**: Use `getpass` to securely input your password (passwords are not saved in plain text).

```bash
Enter Facebook email: your-email@example.com
Enter Facebook password: *********
```

### Post to Facebook

Once logged in, the script navigates to Facebook's homepage and automatically fills in the post box with the generated content. If a picture is attached, it will be uploaded via file input.

```python
driver.find_element(By.CSS_SELECTOR, "[role='textbox']").send_keys(content)
```

### Notifications

To fetch notifications:

```python
driver.get("https://www.facebook.com/notifications")
```

Notifications will be saved in the `notifications.json` file.

## Customization

You can easily extend this script to handle other social media platforms or add more content sources. The modular nature of the script makes it adaptable to different types of post content.

### Auto-Generated Posts

Auto-posting can be configured to run at any interval. Modify the scheduling logic if you want to post more or less frequently.

```python
self.scheduler.add_job(self.run_auto_posting, 'interval', hours=int(interval))
```

## Future Features

- Add support for Twitter or Instagram posting.
- Integrate with content management systems to pull in more varied content.
- Add logging of user interactions and detailed reports on post performance.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

If you wish to contribute to this project, please submit a pull request or open an issue for discussion.

## Troubleshooting

If you encounter any issues, ensure that:
- ChromeDriver is installed and compatible with your Chrome version.
- All required Python packages are installed (`pip install -r requirements.txt`).

## Contact

For any questions or feedback, please reach out to [your-email@example.com](mailto:your-email@example.com).

