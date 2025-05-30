from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.prompts import PromptTemplate


# Load environment variables
load_dotenv(find_dotenv(), override=True)

############################# Initialize the PROMPT AGENT #############################
supervisor_prompt = """
    You are a highly experienced CCIE (Cisco Certified Internetwork Expert) specializing managing a network team.
    You are a Supervisor Agent in a multi-agent system designed to coordinate a team of specialized agents, some of which operate over a networked environment, 
    to complete complex tasks efficiently. Your role is to interpret user requests, decompose them into subtasks, 
    delegate tasks to appropriate agents (including those handling networking-related functions), 
    manage network communication between agents, ensure fault tolerance, and synthesize results into a cohesive output.
    When user ask you somthing, must understand the task and delegate the task to the appropriate agents.
    If you not sure about task belong to IOS, you can ask the user for clarification.
    Don't use agent if you are not sure about the task.

    Please follow these steps to ensure effective task management and communication:

    1. Task Analysis: Understand the user's request and identify the main objectives.
    2. Agent Selection: Choose the most suitable agents for each subtask based on their capabilities.
    3. Task Delegation: Assign subtasks to the selected agents, ensuring clear communication and expectations.
    4. Result Synthesis: Collect and integrate the results from all agents, ensuring consistency and coherence.
    5. Transparency and Reporting: Provide the user with a clear overview of the task progress, including any challenges faced and how they were resolved.
    6. Change or check configuration: If the task involves network configuration or checking, use the IOS agent to perform these tasks.
       IOS-agent will know the username and password for the devices.
    7. Always sending the final result to the via notify-agent, then it will send to user a message via slack with the structure of content
    Questions from the user:
    
    {messages}
    """


supervisor_prompt_template = PromptTemplate(template=supervisor_prompt, input_variables=["messages"])

aci_prompt = """
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

aci_prompt_template = PromptTemplate(template=aci_prompt, input_variables=["messages"])

ios_prompt = """
    You are a highly experienced CCIE (Cisco Certified Internetwork Expert) with extensive expertise in designing, configuring, and managing complex network infrastructures.
    Your task will mainly check and configure on Cisco IOS devices. Your configure should be valid and executable.
    The Network Configuration Agent must achieve the following objectives:
    1. Configuration Validation: Check Cisco IOS device configurations for errors, inconsistencies, or deviations from best practices.
    2. Automated Configuration: Apply valid, executable Cisco IOS configurations based on predefined policies or dynamic requirements.
    3. Thinking Process: Clearly articulate your thought process and reasoning behind each configuration decision.
    4. Result Reporting: Provide a detailed report of the configuration changes made, including before-and-after comparisons.
    
    NOTE: You must not configure if you are not sure about the task. Don't remove any configuration if you are not sure about the task.
    Please send the message to the user via notify-agent, then it will send to user a message via slack with the structure of content.

    Some information about the network:
    Credentials: cisco / cisco
    Protocol: ssh

    mgmt IPs of the devices:
    mgmt vrf: MGMT
    | CSR1         | IOS XE    | 192.168.1.55 |
    | CSR2         | IOS XE    | 192.168.1.59 |
    | CSR3         | IOS XE    | 192.168.1.50 |

    
    Questions to ask:
    
    {messages}
    """

ios_prompt_template = PromptTemplate(template=ios_prompt, input_variables=["messages"])

notify_prompt = """
    You are a highly experienced Slack bot designed to notify users about important events and messages.
    Remember that your channel ID is C086HGY8XAN
    Question:
    {messages}
    """

notify_prompt_template = PromptTemplate(template=notify_prompt, input_variables=["messages"])
###################### END OF PROMPTS ######################


# Define the LLM for google generative AI
llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.5-flash-preview-05-20", temperature=0.5)


async def make_graph():
    client =  MultiServerMCPClient({
    "aci-agent":{
        "command": "/home/dsu979/.local/bin/uv",
        "args" : ["--directory", "/home/dsu979/ACI_MCP/aci_mcp", "run", "/home/dsu979/ACI_MCP/aci_mcp/main.py",],
        "transport": "stdio"
    },
    "ios-agent":{
        "command": "/home/dsu979/.local/bin/uv",
        "args" : ["--directory", "/home/dsu979/MCP_Network_automator", "run", "/home/dsu979/MCP_Network_automator/mcp_cisco_server.py"],
        "transport": "stdio"
    },
    "notify-agent":{
        "command": "npx",
        "args" : ["-y","@modelcontextprotocol/server-slack"],
        "env": {
            "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN", ""),
            "SLACK_TEAM_ID": os.getenv("SLACK_TEAM_ID", "")
        },
        "transport": "stdio"
    }}) # type: ignore
    #aci_mcp_tools = await client.get_tools(server_name="aci-agent")
    ios_mcp_tools = await client.get_tools(server_name="ios-agent")
    notify_mcp_tools = await client.get_tools(server_name="notify-agent")

    # aci_agent = create_react_agent(
    #     model=llm,
    #     tools=aci_mcp_tools,
    #     name="aci-agent",
    #     prompt=aci_prompt_template
    # )

    ios_agent = create_react_agent(
        model=llm,
        tools=ios_mcp_tools,
        name="ios-agent",
        prompt=ios_prompt_template
    )

    notify_agent = create_react_agent(
        model=llm,
        tools=notify_mcp_tools,
        name="notify-agent",
        prompt=notify_prompt_template,
        version="v2"
    )

    workflow = create_supervisor(
        model=llm,
        agents=[ios_agent,notify_agent],
        output_mode="full_history",
        supervisor_name="network-supervisor",
        prompt=supervisor_prompt_template)
    
    # Compile the workflow
    app = workflow.compile()
    return app

if __name__ == "__main__":
    pass
    