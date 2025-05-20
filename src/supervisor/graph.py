# src/supervisor/graph.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from agent_nodes.notify_agent import notify_agent
from agent_nodes.monitoring_agent import monitoring_agent
from langchain.prompts import ChatPromptTemplate

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)



llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.0-flash-lite")

monitoring_agent_instance = monitoring_agent()
notify_agent_instance = notify_agent()

checkpoint = InMemorySaver()
store = InMemoryStore()

graph = create_supervisor(
    [monitoring_agent_instance, notify_agent_instance],
    model=llm,
    prompt=(
        "You are a team supervisor managing a network device. "
        "For reporting and retrive information you can use the monitoring agent. "
        "For sending notifications you can use the notify agent about data when you have completed the task. "
    ),
    output_mode="full_history"
    )

app = graph.compile()