# src/mcp_src/mcp_client/mcp_notify_agent.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from src.tools.telegram_tools import connect, get_updates, send_message
from langchain.prompts import PromptTemplate




from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)
llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model = "gemini-2.0-flash-lite")


prompt = """
    You have these tools by folowing:

    1. connect: Use this tool to check if the server is running. Always use this tool first.
    2. message: Use this tool to send a message to the Telegram bot.
    3. get_updates: Get the latest updates from the Telegram bot to make sure the messages are sent.

    Note: You just use every tool once, and you cannot use the same tool again.

    Question:

    {messages}
    """

prompt_template = PromptTemplate(template=prompt, input_variables=["messages"])

def notify_agent():
    app = create_react_agent(model=llm, tools=[connect, send_message, get_updates], prompt=prompt_template, name="notify-agent")
    return app


if __name__ == "__main__":
    pass