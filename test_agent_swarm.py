import pytest
import pytest_check as check

from agents.knowledge_agent import KnowledgeAgent
from agents.support_agent import SupportAgent

from fastapi.testclient import TestClient
import app as fastapi_app


@pytest.mark.parametrize(
    "question, expected_answer",
    [
        (
            "What is the fees of InfinitePay for debit card",  # knowledge agent
            "0.35%",
        ),
        (
            "What is the fees of InfinitePay for credit card?",  # knowledge agent
            "2.69%",
        ),
        (
            "What is the fees of Stripe",  # serper agent
            "Stripe",
        ),
    ],
)
def test_knowledge_agent(question, expected_answer):
    bot = KnowledgeAgent()
    resp = bot.answer(question)
    check.is_in(expected_answer, resp)


@pytest.mark.parametrize(
    "message,user_id,expected_snippet",
    [
        # 1) Pure account status (should NOT open a ticket)
        ("What is my account balance?", "client789", "$726.40"),
        # 2) Active account but still an issue → ticket TIC-0002
        ("I cannot sign in to my account.", "client789", "TIC-0002"),
        # 3) Ask about existing ticket
        ("What is the status of ticket TIC-0001?", "client789", "TIC-0001"),
    ],
)
def test_support_agent(message, user_id, expected_snippet):
    bot = SupportAgent()
    resp = bot.answer(message, user_id)
    check.is_in(expected_snippet, resp)


def test_e2e():
    payload = {
        "message": "I can't sign in to my account.",
        "user_id": "client789",
    }
    client = TestClient(fastapi_app.app)
    res = client.post("/chat", json=payload)
    assert res.status_code == 200

    body = res.json()
    # ------------- Top-level keys ------------
    for k in ("response", "source_agent_response", "agent_workflow"):
        check.is_in(k, body)

    # ------------- Ticket created ------------
    check.is_in("TIC-0002", body["response"])

    # ------------- Workflow trace ------------
    wf = body["agent_workflow"][0]
    check.equal(wf["agent_name"], "SupportAgent")
    tool_calls = wf["tool_calls"]
    check.is_in("get_account_status", tool_calls)
    check.is_in("create_support_ticket", tool_calls)
