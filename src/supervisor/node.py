# src/supervisor/node.py
from supervisor.state_schema import AgentState
import logging
from src.mcp_src.mcp_client.mcp_notify_agent import mcp_notify_agent
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize llm
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)
llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.0-flash-lite", temperature=0.5)

# Prompt for LLM routing
routing_prompt = PromptTemplate(
    template="""
    You are a supervisor agent managing a notify_agent that sends Slack notifications.
    Given the latest user message: "{user_message}"
    And agent responses: {responses}
    
    Decide the next step:
    - If the user message indicates a need to send a notification and notify_agent hasn’t responded, return "notify_agent".
    - If notify_agent has provided a response, return "complete".
    - If the message is unclear or no action is needed, return "complete".
    
    Return only "notify_agent" or "complete".
    """,
    input_variables=["user_message", "responses"]
)


# Supervisor agent node
async def supervisor_node(state: AgentState) -> AgentState:
    """
    Supervisor node that uses an LLM to interpret user messages from the messages list and end the workflow.
    """
    try:
        # Get the latest user message (type: "human")
        user_message = state.get("messages", [{}])
        responses = state.get("agent_responses", {})
        agent_id = state.get("agent_id", "supervisor")
        logger.info(f"Supervisor processing user message: {user_message}, responses: {responses}")

        new_message = {
            "type": "system",
            "content": f"Processing user message: {user_message}, responses: {responses}",
            "agent_id": agent_id
        }
        # Use LLM to decide next action
        responses_str = "\n".join([f"{agent}: {resp}" for agent, resp in responses.items()]) # type: ignore
        prompt_input = {"user_message": user_message, "responses": responses_str or "None"}
        next_action = (await llm.ainvoke(routing_prompt.format(**prompt_input))).content.strip() # type: ignore

        # Update state
        if next_action == "complete":
            final_output = responses_str if responses_str else "No actions taken for message"
            new_message["content"] += " - Message processing complete."
            logger.info("Supervisor ending workflow")
            return {
                "messages": [new_message],
                "current_agent": None,
                "agent_id": "supervisor",
                "final_output": final_output
            }  # type: ignore
        else:
            new_message["content"] += f" - Delegating to {next_action}."
            logger.info(f"Supervisor delegating to: {next_action}")
            return {
                "messages": [new_message],
                "current_agent": next_action,
                "agent_id": "supervisor"
            } # type: ignore
    except Exception as e:
        logger.error(f"Supervisor error: {e}")
        return {
            "messages": [{
                "type": "system",
                "content": f"Supervisor failed: {str(e)}",
                "agent_id": "supervisor"
            }],
            "current_agent": None,
            "agent_id": "supervisor",
            "final_output": f"Error: {str(e)}"
        }     # type: ignore

async def notify_agent_node(state: AgentState) -> AgentState:
    """
    Notify agent node that sends notifications based on the latest user message.
    """
    try:
        # Get the latest user message
        user_message = state.get("messages", [{}])
        agent_id = state.get("agent_id", "notify_agent")
        logger.info(f"Notify agent processing message: {user_message}")
        result = await mcp_notify_agent(user_message)
        logger.info(f"Notify agent result: {result}")
        new_message = {
            "type": "system",
            "content": f"Notify agent processed message: {user_message}, result: {result}",
            "agent_id": agent_id
        }
        return {
            "agent_responses": {**state.get("agent_responses", {}), "notify_agent": result}, # type: ignore
            "messages": [new_message],
            "current_agent": None,
            "agent_id": "notify_agent"
        }
    except Exception as e:
        logger.error(f"Notify agent error: {e}")
        error_message = {
            "type": "system",
            "content": f"Notify agent failed: {str(e)}",
            "agent_id": "notify_agent"
        }
        return {
            "agent_responses": {**state.get("agent_responses", {}), "notify_agent": f"Error: {str(e)}"}, # type: ignore
            "messages": [error_message],
            "current_agent": None,
            "agent_id": "notify_agent",
            "final_output": f"Error: {str(e)}"
        }