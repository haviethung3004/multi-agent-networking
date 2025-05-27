# src/supervisor/state_schema.py
from typing import TypedDict, List, Dict, Annotated, Optional
from langgraph.graph.message import add_messages


# State for suppervisor agent understanding the task and delegate the task to the appropriate agents.
class AgentState(TypedDict):
    task: Optional[str]  # The task to be processed by the agent
    agent_responses: Optional[Dict[str, str]]
    current_agent: Optional[str]  # The agent currently handling the task, if any
    final_output: Optional[str]  # The final output of the task, if available
    messages: Annotated[List, add_messages]
    agent_id: str