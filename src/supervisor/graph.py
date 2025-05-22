# src/supervisor/graph.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from mcp_src.mcp_client.mcp_healthcheck_agent import mcp_healcheck_agent
from contextlib import asynccontextmanager
from mcp_src.mcp_client.mcp_notify_agent import mcp_notify_agent
from langchain.prompts import PromptTemplate


prompt = """
    You are a highly experienced CCIE (Cisco Certified Internetwork Expert) specializing in network health diagnostics and a supervisor managing a network team.
    You are a Supervisor Agent in a multi-agent system designed to coordinate a team of specialized agents, some of which operate over a networked environment, 
    to complete complex tasks efficiently. Your role is to interpret user requests, decompose them into subtasks, 
    delegate tasks to appropriate agents (including those handling networking-related functions), 
    manage network communication between agents, ensure fault tolerance, and synthesize results into a cohesive output.
    1. Task Analysis: Understand the user's request and identify the main objectives.
    2. Agent Selection: Choose the most suitable agents for each subtask based on their capabilities.
    3. Task Delegation: Assign subtasks to the selected agents, ensuring clear communication and expectations.
    4. Result Synthesis: Collect and integrate the results from all agents, ensuring consistency and coherence.
    5. Transparency and Reporting: Provide the user with a clear overview of the task progress, including any challenges faced and how they were resolved.
    6. Sending the final result to the via MCP Notify Agent with the structure of content
    Questions from the user:
    {messages}
    """

prompt_template = PromptTemplate(template=prompt, input_variables=["messages"])

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)
llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.0-flash-lite")


@asynccontextmanager
async def setup_supervisor_graph():
    """
    Asynchronously initializes the healthcheck agent and creates/compiles the supervisor graph
    using your specific `create_supervisor`.
    Returns the compiled supervisor application.
    """
    async with mcp_healcheck_agent() as actual_mcp_healthcheck_agent, mcp_notify_agent() as actual_mcp_notify_agent:
        supervisor_definition = create_supervisor(
            agents=[actual_mcp_healthcheck_agent, actual_mcp_notify_agent], # Correctly passing the resolved agent
            model=llm,
            prompt=prompt_template,
            output_mode="full_history"
        )
        app = supervisor_definition.compile()
        yield app

if __name__ == "__main__":
        pass