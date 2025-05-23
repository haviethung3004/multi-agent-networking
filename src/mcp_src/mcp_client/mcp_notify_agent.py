# src/mcp_src/mcp_client/mcp_notify_agent.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from src.tools.telegram_tools import connect, get_updates, send_message
from langchain.prompts import PromptTemplate
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



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



server_params = {
    "url": "http://telegram.api.hungaws.online:8001/mcp",
}

# @asynccontextmanager
async def mcp_notify_agent():
    async with streamablehttp_client(**server_params) as (read, write, _): #type: ignore
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

            agent_response = await agent.ainvoke({"messages": "Hello, how are you?, Please use get chat tool first"})
            print(agent_response) 
            return agent
            #yield agent

if __name__ == "__main__":
    # Run the agent
    pass