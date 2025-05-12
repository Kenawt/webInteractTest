print("🚀 Python booting...")

import sys
sys.stdout.flush()
import datetime

try:
    import asyncio
    import os
    from playwright.async_api import async_playwright
    from telegram import Bot
    import time
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("⏳ Startup delay for debug...")
time.sleep(5)
print("✅ Python started")

def get_env(name, fallback=None):
    value = os.environ.get(name)
    if value is None:
        print(f"❌ MISSING ENV VAR: {name}")
    return value if value else fallback

TELEGRAM_TOKEN = get_env("TELEGRAM_TOKEN")
TELEGRAM_CHAT_IDS = get_env("TELEGRAM_CHAT_IDS", "").split(",")
URL = "https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ1mOiKC5Kjxu_1ojfU6-V2URhN1tFZjhiT7WTDsdKIR-IYj-tUCUfMR6x-S_y_NXrr4YW4og4el"
CHECK_INTERVAL_MINUTES = int(get_env("CHECK_INTERVAL_MINUTES", 1))

bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_message(message):
    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            print(f"✅ Message sent to {chat_id}")
        except Exception as e:
            print(f"❌ Telegram error: {e}")

async def check_website():
    async with async_playwright() as p:
        print("🌍 Launching browser to check page...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(URL, timeout=60000)
            #await send_telegram_message("📍 Arrived at page.")
            print("✅ Page loaded successfully.")

            await page.wait_for_timeout(5000)
            #await send_telegram_message("⏳ Waited 5 seconds for JavaScript.")

            # Locate and click the button
            locator = page.locator("span", has_text="Jump to the next bookable date").first
            await locator.wait_for(timeout=15000)
            await locator.click()
            #await send_telegram_message("🖱 Clicked 'Jump to next bookable date'.")

            # Wait another 5s for post-click content updates
            await page.wait_for_timeout(5000)

            # Now check for the availability message
            content = await page.content()
            if "No available times in the next year" in content:
                print("❌ Still no availability.")
                #await send_telegram_message("❌ Still no availability.")
            else:
                await send_telegram_message("📅 A slot might be available!")
        except Exception as e:
            print(f"❌ Error: {e}")
            await send_telegram_message(f"❗ Error during check: {e}")
        finally:
            await browser.close()

async def main():
    start_time = datetime.datetime.now()
    notified_today = False

    while True:
        await check_website()

        # Check if 24 hours have passed since the last notification
        elapsed = datetime.datetime.now() - start_time
        if elapsed.total_seconds() >= 86400 and not notified_today:
            await send_telegram_message("📆 Daily ping: Bot is still running and checking every 5 minutes.")
            start_time = datetime.datetime.now()
            notified_today = True
        elif elapsed.total_seconds() < 86400:
            notified_today = False

        print("⏳ Waiting 5 minutes before next check...")
        await asyncio.sleep(5 * 60)


if __name__ == "__main__":
    asyncio.run(main())
