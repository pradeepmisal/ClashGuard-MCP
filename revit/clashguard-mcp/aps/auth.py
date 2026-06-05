# aps/auth.py
import httpx
import time
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import APS_CLIENT_ID, APS_CLIENT_SECRET

_token_cache = {"token": None, "expires_at": 0}

def get_token() -> str:
    """Get a valid 2-legged APS access token. Caches until expiry."""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    resp = httpx.post(
        "https://developer.api.autodesk.com/authentication/v2/token",
        data={
            "grant_type":    "client_credentials",
            "client_id":     APS_CLIENT_ID,
            "client_secret": APS_CLIENT_SECRET,
            "scope":         "data:read",
        },
        verify=True   # ALWAYS True — Autodesk requirement
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["token"]      = data["access_token"]
    _token_cache["expires_at"] = now + data["expires_in"]
    return _token_cache["token"]
