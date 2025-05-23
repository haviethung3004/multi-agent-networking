# src/mcp_src/mcp_client/mcp_notify_agent.py
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.resources import load_mcp_resources
from langchain_mcp_adapters.prompts import load_mcp_prompt
from contextlib import asynccontextmanager
from langchain.prompts import PromptTemplate
from typing import TypedDict

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



server_params = StdioServerParameters(
    command="/home/dsu979/.local/bin/uv",
    #Make sure to use the correct path to your uv command
    args=["--directory", "/home/dsu979/telegram-mcp", "run", "/home/dsu979/telegram-mcp/main.py",]
)

from typing import Annotated
from langchain.schema import BaseMessage
from langgraph.graph.message import add_messages


@asynccontextmanager
async def mcp_notify_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP client session
            await session.initialize()

            # Load the tools for the agent
            tools = await load_mcp_tools(session)

            # Load the resources for the agent
            await load_mcp_resources(session)
            # Create the agent with the tools
            agent = create_react_agent(
                tools=tools,
                model=llm,
                name="notify-agent",
                prompt=prompt_template,
            )
            yield agent

if __name__ == "__main__":
    pass