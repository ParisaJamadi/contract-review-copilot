from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from .config import PLAYBOOK_PATH, VECTORSTORE_DIR


def build_playbook_index() -> None:
    playbook_text = PLAYBOOK_PATH.read_text(encoding="utf-8")
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=120)
    chunks = splitter.split_text(playbook_text)
    docs = [Document(page_content=chunk, metadata={"source": "playbook"}) for chunk in chunks]

    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    db = Chroma.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(),
        persist_directory=str(VECTORSTORE_DIR),
    )
    db.persist()


if __name__ == "__main__":
    if not Path(PLAYBOOK_PATH).exists():
        raise FileNotFoundError(f"Playbook file not found: {PLAYBOOK_PATH}")
    build_playbook_index()
    print("Playbook index built successfully.")
