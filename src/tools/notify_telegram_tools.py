# src/tools/notify_telegram_tools.py
import os
import asyncio
from langchain_core.tools import tool
import telegram
from dotenv import load_dotenv, find_dotenv

# Load .env if running this file directly for testing
load_dotenv(find_dotenv(), override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def _send_telegram_message_async(message_text: str) -> str:
    """The actual async function that sends the message."""
    print(f"--- ASYNC TOOL PART: _send_telegram_message_async ---")
    if not TELEGRAM_BOT_TOKEN:
        return "Tool Error: TELEGRAM_BOT_TOKEN not set."
    if not TELEGRAM_CHAT_ID:
        return "Tool Error: TELEGRAM_CHAT_ID not set."

    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        max_length = 4096 # Telegram's limit for MarkdownV2
        if len(message_text) > max_length:
            print(f"Warning: Message length ({len(message_text)}) exceeds Telegram limit. Truncating.")
            message_to_send = message_text[:max_length - 20] + "... (message truncated)"
        else:
            message_to_send = message_text
        
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message_to_send, parse_mode=None) # Plain text for simplicity
        return f"Message successfully sent to Telegram: '{message_to_send[:50]}...'"
    except telegram.error.TelegramError as e:
        return f"Tool Error (Telegram API): {e.message}"
    except Exception as e:
        return f"Tool Error (Unexpected): {type(e).__name__} - {e}"

@tool
def notify_telegram(message_text: str) -> str:
    """
    Synchronously sends a message to a predefined Telegram chat.
    The input 'message_text' is the string content to be sent.
    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.
    Returns a success or error message string.
    """
    print(f"--- SYNC TOOL WRAPPER: notify_telegram ---")
    # This is a common way to run an async function from sync code.
    # Be cautious if LangGraph itself is running an event loop for streaming.
    try:
        # Simplest approach for a standalone script or if no outer loop conflicts:
        return asyncio.run(_send_telegram_message_async(message_text))
    except RuntimeError as e:
            return f"Tool Error (Runtime): {e}"
    except Exception as e:
        return f"Tool Error (notify_telegram wrapper): {type(e).__name__} - {e}"


if __name__ == '__main__':
    # Load .env for direct testing of this file
    if find_dotenv():
        load_dotenv(find_dotenv(), override=True)
        TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") # Re-fetch after loading
        TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
        print(f"Token: {'Set' if TELEGRAM_BOT_TOKEN else 'Not Set'}, Chat ID: {'Set' if TELEGRAM_CHAT_ID else 'Not Set'}")


    print("Testing notify_telegram tool...")
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        response = notify_telegram(message_text="Hello from direct tool test of notify_telegram wrapper!")
        print(f"Tool Response: {response}")
    else:
        print("Skipping direct test of notify_telegram as token/chat_id not found in .env")
        response = notify_telegram(message_text="Test with missing creds.")
        print(f"Tool Response (missing creds): {response}")
