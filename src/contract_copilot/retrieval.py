from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from .config import TOP_K, VECTORSTORE_DIR


def get_vectorstore() -> Chroma:
    embedding = OpenAIEmbeddings()
    return Chroma(
        persist_directory=str(VECTORSTORE_DIR),
        embedding_function=embedding,
    )


def retrieve_playbook_context(contract_text: str, k: int = TOP_K) -> str:
    store = get_vectorstore()
    docs = store.similarity_search(contract_text, k=k)
    if not docs:
        return "No playbook context found."
    return "\n\n---\n\n".join([doc.page_content for doc in docs])
