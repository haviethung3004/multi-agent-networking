from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from graph import make_graph

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


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_agent("Hello, how are you?"))
