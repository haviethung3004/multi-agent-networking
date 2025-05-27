# src/mcp_src/mcp_client/mcp_notify_agent.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain.prompts import PromptTemplate
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
import logging
from contextlib import asynccontextmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)
llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model = "gemini-2.0-flash-lite")

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_TEAM_ID = os.getenv("SLACK_TEAM_ID", "")

prompt = """
    You are a highly experienced Slack bot designed to notify users about important events and messages.
    Remember that your channel ID is C086HGY8XAN


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

#@asynccontextmanager
async def mcp_notify_agent(messages) -> str:
    async with stdio_client(server_params) as (read, write):
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
                name="notify-agent",
                prompt=prompt_template,
            )

            async for chunk in agent.astream({"messages": f"{messages}"}):
                if isinstance(chunk, dict) and "agent" in chunk and "messages" in chunk["agent"]:
                    for message in chunk["agent"]["messages"]:
                        if hasattr(message, "content") and message.content:
                            logger.info(message.content)
                            return message.content
            return "No response"
            #yield agent

if __name__ == "__main__":
    # Run the agent
    import asyncio
    asyncio.run(mcp_notify_agent(messages="Hello, Can you send me the hello message to my channel?"))
    #pass