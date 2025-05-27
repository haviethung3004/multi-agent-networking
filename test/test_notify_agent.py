# test/test_notify_agent.py
from src.supervisor.state_schema import AgentState
from src.supervisor.node import supervisor_node, notify_agent_node
from langgraph.graph import StateGraph, END
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("notify_agent", notify_agent_node)
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["current_agent"] if state["current_agent"] else END,
    {
        "notify_agent": "notify_agent",
        END: END
    }
)

workflow.add_edge("notify_agent", "supervisor")
workflow.set_entry_point("supervisor")

graph = workflow.compile()

async def test_notify_agent(user_message: str):
    initial_state = AgentState(
        agent_responses={},
        current_agent=None,
        final_output=None,
        messages=[{"type": "human", "content": user_message}],
        agent_id="supervisor"
    )
    try:
        result = await graph.ainvoke(initial_state)
        logger.info(f"Test result: {result}")
        return result
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return None

if __name__ == "__main__":
    test_messages = ["Please send Hello to me"]
    for message in test_messages:
        print(f"\nTesting message: {message}")
        result = asyncio.run(test_notify_agent(message))
        print(f"Final state: {result}")