# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APS_CLIENT_ID      = os.getenv("APS_CLIENT_ID", "")
APS_CLIENT_SECRET  = os.getenv("APS_CLIENT_SECRET", "")
ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL    = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL       = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
DEMO_MODE          = os.getenv("DEMO_MODE", "true").lower() == "true"
CSHARP_EXPORT_PATH = os.getenv("CSHARP_EXPORT_PATH", "")

# Absolute paths
BASE_DIR     = Path(__file__).parent
MOCK_DB_PATH = BASE_DIR / "data" / "mock_db.json"
OUTPUT_DIR   = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
