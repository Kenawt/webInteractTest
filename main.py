import asyncio
import os
from playwright.async_api import async_playwright
from telegram import Bot

def get_env(name, fallback=None):
    value = os.environ.get(name)
    if value is None:
        print(f"❌ MISSING ENV VAR: {name}")
    return value if value else fallback

print("✅ Booting up main.py...")

# Load env vars with safe fallbacks
TELEGRAM_TOKEN = get_env("TELEGRAM_TOKEN")
TELEGRAM_CHAT_IDS = get_env("TELEGRAM_CHAT_IDS", "").split(",")
URL = ("https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ1mOiKC5Kjxu_1ojfU6-V2URhN1tFZjhiT7WTDsdKIR-IYj-tUCUfMR6x-S_y_NXrr4YW4og4el")
CHECK_INTERVAL_MINUTES = int(get_env(1)

# Display config
print("🔍 ENV LOADED:")
print("Token:", "✔" if TELEGRAM_TOKEN else "❌ MISSING")
print("Chat IDs:", TELEGRAM_CHAT_IDS if TELEGRAM_CHAT_IDS != [""] else "❌ None provided")
print(URL)

bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_message(message):
    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            print(f"✅ Message sent to chat ID {chat_id}")
        except Exception as e:
            print(f"❌ Failed to send to {chat_id}: {e}")

async def check_calendar():
    async with async_playwright() as p:
        print("🧠 Waiting 5s for network...")
        await asyncio.sleep(5)

        print("🧠 Attempting to launch browser...")
        browser = await p.chromium.launch(headless=True)
        print("✅ Browser launched")

        page = await browser.new_page()
        try:
            print("🌍 Navigating to calendar page...")
            await page.goto(URL, timeout=60000)
            print("🌐 Page loaded.")

            print("➡️ Clicking 'Jump to next available bookable date'...")
            await page.click("text=Jump to next available bookable date", timeout=15000)
            await page.wait_for_timeout(5000)

            page_text = await page.content()
            if "No available times in the next year" not in page_text:
                print("📅 Slot might be available!")
                return True
            else:
                print("❌ Still no availability.")
                return False
        except Exception as e:
            print(f"❗ Error during calendar check: {e}")
            return False
        finally:
            await browser.close()

async def main():
    print("🔁 Starting calendar check loop...")
    while True:
        if await check_calendar():
            await send_telegram_message(f"🚨 A slot may be available!\n{URL}")
            break
        print(f"⏳ Waiting {CHECK_INTERVAL_MINUTES} minute(s) before next check...")
        await asyncio.sleep(CHECK_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    asyncio.run(main())
