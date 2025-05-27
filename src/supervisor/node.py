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
    You are a supervisor agent managing three agents: notify_agent, ios_agent, and aci_agent.
    - notify_agent sends Slack notifications.
    - ios_agent handles iOS-related tasks.
    - aci_agent processes ACI-specific tasks.
    
    Given the task: "{task}"
    And agent responses: {responses}
    
    Decide which agent to route to next or if the task is complete.
    - If an agent has provided a response, consider it to decide the next step.
    - If the task is complete, return "complete".
    - Otherwise, choose "notify_agent", "ios_agent", or "aci_agent".
    
    Return only the agent name or "complete".
    """,
    input_variables=["task", "responses"]
)


# Supervisor agent node
async def supervisor_node(state: AgentState) -> AgentState:
    """
    Supervisor node that manages the state of the supervisor agent,
    delegating tasks to notify_agent, ios_agent, or aci_agent.
    """
    try:
        task = state.get("task", "No task provided")
        responses = state.get("agent_responses", {})
        logger.info(f"Supervisor processing task: {task} with responses: {responses}")
        # Create a new message to log supervisor activity
        new_message = {
            "type": "system",  # Changed to "type" for LangGraph convention
            "content": f"Processing task: {state['task']}",
            "agent_id": state["agent_id"]
        }

        #Use llm to device the next agent
        responses_str = "\n".join([f"{agent}: {resp}" for agent, resp in responses.items()]) # type: ignore
        prompt_input = {"task": task, "responses": responses_str or "None"}
        next_agent = (await llm.ainvoke(routing_prompt.format(**prompt_input))).content.strip() # type: ignore

        # Update state
        if next_agent == "complete":
            logger.info("Task is complete, share final output to user")
            final_output = responses_str or "Task completed"
            return {
                "messages": [new_message],
                "current_agent": None,
                "agent_id": "supervisor",
                "final_output": final_output
            } # type: ignore
        else: 
            logger.info(f"Routing task to next agent: {next_agent}")
            return {
                "messages": [new_message],
                "current_agent": next_agent,
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
        }# type: ignore
    

async def notify_agent_node(state: AgentState) -> AgentState:
    """
    Notify agent node that sends notifications to users.
    This node is responsible for sending messages to users via the notify agent.
    """
    try:
        # Extract the task from state
        task = state.get("task", "No task provided")
        logger.info(f"Notify agent processing task: {task}")

        #Call the mcp_notify_agent to send the message
        result = await mcp_notify_agent(task)
        logger.info(f"Notify agent result: {result}")

        # Create a new message to log notify agent activity
        new_message = {
            "type": "assistant",  # Changed to "type" for LangGraph convention
            "content": f"Notify agent processed task: {task}",
            "agent_id": state["agent_id"]
        }

        #Update state
        return {
            "agent_responses": {**state.get("agent_responses", {}), "notify_agent": result}, # type: ignore
            "messages": [new_message],
            "current_agent": None,
            "agent_id": "notify_agent"
        } # type: ignore
    except Exception as e:
        logger.error(f"Notify agent error: {e}")
        error_message = {
            "type": "error",
            "content": f"Notify agent failed: {str(e)}",
            "agent_id": "notify_agent"
        }
        return {
            "agent_responses": {**state.get("agent_responses", {}), "notify_agent": f"Error: {str(e)}"}, # type: ignore
            "messages": [error_message],
            "current_agent": None,
            "agent_id": "notify_agent",
            "final_output": f"Error: {str(e)}"
        } # type: ignore
