import sys
import os
import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from telegram import Bot
import time
import pytz

print("🚀 Python booting...")
sys.stdout.flush()
time.sleep(5)
print("✅ Python started")

# Get environment variables safely
def get_env(name, fallback=None):
    value = os.environ.get(name)
    if value is None:
        print(f"❌ MISSING ENV VAR: {name}")
    return value if value else fallback

# Load config
TELEGRAM_TOKEN = get_env("TELEGRAM_TOKEN")
TELEGRAM_CHAT_IDS = get_env("TELEGRAM_CHAT_IDS", "").split(",")

# List of websites to check, format: ("Name", "URL")
URLS_TO_CHECK = [
    ("8AM to 12PM", "https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ1mOiKC5Kjxu_1ojfU6-V2URhN1tFZjhiT7WTDsdKIR-IYj-tUCUfMR6x-S_y_NXrr4YW4og4el"),
    ("8AM to 10AM", "https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ1hsXIaeTeu9ChgNNlkeXWSUa9L-XMnGZ_ZP-3zxddON5OPeN7pXjUiakurt5Us69tZjuVxypr9"),
    ("10AM to 12PM", "https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ0DbxMOwTcYM3YBFm7G9X4uKwycOMloofkGYOi6M4Bgw9KarOeEsObP5g6RGjM8jtTZhmdY-eNL")
]


bot = Bot(token=TELEGRAM_TOKEN)
SG_TIMEZONE = pytz.timezone("Asia/Singapore")

# Send messages to all listed chat IDs
async def send_telegram_message(message):
    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            print(f"✅ Message sent to {chat_id}")
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            
async def check_all_websites():
    for name, url in URLS_TO_CHECK:
        await check_website(name, url)

# Main page check
async def check_website(name,url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=60000)
            
            #Hashes below are for debug
            #await send_telegram_message(f"📍 [{name}] Arrived at page!\n{url}")
            #await send_telegram_message("📍 Arrived at page.")
            
            await page.wait_for_timeout(5000)
            #await send_telegram_message("⏳ Waited 5 seconds for JavaScript.")

            locator = page.locator("span", has_text="Jump to the next bookable date").first
            await locator.wait_for(timeout=15000)
            await locator.click()
            #await send_telegram_message("🖱 Clicked 'Jump to next bookable date'.")

            await page.wait_for_timeout(10000)
            content = await page.content()
            if "No available times in the next year" in content:
                now = datetime.now(SG_TIMEZONE)
                print(f"[{name}] No availability as of: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                #await send_telegram_message("❌ Still no availability.")

                #Debug version
                #screenshot_path = f"screenshot_{name.replace(' ', '_')}.png"
                #await page.screenshot(path=screenshot_path, full_page=True)
                
                # Send the text alert
                #await send_telegram_message(f"📅 [{name}] ❌Still no avaiability...\n{url}")
                
                # Send the screenshot
                #for chat_id in TELEGRAM_CHAT_IDS:
                    #try:
                        #with open(screenshot_path, "rb") as photo:
                            #await bot.send_photo(chat_id=chat_id, photo=photo)
                            #print(f"📸 Screenshot sent to {chat_id}")
                    #except Exception as e:
                        #print(f"❌ Failed to send screenshot to {chat_id}: {e}")
            else:
                screenshot_path = f"screenshot_{name.replace(' ', '_')}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                
                # Send the text alert
                await send_telegram_message(f"📅 [{name}] A slot might be available!\n{url}")
                
                # Send the screenshot
                for chat_id in TELEGRAM_CHAT_IDS:
                    try:
                        with open(screenshot_path, "rb") as photo:
                            await bot.send_photo(chat_id=chat_id, photo=photo)
                            print(f"📸 Screenshot sent to {chat_id}")
                    except Exception as e:
                        print(f"❌ Failed to send screenshot to {chat_id}: {e}")

        except Exception as e:
            await send_telegram_message(f"❗ [{name}] Error during check: {e}")
        finally:
            await browser.close()

# Main loop
async def main():
    # Notify bot startup with time
    now = datetime.now(SG_TIMEZONE)
    await send_telegram_message(f"🤖 Bot started at {now.strftime('%Y-%m-%d %H:%M:%S')} GMT+8.\n"
                                f"🕙 It will send a daily check-in at 11:00 PM GMT+8.")
    last_daily_ping_date = None
    while True:
        await check_all_websites()

        now = datetime.now(SG_TIMEZONE)
        current_date = now.date()

        # If it's after 11PM and you haven't pinged today yet
        if now.hour >= 23 and last_daily_ping_date != current_date:
            await send_telegram_message("🕙 Daily check-in: Bot is still running as of 11:00 PM GMT+8.")
            last_daily_ping_date = current_date
            
        await asyncio.sleep(180)  # 3 minutes

if __name__ == "__main__":
    asyncio.run(main())
