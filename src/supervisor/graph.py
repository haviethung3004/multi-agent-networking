# src/supervisor/graph.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from mcp_src.mcp_client.mcp_healthcheck_agent import healcheck_agent
from langchain.prompts import ChatPromptTemplate

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)



llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.0-flash-lite")
mcp_healthcheck_agent = healcheck_agent()

# checkpoint = InMemorySaver()
# store = InMemoryStore()

# graph = create_supervisor(
#     [mcp_healthcheck_agent],
#     model=llm,
#     prompt=(
#         "You are a team supervisor managing a network device. "
#         "For reporting and retrive information you can use the monitoring agent. "
#         "For sending notifications you can use the notify agent about data when you have completed the task. "
#     ),
#     output_mode="full_history"
#     )


from contextlib import asynccontextmanager

@asynccontextmanager
async def setup_supervisor_graph():
    """
    Asynchronously initializes the healthcheck agent and creates/compiles the supervisor graph
    using your specific `create_supervisor`.
    Returns the compiled supervisor application.
    """
    global app

    # healcheck_agent() returns an async context manager.
    # We MUST enter this context manager using `async with` to get the actual agent.
    async with healcheck_agent() as actual_mcp_healthcheck_agent:
        # Now, 'actual_mcp_healthcheck_agent' is the CompiledGraph (a Pregel type)
        # yielded by your healcheck_agent. This is what your create_supervisor needs.

        checkpoint = InMemorySaver()

        # Using YOUR `create_supervisor` from `langgraph_supervisor`
        supervisor_definition = create_supervisor(
            agents=[actual_mcp_healthcheck_agent], # Correctly passing the resolved agent
            model=llm, # Or 'llm=llm' if that's the parameter name in your supervisor
            prompt=(
                "You are a team supervisor managing a network device. "
                "For reporting and retrive information you can use the monitoring agent. "
                "For sending notifications you can use the notify agent about data when you have completed the task. "
            ),
            output_mode="full_history"
            # Add other parameters specific to your create_supervisor if needed (e.g., checkpointer)
        )

        # Compile the graph, as in your original script.
        # This assumes your create_supervisor returns a graph definition that needs compiling.
        # If it already returns a compiled app (Pregel instance), this line would change.
        app = supervisor_definition.compile()
        print("Supervisor app compiled successfully using langgraph_supervisor.create_supervisor.")
        yield app