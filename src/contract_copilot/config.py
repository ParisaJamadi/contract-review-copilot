from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
VECTORSTORE_DIR = ROOT_DIR / "vectorstore"
OUTPUTS_DIR = ROOT_DIR / "outputs"

PLAYBOOK_PATH = DATA_DIR / "playbook.md"
RUBRIC_PATH = DATA_DIR / "rubric.md"
MODEL_NAME = "gpt-4o-mini"
TOP_K = 4

# Load local secrets/config from project .env (if present).
load_dotenv(ROOT_DIR / ".env")
