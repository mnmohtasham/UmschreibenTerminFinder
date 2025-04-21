# 🗓️ Kaiserslautern Appointment Notifier Bot

A Python-based Telegram bot that scrapes available appointment dates from the **Führerscheinstelle Kaiserslautern** website and notifies you via Telegram if an earlier date becomes available than your specified target date otherwise sends ewarlies bookable date silently to Telegram channel.
This is especially helpful if you are looking to secure an earlier driver’s license appointment and want to be automatically alerted when new slots open.

---

## 🛠️ Requirements

- Docker installed **or** Python 3.11+ with pip
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A Telegram channel (or group) and your user ID

---

## 🧾 Configuration

Before running the bot, configure your `config.json` file like this:

```json
{
  "TELEGRAM_BOT_TOKEN": "YOUR_BOT_TOKEN",
  "TELEGRAM_CHANNEL_ID": "-100XXXXXXXXXX",
  "TELEGRAM_USER_ID": 123456789,  #your personal telegram id for tagging
  "TARGET_DATE": "2024-08-27",    #target date to notiy if timeslot found earlier than this
  "CHROMEDRIVER_PATH": "/usr/bin/chromedriver",   #path to chromium on your local machine
  "POSTAL_CODE": "YOUR_POSTAL_CODE",    #postal code for portal verification
  "SERVICE_ID": "5007b529-dd93-49cd-8afd-7e6edc94a693",   #(do not change) this service Id is unique to Umschreiben
  "INTERVAL_MINUTES": 60
}


IMPORTANT: The Dockerfile optimized to run on ARM-based processors like raspberry pi. please update Dockerfile for X86 platform 

Running via Docker
1. Clone the repo:
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

2. Build the Docker image:
docker build -t appointment-checker .

3. Run the container:
docker run -d --name kaiserslautern-bot appointment-checker
Make sure your config.json is in the same directory and properly set up before building!
