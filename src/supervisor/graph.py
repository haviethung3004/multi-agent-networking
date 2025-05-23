# src/supervisor/graph.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from mcp_src.mcp_client.mcp_healthcheck_agent import mcp_healcheck_agent
from contextlib import asynccontextmanager
from mcp_src.mcp_client.mcp_notify_agent import notify_agent
from mcp_src.mcp_client.mcp_ios_cisco_agent import mcp_ios_agent
from mcp_src.mcp_client.mcp_aci_cisco_agent import mcp_aci_agent
from langchain.prompts import PromptTemplate
from langgraph_supervisor import create_handoff_tool

prompt = """
    You are a highly experienced CCIE (Cisco Certified Internetwork Expert) specializing managing a network team.
    You are a Supervisor Agent in a multi-agent system designed to coordinate a team of specialized agents, some of which operate over a networked environment, 
    to complete complex tasks efficiently. Your role is to interpret user requests, decompose them into subtasks, 
    delegate tasks to appropriate agents (including those handling networking-related functions), 
    manage network communication between agents, ensure fault tolerance, and synthesize results into a cohesive output.
    When user ask you somthing, must understand the task and delegate the task to the appropriate agents.
    If you not sure about task belong to IOS or ACI, you can ask the user for clarification.
    Don't use agent if you are not sure about the task.

    Please follow these steps to ensure effective task management and communication:

    1. Task Analysis: Understand the user's request and identify the main objectives.
    2. Agent Selection: Choose the most suitable agents for each subtask based on their capabilities.
    3. Task Delegation: Assign subtasks to the selected agents, ensuring clear communication and expectations.
    4. Result Synthesis: Collect and integrate the results from all agents, ensuring consistency and coherence.
    5. Transparency and Reporting: Provide the user with a clear overview of the task progress, including any challenges faced and how they were resolved.
    6. Change or check configuration: If the task involves network configuration or checking, use the IOS agent to perform these tasks.
       IOS-agent will know the username and password for the devices.
    7. ACI Agent: If the task involves ACI configuration, use the ACI agent to perform these tasks.
    8. Always sending the final result to the via notify-agent, then it will send to user a message via telegram with the structure of content

    NOTE: Please be careful when ask notify-agent, just send the message, don't say too much ask him to send the message.

    Questions from the user:
    
    {messages}
    """

prompt_template = PromptTemplate(template=prompt, input_variables=["messages"])

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)
llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.0-flash-lite", temperature=0.5)



@asynccontextmanager
async def setup_supervisor_graph():
    """
    Asynchronously initializes the healthcheck agent and creates/compiles the supervisor graph
    using your specific `create_supervisor`.
    Returns the compiled supervisor application.
    """
    async with mcp_ios_agent() as actual_mcp_ios_agent, mcp_aci_agent() as actual_mcp_aci_agent:
        supervisor_definition = create_supervisor(
            agents=[notify_agent(), actual_mcp_ios_agent, actual_mcp_aci_agent],
            model=llm,
            prompt=prompt_template,
            output_mode="full_history",
            supervisor_name="network-supervisor",
        )
        app = supervisor_definition.compile()
        yield app

if __name__ == "__main__":
        pass