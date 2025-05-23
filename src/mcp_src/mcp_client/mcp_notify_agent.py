# src/mcp_src/mcp_client/mcp_notify_agent.py
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from contextlib import asynccontextmanager
from langchain.prompts import PromptTemplate


from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)


prompt = """
    Your task is to send a message to the user by telegram.
    You can use the following tools:
    1. send_message: Send a message to the user by telegram.
    2. update_message: Update a message to the user by telegram.
    3. connect: Checking the connection to the server.

    Question:

    {messages}
    """

prompt_template = PromptTemplate(template=prompt, input_variables=["messages"])



server_params = StdioServerParameters(
    command="/home/dsu979/.local/bin/uv",
    #Make sure to use the correct path to your uv command
    args=["--directory", "/home/dsu979/telegram-mcp", "run", "/home/dsu979/telegram-mcp/main.py",]
)
# @asynccontextmanager
async def mcp_notify_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP client session
            await session.initialize()

            # Load the tools for the agent
            tools = await load_mcp_tools(session)
            print(tools)

            llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model = "gemini-2.0-flash-lite")

            # Create the agent with the tools
            agent = create_react_agent(
                tools=tools,
                model=llm,
                name="notify-agent",
                prompt=prompt_template,
            )

            agent_response = await agent.ainvoke({"messages": "Hello, how are you?"})
            print(agent_response) 
            return agent
            #yield agent

if __name__ == "__main__":
    # Run the agent
    asyncio.run(mcp_notify_agent())