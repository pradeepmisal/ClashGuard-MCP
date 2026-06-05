# aps/auth.py
"""
Autodesk Platform Services — OAuth 2.0 authentication.
Uses client credentials flow (2-legged).
All connections use HTTPS — Autodesk marketplace requirement.
"""
import time
import httpx
from config import APS_CLIENT_ID, APS_CLIENT_SECRET

_cache: dict = {"token": None, "expires_at": 0}


def get_token() -> str:
    """Returns a valid APS access token, using cached value if not expired."""
    now = time.time()
    if _cache["token"] and now < _cache["expires_at"] - 60:
        return _cache["token"]

    resp = httpx.post(
        "https://developer.api.autodesk.com/authentication/v2/token",
        data={
            "grant_type":    "client_credentials",
            "client_id":     APS_CLIENT_ID,
            "client_secret": APS_CLIENT_SECRET,
            "scope":         "data:read",
        },
        verify=True,  # AUTODESK REQUIREMENT — never set to False
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    _cache["token"]      = data["access_token"]
    _cache["expires_at"] = now + data.get("expires_in", 3600)
    return _cache["token"]
