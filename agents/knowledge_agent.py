import os
from typing import Any

from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.prompts import ChatPromptTemplate

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.schema import BaseRetriever

from knowledge_base_builder import get_retriever
from config import Config


class KnowledgeAgent:
    """Answers questions about InfinitePay (RAG) and general web queries (Serper)."""

    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.0,
        web_timeout: int | None = None,
    ) -> None:
        """Build RAG chain + search tool + agent."""
        # -- 1) LLM ----------------------------------------------------------
        self.config = Config()
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature, api_key=self.config.OPENAI_API_KEY)

        # -- 2) Retriever & RAG chain ----------------------------------------
        retriever: BaseRetriever = get_retriever()   # loads or builds FAISS
        rag_prompt = hub.pull("rlm/rag-prompt")      # generic combine-docs prompt
        combine_docs_chain = create_stuff_documents_chain(self.llm, rag_prompt)
        self.rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

        # Wrap RAG as a tool
        @tool("company_docs", return_direct=True)
        def company_docs(query: str) -> str:
            """Search InfinitePay documentation & answer."""
            result = self.rag_chain.invoke({"question": query, "input": query})
            return result['answer']

        # -- 3) Serper search tool ------------------------------------------
        serper = GoogleSerperAPIWrapper(serper_api_key=self.config.SERPER_API_KEY,
                                        k=8, timeout=web_timeout)

        @tool("search_web", return_direct=True)
        def search_web(query: str) -> str:
            """Answer using Google (Serper.dev)."""
            return serper.run(query)

        # -- 4) Assemble agent ----------------------------------------------
        system_prompt = (
            "You are InfiniBot, expert on InfinitePay. "
            "If the question is about InfinitePay products, first try `company_docs`. "
            "Otherwise, or if docs are insufficient, use `search_web`. "
            "Cite sources when you can."
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
                # Placeholders fill up a **list** of messages
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        tools = [company_docs, search_web]
        self.agent = create_tool_calling_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=tools, return_intermediate_steps=True)

    # ---------------------------------------------------------------------- #
    def answer(self, query: str) -> dict[str, Any]:
        """Public method: route question to best tool and return final answer."""
        result = self.agent_executor.invoke({"input": query})
        return result["output"]


# --------------------------------------------------------------------------
# Quick CLI test
if __name__ == "__main__":

    bot = KnowledgeAgent()
    # question = "What is InfinitePay Tap to Pay and how fast are settlements?"
    question = "What is the fees of InfinitePay"
    # question = "Find me similar products to InfinitePay"
    print("Answer: ", bot.answer(question))

