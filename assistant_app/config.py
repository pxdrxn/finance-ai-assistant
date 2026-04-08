from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DEFAULT_CONTEXT_FILE = DATA_DIR / "conversation_state.json"
DEFAULT_LOG_FILE = LOGS_DIR / "assistant.log"
DEFAULT_MODEL = "gpt-4o-mini"
