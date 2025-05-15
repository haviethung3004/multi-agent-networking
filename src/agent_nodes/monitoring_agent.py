# src/agent_nodes/monitoring_agent.py

from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.device_tools import get_device_info, generate_report
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import PromptTemplate
import os

load_dotenv(find_dotenv(), override=True)

llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model = "gemini-2.0-flash-lite")

prompt = """
    You are a monitoring agent. You can use the following tools:
    1. get_device_info: Retrieves all information in inventory.
    2. generate_report: Generates a report based on the provided data.
    {messages}
    """

promt_template = PromptTemplate(
    template=prompt,
    input_variables=["messages"],
    )

def monitoring_agent():
    # Create the agent
    monitoring_agent = create_react_agent(
        model=llm,
        tools=[get_device_info, generate_report],
        name="monitoring_agent",
        prompt=promt_template,
        )
    return monitoring_agent

if __name__ == "__main__":
    while True:
        user_input = input("Ask to AI Agent the question or 'exit' to quit: ")
        inputs = {"messages": [{"role": "user", "content": user_input}]}
        for s in monitoring_agent.stream(inputs, stream_mode="values"):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()
        if user_input.lower() == "exit":
            break
            