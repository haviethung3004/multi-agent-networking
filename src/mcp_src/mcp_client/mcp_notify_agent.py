# src/mcp_src/mcp_client/mcp_notify_agent.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain.prompts import PromptTemplate
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



from dotenv import load_dotenv, find_dotenv
import os

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_TEAM_ID = os.getenv("SLACK_TEAM_ID", "")

load_dotenv(find_dotenv(), override=True)
llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model = "gemini-2.0-flash-lite")


prompt = """
    You are a highly experienced Slack bot designed to notify users about important events and messages.

    Question:

    {messages}
    """

prompt_template = PromptTemplate(template=prompt, input_variables=["messages"])



server_params = StdioServerParameters(
    command="npx",
    args= ["-y","@modelcontextprotocol/server-slack"],
    env= {
    "SLACK_BOT_TOKEN": f"{SLACK_BOT_TOKEN}",
    "SLACK_TEAM_ID": f"{SLACK_TEAM_ID}",
    }

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

            agent_response = await agent.ainvoke({"messages": "Hello, how are you?, Please send me a Hello message."})
            print(agent_response) 
            return agent
            #yield agent

if __name__ == "__main__":
    # Run the agent
    import asyncio
    asyncio.run(mcp_notify_agent())