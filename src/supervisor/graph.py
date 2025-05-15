# src/supervisor/graph.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import MemorySaver
from agent_nodes import notify_agent, monitoring_agent

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)


llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.0-flash-lite")

graph = create_supervisor(
    agents= [])