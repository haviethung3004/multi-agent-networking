from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from graph import make_graph
import json

# Initialize FastAPI app
app = FastAPI(title="Network Multi Agent")

# Define the request model
class AgentRequest(BaseModel):
    input_text: str

# Define the response model
class AgentResponse(BaseModel):
    output_text: str
    error: Optional[str] = None

# Langgraph to run agent function
async def run_agent(input_text:str)-> AgentResponse:
    agent = await make_graph()
    try:
        response = await agent.ainvoke({"messages": f"{input_text}"})
        messages = response.get("messages", [])

        # Extract sting content from messages
        if isinstance(messages, list) and len(messages) > 0:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                output_text = last_message.content
            else:
                output_text = str(last_message)
        else:
            output_text = str(messages)
        return AgentResponse(output_text=output_text)
    except Exception as e:
        return AgentResponse(output_text="", error=str(e))
            

# API endpoint to handle agent requests
@app.post("/agent", response_model=AgentResponse)
async def call_agent(request: AgentRequest):
    try:
        response = await run_agent(request.input_text)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the Network Multi Agent API. Use POST /agent to interact with the agent."}


@app.post("/grafana_webhook") # You can choose a different path like /alertmanager or /alerts
async def receive_grafana_alert(request: Request): # Using fastapi.Request to get the raw body
    try:
        grafana_payload = await request.json() # Grafana sends JSON

        # For debugging: Print the received payload to your Uvicorn console
        print("--- Received Grafana Alert Payload ---")
        print(json.dumps(grafana_payload, indent=2))
        print("--------------------------------------")

        # Now you can process the grafana_payload
        # For example, extract information and pass it to your existing agent:
        alert_title = grafana_payload.get("title", "Grafana Alert")
        alert_message = grafana_payload.get("message", "No specific message in payload.")
        
        # Example: Create a descriptive input for your LangGraph agent
        input_for_langgraph = f"Alert Notification: {alert_title}. Details: {alert_message}"
        
        # Optional: Call your existing agent logic with this information
        agent_response = await run_agent(input_for_langgraph)
        print(f"Agent processing of Grafana alert: {agent_response.output_text}")
        if agent_response.error:
            print(f"Agent error: {agent_response.error}")

        return {"status": "success", "message": "Grafana webhook received"}
    except Exception as e:
        print(f"Error processing Grafana webhook: {str(e)}")
        # It's good practice to return an error status to Grafana if processing fails
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_agent("Hello, how are you?"))
