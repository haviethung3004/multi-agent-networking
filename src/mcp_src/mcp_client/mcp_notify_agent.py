# src/mcp_src/mcp_client/mcp_notify_agent.py
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from contextlib import asynccontextmanager


from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)

server_params = {
    "url": "http://telegram.api.hungaws.online:8001/mcp",
}

@asynccontextmanager
async def mcp_notify_agent():
    async with streamablehttp_client(**server_params) as (read, write, _): #type: ignore
        async with ClientSession(read, write) as session:
            # Initialize the MCP client session
            await session.initialize()

            # Load the tools for the agent
            tools = await load_mcp_tools(session)

            llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model = "gemini-2.0-flash-lite")

            # Create the agent with the tools
            agent = create_react_agent(
                tools=tools,
                model=llm,
                name="Notify Agent",
                prompt="You are a Notify Agent. Your job is to send the message to the user via MCP Notify Agent."
            )

            yield agent

if __name__ == "__main__":
    asyncio.run(mcp_notify_agent()) #type: ignore