from datetime import datetime
from itertools import count
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from config import Config
# --------------------------------------------------------------------------- #
# 🗄️  Dummy “database” & helpers
_FAKE_ACCOUNTS: Dict[str, Dict[str, Any]] = {
    "client789": {
        "status": "Active",
        "balance": 726.40,
        "plan": "Pro",
        "last_login": "2025-06-18T14:11:00",
    }
}
_TICKET_COUNTER = count(2)
_FAKE_TICKETS: Dict[str, Dict[str, Any]] = {
    "TIC-0001": {
    "user": "client789",
    "issue": "account login",
    "status": "open",
    "created": "2025-06-18T14:11:00",
    }
}


# ──────────────────────────────────────────────────────────────────────────
# 🔧  Tools

@tool("get_account_status")  # ⚠️  NO return_direct
def get_account_status(user_id: str) -> str:
    """
    Return account status, balance, plan, last login.
    """
    rec = _FAKE_ACCOUNTS.get(user_id)
    if not rec:
        return f"NO_ACCOUNT"
    return (
        f"STATUS={rec['status']}; "
        f"BALANCE={rec['balance']}; "
        f"PLAN={rec['plan']}; "
        f"LAST_LOGIN={rec['last_login']}"
    )


@tool("create_support_ticket", return_direct=True)
def create_support_ticket(user_id: str, issue: str) -> str:
    """
    Open a ticket and immediately show the ticket-ID to the user.
    """
    ticket_id = f"TIC-{next(_TICKET_COUNTER):04}"
    _FAKE_TICKETS[ticket_id] = {
        "user": user_id,
        "issue": issue,
        "status": "open",
        "created": datetime.utcnow().isoformat(timespec="seconds"),
    }
    return (
        f"✅ I’ve opened support ticket **{ticket_id}** for you. "
        "Our engineers will investigate and update you soon."
    )


@tool("get_ticket_status")   # NO return_direct
def get_ticket_status(ticket_id: str) -> str:
    """
    Look up the current status of a support ticket.
    """
    t = _FAKE_TICKETS.get(ticket_id)
    if not t:
        return "NOT_FOUND"
    return (
        f"TICKET={ticket_id}; STATUS={t['status']}; "
        f"CREATED={t['created']}; ISSUE={t['issue']}"
    )


class SupportAgent:
    """
    Handles account/help questions with two tools:
    • get_account_status
    • create_support_ticket
    """

    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.0):
        self.config = Config()
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature, api_key=self.config.OPENAI_API_KEY)

        tools = [get_account_status, create_support_ticket, get_ticket_status]

        system_prompt = (
            "You are Customer-Support Bot for InfinitePay.\n"
            "The current user ID is the *string* \"{user_id}\".\n"
            "1. ALWAYS call `get_account_status(user_id)` first when the user "
            "mentions sign-in problems, transfers, or any account-specific issue.\n"
            "2. If `get_account_status` returns `STATUS=Active` (i.e. no restriction) "
            "but the user still reports a problem, IMMEDIATELY call "
            "`create_support_ticket(user_id, issue=`the user's exact complaint`).\n"
            "3. If the user asks about an existing ticket ID, call "
            "`get_ticket_status(ticket_id)`.\n"
            "4. Keep replies concise, empathetic, and always include the ticket ID "
            "when a ticket is opened."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        agent = create_tool_calling_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, return_intermediate_steps=True)

    # ------------------------------------------------------------------ #
    def answer(self, message: str, user_id: str) -> str:
        """
        Public entry for the router.
        Returns the agent's final reply (string).
        """
        result = self.agent_executor.invoke({"input": message, "user_id": user_id})
        return result["output"]


# --------------------------------------------------------------------------- #
# CLI smoke-test
if __name__ == "__main__":

    uid = "client789"
    bot = SupportAgent()
    question = "I cant sign in my account. "
    # question = "get me status of TIC-0001 "

    print("Answer: ", bot.answer(question, uid))
