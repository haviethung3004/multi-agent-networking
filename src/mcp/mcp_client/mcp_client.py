from contextlib import asynccontextmanager
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.resources import load_mcp_resources
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langgraph.prebuilt import create_react_agent
import os
import asyncio
import pprint

load_dotenv(find_dotenv(), override=True)

server_params = StdioServerParameters(
    command="/home/dsu979/.local/bin/uv",
    #Make sure to use the correct path to your uv command
    args=["run", "src/mcp/mcp_server/mcp_pyats.py"]
)

@asynccontextmanager
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List the available tools
            tools = await load_mcp_tools(session)
            
            # List available resources
            await load_mcp_resources(session)

            # Create the agent
            llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model = "gemini-2.0-flash-lite")
            agent = create_react_agent(model=llm, tools=tools, name="CPU Agent")
            yield agent
            
if __name__ == "__main__":
    pass
