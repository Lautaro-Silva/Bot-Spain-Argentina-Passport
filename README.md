# Passport Appointer Notifier Bot
This project monitors changes on the CGE Online Passport Appointment page (corresponding to the renovation of Spanish passport in the Spain Consulate in Argentina) and sends updates via Telegram whenever appointment dates are updated or as a daily summary.


# Features (so far)
- Web scraping: Extracts the latest and next opening dates for passport appointments.
- Telegram notifications: Sends alerts when changes are detected.
- Daily updates: Notifies about the current status daily at 9:00 AM.
- Change tracking: Maintains a historical log of all detected updates.

# What's inside the code
This project is written in Python and uses the following libraries:
- `requests`: For making HTTP requests to fetch the webpage content.
- `BeautifulSoup` (from `bs4`): To parse and extract data from the HTML page.

The main features of the bot include:
- Scraping and extracting relevant dates for passport appointments.
- Comparing current and previous data to detect changes.
- Sending real-time notifications via Telegram when new dates are announced.
- Sending daily notifications about the current status, even if no changes occurred.

The program ensures reliable data handling by saving the last known state in a JSON file.

# Configuration
1. Telegram Bot: Create a bot using BotFather and get your bot token.
2. Chat ID: Use the bot to get your Telegram chat ID.
3. Update Settings:
  - `TELEGRAM_TOKEN`: Your Telegram bot token.
  - `CHAT_ID`: Your chat ID.
  - `URL`: The URL of the page to scrape.

# Why I made this
Managing passport appointments can be frustrating when availability changes suddenly. I created this bot to help users stay updated without constantly checking the website. This project was also a great opportunity to improve my skills in web scraping and automation. It's a simple yet useful tool that bridges manual effort with automated efficiency. There's still room for improvement, and I’m excited to keep iterating based on feedback or ideas!

# What's next?
Here are some features I plan to add in the future:
- Better error handling for website changes or outages.
- Customizable notification times and frequencies.
- Support for notifications to multiple accounts at once.
- Deployment to a serverless environment like AWS Lambda for better uptime.

# Contributing
This is more of a personal project than a professional one, but if you want to play around with the code or suggest improvements, feel free to fork the repo and submit a pull request.
