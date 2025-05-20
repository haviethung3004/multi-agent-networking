# src/supervisor/graph.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from mcp_src.mcp_client.mcp_healthcheck_agent import healcheck_agent
from contextlib import asynccontextmanager

from langchain.prompts import PromptTemplate

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
    async with healcheck_agent() as actual_mcp_healthcheck_agent:
        # Using YOUR `create_supervisor` from `langgraph_supervisor`
        supervisor_definition = create_supervisor(
            agents=[actual_mcp_healthcheck_agent], # Correctly passing the resolved agent
            model=llm, # Or 'llm=llm' if that's the parameter name in your supervisor
            prompt=(
                "You are a team supervisor managing a network device. "
                "For reporting and retrive information you can use the healcheck agent to get the status of the device. "
                "Please ask the agent carefully"
            ),
            output_mode="full_history"
        )
        app = supervisor_definition.compile()
        print("Supervisor app compiled successfully using langgraph_supervisor.create_supervisor.")
        yield app