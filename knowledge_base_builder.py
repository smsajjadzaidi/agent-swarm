from pathlib import Path
from config import Config

from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import BaseRetriever

config = Config()

INDEX_DIR = Path(config.KNOWLEDGE_BASE_DIR)          # where the index lives
K = config.K                                 # top-k for retrieval


def get_retriever() -> "BaseRetriever":
    """
    Returns a retriever.
    • First tries to load an existing FAISS index from disk.
    • If none exists, crawls the URLs, builds + saves the index once.
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # ---------- 1) Fast path: index already built ----------
    if INDEX_DIR.exists():
        store = FAISS.load_local(
            str(INDEX_DIR),
            embeddings,
            allow_dangerous_deserialization=True  # required by LangChain ≥0.1.0
        )
        return store.as_retriever(search_kwargs={"k": K})

    # ---------- 2) Slow path: build index ----------
    cfg = Config()
    docs = WebBaseLoader(cfg.INFINITEPAY_URLS).load()

    # optional: clean / split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    store = FAISS.from_documents(chunks, embeddings)
    store.save_local(str(INDEX_DIR))           # persist to disk for next time

    return store.as_retriever(search_kwargs={"k": K})


if __name__ == "__main__":
    retriever = get_retriever()
    print(retriever.invoke("What is InfinitePay?"))
