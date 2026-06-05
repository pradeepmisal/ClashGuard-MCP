import os
from dotenv import load_dotenv

load_dotenv()

APS_CLIENT_ID     = os.getenv("APS_CLIENT_ID", "")
APS_CLIENT_SECRET = os.getenv("APS_CLIENT_SECRET", "")
APS_CALLBACK_URL  = os.getenv("APS_CALLBACK_URL", "http://localhost:8080/callback")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL   = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
DEMO_MODE         = os.getenv("DEMO_MODE", "true").lower() == "true"

if not ANTHROPIC_API_KEY and not DEMO_MODE:
    raise ValueError("ANTHROPIC_API_KEY is required. Set it in .env file.")
