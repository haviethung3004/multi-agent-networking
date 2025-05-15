# src/tools/notify_telegram_tools.py

import os
import asyncio
from langchain_core.tools import tool
import telegram
from dotenv import load_dotenv, find_dotenv


# load the environment variables from the .env file
load_dotenv(find_dotenv(), override=True)
TELEGRAM_API_KEY = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

@tool
async def notify_telegram(message: str) -> str:
    """
    Sends a notification to a Telegram chat.
    Args:
        message (str): The message to send.
    """
    try:
        bot = telegram.Bot(token=TELEGRAM_API_KEY)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        return "Notification sent successfully."
    except Exception as e:
        return f"Failed to send notification: {e}"

if __name__ == "__main__":
    message = "This is a test notification from the notify_telegram tool."
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(notify_telegram(message))
    print(result)
