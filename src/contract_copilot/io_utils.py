from pathlib import Path

from pypdf import PdfReader


def load_contract_text(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix in [".txt", ".md"]:
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        texts = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(texts).strip()
    raise ValueError(f"Unsupported file type: {suffix}")
