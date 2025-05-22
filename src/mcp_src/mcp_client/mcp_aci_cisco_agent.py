from contextlib import asynccontextmanager
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.resources import load_mcp_resources
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt import ToolNode
from langchain.prompts import PromptTemplate
import os
import asyncio

load_dotenv(find_dotenv(), override=True)
llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model = "gemini-2.0-flash-lite")

prompt = """
    You are a highly experienced CCIE (Cisco Certified Internetwork Expert) with extensive expertise in designing, configuring, and managing complex network Datacenter infrastructures.
    Your task will check and configure on ACI. Your configure should be valid and executable.
    The ACI CISCO AGENT will achieve the following objectives:
    1. Configuration Validation: Check the valid url to call the ACI API and check the configuration for errors, inconsistencies, or deviations from best practices.
    2. Management: Apply valid, executable ACI configurations based on predefined policies or dynamic requirements.
    3. Thinking Process: Clearly articulate your thought process and reasoning behind each configuration decision.
    4. Result Reporting: Provide a detailed report of the configuration changes made, including before-and-after comparisons.
    
    Questions to ask:
    
    {messages}
    """

prompt_template = PromptTemplate(template=prompt, input_variables=["messages"])


server_params = StdioServerParameters(
    command="/home/dsu979/.local/bin/uv",
    args=["run", "--with-requirements", "/home/dsu979/ACI_MCP/aci_mcp/requirements.txt", "/home/dsu979/ACI_MCP/aci_mcp/main.py"]
)

@asynccontextmanager
async def mcp_aci_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List the available tools
            tools = await load_mcp_tools(session)            

            # List available resources
            # await load_mcp_resources(session)

            # Load the prompt
            #prompt = await load_mcp_prompt(session)

            # Create the agent
            agent = create_react_agent(model=llm, tools=tools, name="aci_agent", prompt=prompt_template)
            yield agent

if __name__ == "__main__":
    pass