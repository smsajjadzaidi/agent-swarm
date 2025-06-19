# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from agents.router_agent import RouterAgent   # your RouterAgent class

router_agent = RouterAgent()
app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    user_id: str


@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    # Step 1: decide route + get raw answer + steps
    if router_agent._is_support(req.message):
        raw_result = router_agent.support.agent_executor.invoke(
            {"input": req.message, "user_id": req.user_id}
        )
        agent_name = "SupportAgent"
    else:
        raw_result = router_agent.knowledge.agent_executor.invoke(
            {"input": req.message}
        )
        agent_name = "KnowledgeAgent"

    # Step 2: build workflow payload
    workflow = {}
    for action, tool_return in raw_result["intermediate_steps"]:
        workflow[action.tool] = tool_return

    # Step 3: personality layer
    friendly = router_agent.style_llm.invoke(
        router_agent.style_prompt.format_messages(
            raw_answer=raw_result["output"]
        )
    ).content.strip()

    return {
        "response": friendly,
        "source_agent_response": raw_result["output"],
        "agent_workflow": [
            {"agent_name": agent_name, "tool_calls": workflow}
        ],
    }

