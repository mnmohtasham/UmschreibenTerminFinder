import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import requests
import os
import json

# Load configuration from config.json
with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
    config = json.load(f)

TELEGRAM_BOT_TOKEN = config["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL_ID = config["TELEGRAM_CHANNEL_ID"]
TELEGRAM_USER_ID = config["TELEGRAM_USER_ID"]
TARGET_DATE_STR = config["TARGET_DATE"]
TARGET_DATE = datetime.strptime(TARGET_DATE_STR, "%Y-%m-%d")

CHROMEDRIVER_PATH = config["CHROMEDRIVER_PATH"]
POSTAL_CODE = config["POSTAL_CODE"]
SERVICE_ID = config["SERVICE_ID"]
INTERVAL_MINUTES = config.get("INTERVAL_MINUTES", 60)


def random_sleep():
    """Sleeps for a random amount of time between 2 and 10 seconds to avoid detection."""
    sleep_time = random.randint(2, 10)
    print(f"Sleeping for {sleep_time} seconds.")
    time.sleep(sleep_time)


def send_telegram_message(message, silent=False, notify_user=False):
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": f"{message}" + (f" 👤 [User](tg://user?id={TELEGRAM_USER_ID})" if notify_user else ""),
        "parse_mode": "Markdown",
        "disable_notification": silent,
    }
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, json=payload)
    if response.ok:
        print("📨 Telegram message sent")
    else:
        print("⚠️ Failed to send Telegram message:", response.text)


def highlight_element(driver, element):
    """Highlights an element with yellow border"""
    driver.execute_script(
        "arguments[0].style.border='3px solid yellow';"
        "arguments[0].style.backgroundColor='rgba(255,255,0,0.2)';",
        element
    )


def run_script():
    try:
        # Setup for the browser and driver
        options = Options()
        options.add_argument("--headless")  # Run in background
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)

        # Step 1: Open the main page
        driver.get("https://onlinetermine.kaiserslautern.de/fuehrerscheinstelle")

        # Step 2: Enter postal code
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "plz_field")))
        plz_input = driver.find_element(By.ID, "plz_field")
        plz_input.clear()
        plz_input.send_keys(POSTAL_CODE)
        random_sleep()  # Random sleep to avoid detection

        # Step 3: Click first Weiter button
        first_weiter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "first_next_btn"))
        )
        highlight_element(driver, first_weiter)
        first_weiter.click()
        print("✅ Clicked first 'Weiter' button")

        # Step 4: Click '+' button for service
        plus_xpath = f"//span[@class='counterButton' and @onclick=\"changecap(1,2,'{SERVICE_ID}')\"]"
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, plus_xpath))
        )
        plus_button = driver.find_element(By.XPATH, plus_xpath)
        highlight_element(driver, plus_button)
        plus_button.click()
        print(f"✅ Clicked '+' button for service ID: {SERVICE_ID}")
        random_sleep()  # Random sleep

        # Step 5–6: Click second Weiter button by simulating the JavaScript onclick
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "forward-service")))

        # Manually trigger the same JS logic as the onclick handler
        driver.execute_script("document.getElementById('action_type').value = 'next_step';")
        driver.execute_script("document.getElementById('step_active').value = '4';")

        forward_btn = driver.find_element(By.ID, "forward-service")
        driver.execute_script("arguments[0].scrollIntoView(true);", forward_btn)
        highlight_element(driver, forward_btn)
        forward_btn.click()
        print("✅ Clicked second 'Weiter' button (via JS and click)")

        random_sleep()  # Random sleep

        # Step 7: Wait for calendar dates
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@class='smart-date']"))
        )

        # Step 8: Extract and process dates
        date_elements = driver.find_elements(By.XPATH, "//a[@class='smart-date']")
        available_dates = []

        for el in date_elements:
            date_str = el.get_attribute("id").replace("day-", "")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                available_dates.append(date_obj)
            except ValueError:
                continue

        if available_dates:
            earliest = min(available_dates)
            formatted = earliest.strftime('%A, %d %B %Y')
            print(f"✅ Earliest available appointment date: {formatted}")

            if earliest < TARGET_DATE:
                # Earlier than target, tag you
                send_telegram_message(f"📅 Sooner appointment available: {formatted}", silent=False, notify_user=True)
            else:
                # Later or equal, send silently to channel
                send_telegram_message(f"📅 Appointment available: {formatted}", silent=True, notify_user=False)
        else:
            print("❌ No appointment dates found.")

    except Exception as e:
        print("❌ Error occurred:", e)
        print("🔍 Current URL:", driver.current_url)
        print("🔍 Page title:", driver.title)

        # Send failure message to Telegram channel
        error_message = f"⚠️ Script failed to run.\nError: {str(e)}\nCurrent URL: {driver.current_url}\nPage Title: {driver.title}"
        send_telegram_message(error_message, silent=False, notify_user=True)

    finally:
        driver.quit()


# Run the script in an infinite loop every 30 minutes
while True:
    run_script()
    print("⏳ Sleeping for 60 minutes before the next run...")
    # scheduled run
    time.sleep(INTERVAL_MINUTES * 60)  # Sleep for 30 minutes
