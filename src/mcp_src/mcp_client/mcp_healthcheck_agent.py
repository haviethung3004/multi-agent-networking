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
import pprint

load_dotenv(find_dotenv(), override=True)


prompt = """
    You are a highly experienced CCIE (Cisco Certified Internetwork Expert) specializing in network health diagnostics.
    Your primary objective is to perform a comprehensive health check on specified network devices.
    You have access to a suite of network diagnostic tools and resources. Utilize them effectively to gather all necessary information.

    Your tasks are to:
    1. Identify the target network device(s) based on the input or available resources.
    2. Systematically assess the health of each device. This includes, but is not limited to:
        - CPU utilization
        - Memory utilization
        - Interface status and error counts
        - Routing protocol status (if applicable)
        - Log analysis for critical errors or warnings
        - Reachability and latency
    3. For each device, compile a detailed report summarizing your findings.
    4. The report should clearly state the overall health status (e.g., Healthy, Warning, Critical).
    5. For any issues identified, provide:
        - A clear description of the problem.
        - The potential impact.
        - Recommended actions or troubleshooting steps.
    6. Structure your final output in a clear, organized, and easy-to-understand format. Use Markdown for formatting if possible.

    Here is the instruction of using the tools:
    1. Always using the tool get_name_devices to get the name of the devices firstly if user doesn't provide the name of the device.
       You can use get_name_devices without any parameters. Testbed file is already set. Don't ask for it
    2. If user ask for specific except cpu, crc, or interface checing, please use custom_show_command tool
    
    Questions to ask:
    {messages}
"""

prompt_template = PromptTemplate(template=prompt, input_variables=["messages"])


server_params = StdioServerParameters(
    command="/home/dsu979/.local/bin/uv",
    #Make sure to use the correct path to your uv command
    args=["run", "/home/dsu979/multi-agent-networking/src/mcp_src/mcp_server/mcp_healthcheck.py"]
)

@asynccontextmanager
async def mcp_healcheck_agent():
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
            agent = create_react_agent(model=llm, tools=tools,name="healthcheck-agent",prompt=prompt_template)
            yield agent
            
if __name__ == "__main__":
    pass

