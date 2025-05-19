# src/agent_nodes/notify_agent.py

from langgraph.prebuilt import create_react_agent
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.notify_telegram_tools import notify_telegram
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
# Load environment variables
llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model = "gemini-2.0-flash-lite")

prompt = """
    You are a helpful assistant that notifies the user about the status of their tasks.
    Your task will send the messages to telegram by using the notify_telegram tool.
    {messages}
    """

prompt_template = PromptTemplate(
    input_variables=["messages"],
    template=prompt,
)

def notify_agent():
    # Create the agent
    notify_agent = create_react_agent(
        model=llm,
        tools=[notify_telegram],
        prompt=prompt_template,
        name="notify_agent",
    )

    return notify_agent

if __name__ == "__main__":
    # Example messages to notify
    while True:
        user_input = input("Ask to AI Agent the question or 'exit' to quit: ")
        inputs = {"messages": [{"role": "user", "content": user_input}]}
        for s in notify_agent.stream(inputs, stream_mode="values"):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()
        if user_input.lower() == "exit":
            break
