import sys
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, Error as PlaywrightError
from telegram import Bot
import time
import pytz

print("🚀 Python booting...", flush=True)
time.sleep(5)
print("✅ Python started", flush=True)

def get_env(name, fallback=None):
    value = os.environ.get(name)
    if value is None:
        print(f"❌ MISSING ENV VAR: {name}", flush=True)
    return value if value else fallback

TELEGRAM_TOKEN = get_env("TELEGRAM_TOKEN")
TELEGRAM_CHAT_IDS = get_env("TELEGRAM_CHAT_IDS", "").split(",")

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
            
async def check_website(name, url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Retry goto once if it fails
            for attempt in range(2):
                try:
                    await page.goto(url, timeout=60000)
                    break
                except PlaywrightError as e:
                    if attempt == 1:
                        raise
                    print(f"⚠️ Goto failed on attempt {attempt + 1}, retrying...", flush=True)
                    await asyncio.sleep(3)

            await page.wait_for_timeout(10000)

            locator = page.locator("span", has_text="Jump to the next bookable date").first
            await locator.wait_for(timeout=15000)
            await locator.click()

            await page.wait_for_timeout(10000)
            content = await page.content()

            if "No available times in the next year" in content:
                now = datetime.now(SG_TIMEZONE)
                print(f"[{name}] No availability as of: {now.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
            else:
                screenshot_path = f"screenshot_{name.replace(' ', '_')}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                await send_telegram_message(f"📅 [{name}] A slot might be available!\n{url}")
                await send_telegram_screenshot(name, screenshot_path)

            await browser.close()
    except Exception as e:
        await send_telegram_message(f"❗ [{name}] Error during check: {type(e).__name__}: {e}")
        print(f"❌ [{name}] Crash during check: {e}", flush=True)

async def check_all_websites():
    for name, url in URLS_TO_CHECK:
        await check_website(name, url)

async def main():
    now = datetime.now(SG_TIMEZONE)
    await send_telegram_message(f"🤖 Bot started at {now.strftime('%Y-%m-%d %H:%M:%S')} GMT+8.\n"
                                f"🕙 It will send a daily check-in at 11:15 PM GMT+8.")

    last_daily_ping_date = None

    while True:
        try:
            print(f"🔄 Checking all websites at {datetime.now(SG_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
            await check_all_websites()
        except Exception as e:
            msg = f"💥 Unhandled crash in main loop:\n{type(e).__name__}: {e}"
            await send_telegram_message(msg)
            print(msg, flush=True)

        now = datetime.now(SG_TIMEZONE)
        current_date = now.date()

        if now.hour >= 23 and now.minute >= 15 and last_daily_ping_date != current_date:
            await send_telegram_message("🕙 Daily check-in: Bot is still running as of 11:00 PM GMT+8.")
            last_daily_ping_date = current_date

        await asyncio.sleep(180)  # 3 minutes

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"🔥 Fatal crash in script: {type(e).__name__}: {e}", flush=True)
