from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv, find_dotenv
import os
import telegram
import asyncio
import time
import logging
from langchain.tools import tool

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Load environment variables from .env file
load_dotenv(find_dotenv(), override=True)

# Get the environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Check if the environment variables are set
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Please set the TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")

@tool
async def connect():
    """
    Check if the server is running.
    This function will be called first to check if the server is running.
    Return the status of the server.
    """
    try:
        bot = telegram.Bot(token = f"{TELEGRAM_BOT_TOKEN}")
        async with bot:
            await bot.get_me()
        return "Connected to Telegram bot."
    except telegram.error.TelegramError as e:
        logger.error(f"Failed to connect to Telegram bot: {e}")
        return "Failed to connect to Telegram bot."

@tool
async def get_updates():
    """
    Get the latest updates from the Telegram.
    This function will be called to get the latest updates from the Telegram bot.
    """
    try:
        bot = telegram.Bot(token = f"{TELEGRAM_BOT_TOKEN}")
        async with bot:
            updates = (await bot.get_updates())[0]
            if updates:
                return logger.info(f"Update: {updates}")
            else:
                return logger.info("No new updates.")

    except telegram.error.TelegramError as e:
        logger.error(f"Failed to get updates: {e}")
        return "Failed to get updates."
    
@tool
async def send_message(messages: str):
    """
    Send a message to the Telegram bot.
    param messages: str
    return: str
    return the status of the message. It will be sent successfully or not.
    """
    bot = telegram.Bot(token=f"{TELEGRAM_BOT_TOKEN}")
    await bot.send_message(text=messages, chat_id=f"{TELEGRAM_CHAT_ID}")
    await asyncio.sleep(1)  # Sleep for 1 second to ensure the message is sent
    logger.info(f"Message sent: {messages}")
    return "Message sent successfully."

def get_data() -> str: 
    return "Greetings to the telegram mcp server"


if __name__ == "__main__":
    pass