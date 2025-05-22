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
    You are a highly experienced CCIE (Cisco Certified Internetwork Expert) with extensive expertise in designing, configuring, and managing complex network infrastructures.
    Your task will check and configure on Cisco IOS devices. Your configure should be valid and executable.
    The Network Configuration Agent must achieve the following objectives:
    1. Configuration Validation: Check Cisco IOS device configurations for errors, inconsistencies, or deviations from best practices.
    2. Automated Configuration: Apply valid, executable Cisco IOS configurations based on predefined policies or dynamic requirements.
    3. Thinking Process: Clearly articulate your thought process and reasoning behind each configuration decision.
    4. Result Reporting: Provide a detailed report of the configuration changes made, including before-and-after comparisons.
    
    Some information about the network:
    Credentials: cisco / cisco
    Protocol: ssh

    | R1         | IOL XE    | 10.10.20.171 |
    | R2         | IOL XE    | 10.10.20.172 |
    | SW1        | IOL L2 XE | 10.10.20.173 |
    | SW2        | IOL L2 XE | 10.10.20.174 |

    
    Questions to ask:
    
    {messages}
    """

prompt_template = PromptTemplate(template=prompt, input_variables=["messages"])

server_params = StdioServerParameters(
    command="/home/dsu979/.local/bin/uv",
    #Make sure to use the correct path to your uv command
    args=["run","--with", "netmiko", "/home/dsu979/MCP_Network_automator/mcp_cisco_server.py"]
)

@asynccontextmanager
async def mcp_ios_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List the available tools
            tools = await load_mcp_tools(session)            

            # List available resources
            await load_mcp_resources(session)

            # Create the agent
            agent = create_react_agent(model=llm, tools=tools,name="ios-agent",prompt=prompt_template)
            # agent_response = await agent.ainvoke({"messages": "Hello how are you? please login R1 and show me the cpu utilization"})
            # print(agent_response)

            yield agent

if __name__ == "__main__":
    pass