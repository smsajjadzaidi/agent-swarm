import re

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from agents.knowledge_agent import KnowledgeAgent
from agents.support_agent import SupportAgent
from config import Config

class RouterAgent:
    """
    Entry-point agent that chooses KnowledgeAgent or SupportAgent,
    then applies a personality layer to the final answer.
    """

    _SUPPORT_KEYWORDS = re.compile(
        r"\b(sign[\s-]?in|login|log ?in|transfer|balance|password|"
        r"can'?t\s+.*?(pay|send|transfer))",
        re.IGNORECASE,
    )

    def __init__(self):
        self.knowledge = KnowledgeAgent()
        self.support = SupportAgent()
        self.config = Config()

        # Small LLM for “unsure” classification + personality polishing
        self.clf_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, api_key=self.config.OPENAI_API_KEY)
        self.style_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.4, api_key=self.config.OPENAI_API_KEY)

        # Personality layer prompt
        self.style_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Rewrite the assistant response so it sounds like a friendly, "
                    "empathetic human. Keep the facts unchanged.",
                ),
                ("human", "{raw_answer}"),
            ]
        )

    # ------------------------------------------------------------------ #
    def _is_support(self, message: str) -> bool:
        """Fast heuristic; if unclear we'll ask a tiny LLM."""
        if self._SUPPORT_KEYWORDS.search(message):
            return True
        if re.search(r"\b(rate|fee|cost|maquininha|tap to pay|pix)\b", message, re.I):
            return False  # product/feature → knowledge
        # Unclear → ask classifier LLM
        clf_prompt = ChatPromptTemplate.from_template(
            "Classify the user query:\n"
            "{question}\n\n"
            "Reply with ONE WORD only: 'support' or 'knowledge'."
        )
        resp = self.clf_llm.invoke(
            clf_prompt.format_messages(question=message)
        ).content.strip().lower()
        return resp == "support"

    # ------------------------------------------------------------------ #
    def answer(self, message: str, user_id: str) -> str:
        """Public API for the chatbot front-end."""
        if self._is_support(message):
            raw = self.support.answer(message, user_id)
        else:
            raw = self.knowledge.answer(message)

        # Personality layer
        final = self.style_llm.invoke(
            self.style_prompt.format_messages(raw_answer=raw)
        ).content.strip()

        return final


# ---------------------------------------------------------------------- #
# CLI demo
if __name__ == "__main__":


    question =  "What is the cost of the Maquininha Smart?"
    # question = "I can't sign in to my account."
    uid = "client789"

    bot = RouterAgent()
    print(bot.answer(message=question, user_id=uid))
