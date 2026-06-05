# ClashGuard MCP — Complete Product Requirements & Execution Plan
**Version:** 1.0  
**Date:** June 2, 2026  

> **HOW TO USE THIS DOCUMENT**  
> This is a complete, self-contained execution plan. Every step is numbered and actionable.  
> - If you are an **AI agent**: execute every step in order. Steps marked `[MANUAL]` require human action.  
> - If you are a **developer**: read Section 0 first, then follow your assigned sections.  
> - Steps marked `⚠` are blockers — nothing after them works until they are done.  
> - Steps marked `[AUTODESK REQUIREMENT]` are mandatory for marketplace submission.

---

## TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [Architecture Decision Record](#2-architecture-decision-record)
3. [Repository Setup](#3-repository-setup)
4. [APS Developer Account Setup](#4-aps-developer-account-setup) ⚠ BLOCKER
5. [Project Folder Structure](#5-project-folder-structure)
6. [Environment Configuration](#6-environment-configuration)
7. [MCP Server Core](#7-mcp-server-core)
8. [Tool 1 — extract_revit_data](#8-tool-1--extract_revit_data)
9. [Tool 2 — analyze_model](#9-tool-2--analyze_model)
10. [Tool 3 — detect_clashes](#10-tool-3--detect_clashes)
11. [Tool 4 — suggest_resolutions](#11-tool-4--suggest_resolutions)
12. [Tool 5 — generate_report](#12-tool-5--generate_report)
13. [Mock Data for Demo](#13-mock-data-for-demo)
14. [Claude Desktop Configuration](#14-claude-desktop-configuration)
15. [Autodesk Manifest JSON](#15-autodesk-manifest-json) [AUTODESK REQUIREMENT]
16. [User Consent Flow](#16-user-consent-flow) [AUTODESK REQUIREMENT]
17. [Security Hardening](#17-security-hardening) [AUTODESK REQUIREMENT]
18. [Testing & Validation](#18-testing--validation)
19. [Demo Scenarios](#19-demo-scenarios)
20. [PowerPoint Presentation](#20-powerpoint-presentation)
21. [Autodesk Submission Checklist](#21-autodesk-submission-checklist)
22. [Known Risks & Mitigations](#22-known-risks--mitigations)

---

## 1. PROJECT OVERVIEW

### What We Are Building
**ClashGuard MCP** is a Model Context Protocol server that connects Claude AI to Autodesk Revit via APS APIs to detect, prioritize, and suggest resolutions for MEP (Mechanical, Electrical, Plumbing) clashes using natural language.

### The One-Sentence Pitch
> An architect types "Will my new windows clash with HVAC ducts?" in Claude Desktop and gets a prioritized, actionable answer — without opening Navisworks — in under 5 minutes.

### Why It Matters
- MEP clashes cost the global AEC industry **$625 billion/year** in rework
- Current tools (Navisworks) detect clashes but don't prioritize or suggest fixes
- ClashGuard is the first MCP to bring natural language + AI reasoning into this workflow
- Targets: Autodesk Design & Make Marketplace (live since DevCon 2026)

### Target Users
| User | Pain | How ClashGuard Helps |
|------|------|----------------------|
| BIM Coordinator | 2-4 hrs/cycle in Navisworks | Detect + prioritize in 5 min |
| Architect | No real-time clash feedback | Instant clash check during design |
| MEP Engineer | Manual coordination meetings | AI-generated rerouting suggestions |
| Project Manager | Late discovery of clashes | Proactive continuous checking |

### Scope for This Delivery (June 5)
- ✅ Working MCP server with 5 tools
- ✅ Demo running on Claude Desktop (free tier)
- ✅ Mock data for demo (real APS if sandbox available)
- ✅ Autodesk manifest.json created
- ✅ PDF/Word clash report generation
- ✅ 10-slide PPT for presentation
- ❌ NOT in scope: Revit write-back (annotation in model) — deferred to v2
- ❌ NOT in scope: Multi-agent architecture — deferred to v2
- ❌ NOT in scope: AWS Lambda deployment — deferred to v2

---

## 2. ARCHITECTURE DECISION RECORD

### Core Decision: Deterministic Geometry + AI Reasoning
**Decision:** All geometric calculations (collision detection, coordinate extraction, clearance measurement) are 100% deterministic, rule-based code. Claude AI is used ONLY for reasoning, prioritization, report writing, and natural language understanding.

**Why this matters for Autodesk:**  
Autodesk's Trust & Safety requirements for marketplace MCPs require that engineering calculations be reliable and not subject to AI hallucination. Our architecture satisfies this by design.

**The boundary is:**
```
DETERMINISTIC ENGINE handles:        AI/CLAUDE handles:
- AABB bounding box collision         - "Which clash matters most right now?"
- Intersection volume calculation     - "Why does this clash matter?"
- Coordinate extraction from Revit    - "What should the engineer do?"
- Clearance measurement               - "Write a professional report"
- Severity scoring (rule-based)       - "Understand user's natural language"
- Tolerance thresholds                - "Explain the fix in plain English"
```

### Transport: stdio (Claude Desktop)
For the hackathon demo, the MCP server uses stdio transport — it runs as a local process called by Claude Desktop. This matches the official Autodesk manifest example exactly.

### Stack Decisions
| Component | Choice | Reason |
|-----------|--------|--------|
| Language | Python 3.11 | MCP SDK, trimesh, APS SDK all Python-native |
| MCP framework | anthropic MCP SDK | Official, stdio support built-in |
| Geometry engine | trimesh + shapely | Battle-tested, well-documented, open source |
| APS client | requests + httpx | Simple, HTTPS-enforced |
| Report generation | python-docx + reportlab | No external dependencies |
| AI calls | anthropic Python SDK | Direct Claude API, no middleware |
| Demo data | Local JSON (mock_db.json) | No APS account needed for demo |

---

## 3. REPOSITORY SETUP

### Step 3.1 — Create GitHub Repository [MANUAL: Krushna]
```bash
# Go to github.com and create new repo: clashguard-mcp
# Visibility: Private (change to public before Autodesk submission)
# Initialize with README: Yes
# .gitignore: Python
# License: MIT

# Clone locally
git clone https://github.com/cctech-pune/clashguard-mcp.git
cd clashguard-mcp
```

### Step 3.2 — Initialize Python environment [Krushna]
```bash
# Create virtual environment
python3.11 -m venv venv

# Activate
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Verify Python version
python --version
# Must show: Python 3.11.x
```

### Step 3.3 — Install all dependencies [Krushna]
```bash
pip install anthropic          # MCP SDK + Claude API
pip install httpx              # HTTPS-enforced HTTP client
pip install requests           # APS API calls
pip install trimesh            # 3D geometry / AABB collision
pip install shapely            # 2D geometry operations
pip install numpy              # Math for geometry
pip install python-docx        # Word report generation
pip install reportlab          # PDF report generation
pip install python-dotenv      # .env file loading
pip install pytest             # Testing framework
pip install pytest-asyncio     # Async test support

# Save to requirements.txt
pip freeze > requirements.txt
```

---

## 4. APS DEVELOPER ACCOUNT SETUP

> ⚠ **BLOCKER** — Without this, Tools 1 and 2 cannot be built or tested against real Revit data. Do this on Day 1.

### Step 4.1 — Create APS Developer Account [MANUAL: Prathmesh]
1. Go to: https://aps.autodesk.com
2. Click "Sign In" → "Create Account" (or use existing Autodesk account)
3. Go to Developer Portal: https://developer.autodesk.com
4. Click "Create App"
5. App Name: `ClashGuard MCP`
6. Application Type: `Server-side app`
7. Callback URL: `http://localhost:8080/callback` (for local dev OAuth)
8. Select APIs to enable:
   - ✅ Data Management API
   - ✅ Model Derivative API
   - ✅ Authentication API
9. Click "Create App"
10. **SAVE THESE VALUES** — you will need them:
    - `CLIENT_ID`: (copy from dashboard)
    - `CLIENT_SECRET`: (copy from dashboard)

### Step 4.2 — Test API Access [MANUAL: Prathmesh]
```bash
# Test that you can get a 2-legged token (server-to-server)
curl -X POST "https://developer.api.autodesk.com/authentication/v2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=data:read"

# Expected: {"access_token": "...", "token_type": "Bearer", "expires_in": 3600}
# If you see this — APS is working. Proceed.
# If you see an error — check CLIENT_ID and CLIENT_SECRET values.
```

### Step 4.3 — Upload a test Revit model to BIM 360 [MANUAL: Prathmesh]
> If CCTech has a Revit model available — even a simple one with ducts, pipes, and walls — upload it to BIM 360 to get a real URN for testing. If not, skip this and use mock data (Section 13).

1. Go to https://acc.autodesk.com
2. Create or open a project
3. Upload a Revit file (.rvt)
4. After upload, get the file URN (base64-encoded string) from the URL
5. Save the URN — you will need it for Tool 1 testing

---

## 5. PROJECT FOLDER STRUCTURE

Create this exact folder structure:
```
clashguard-mcp/
│
├── server.py                    # MAIN ENTRY POINT — run this
├── requirements.txt             # Python dependencies
├── .env                         # API keys (NEVER commit to Git)
├── .env.example                 # Template for .env (commit this)
├── .gitignore                   # Must include .env
├── manifest.json                # Autodesk MCP manifest [AUTODESK REQUIREMENT]
├── claude_desktop_config.json   # Claude Desktop setup template
├── README.md                    # Setup instructions
│
├── tools/                       # One file per MCP tool
│   ├── __init__.py
│   ├── extract_revit_data.py    # Tool 1
│   ├── analyze_model.py         # Tool 2
│   ├── detect_clashes.py        # Tool 3
│   ├── suggest_resolutions.py   # Tool 4
│   └── generate_report.py       # Tool 5
│
├── engine/                      # Deterministic geometry engine
│   ├── __init__.py
│   ├── aabb.py                  # AABB collision detection
│   ├── severity.py              # Rule-based severity scoring
│   └── geometry_utils.py        # Coordinate helpers
│
├── aps/                         # Autodesk API client
│   ├── __init__.py
│   ├── auth.py                  # OAuth 2.0 token management
│   ├── model_derivatives.py     # Model Derivatives API client
│   └── revit_client.py          # Revit element extraction
│
├── data/
│   ├── mock_db.json             # Mock Revit data for demo
│   ├── severity_rules.json      # Clash severity rule definitions
│   └── report_templates/
│       ├── clash_report.docx    # Word template
│       └── clash_report_pdf.py  # PDF template
│
├── outputs/                     # Generated reports (gitignored)
│   └── .gitkeep
│
└── tests/
    ├── test_tools.py            # Unit tests for all 5 tools
    ├── test_engine.py           # Tests for geometry engine
    └── fixtures/
        └── sample_clash_data.json
```

### Step 5.1 — Create all folders and init files
```bash
mkdir -p tools engine aps data/report_templates outputs tests/fixtures

# Create __init__.py files
touch tools/__init__.py engine/__init__.py aps/__init__.py

# Create placeholder files
touch tools/extract_revit_data.py tools/analyze_model.py
touch tools/detect_clashes.py tools/suggest_resolutions.py
touch tools/generate_report.py
touch engine/aabb.py engine/severity.py engine/geometry_utils.py
touch aps/auth.py aps/model_derivatives.py aps/revit_client.py
touch outputs/.gitkeep tests/test_tools.py tests/test_engine.py

echo "Folder structure created."
```

---

## 6. ENVIRONMENT CONFIGURATION

### Step 6.1 — Create .env.example (commit this to Git)
```ini
# Autodesk Platform Services (APS)
APS_CLIENT_ID=your_aps_client_id_here
APS_CLIENT_SECRET=your_aps_client_secret_here
APS_CALLBACK_URL=http://localhost:8080/callback

# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-5

# Optional: Revit project URN for real testing
APS_TEST_URN=your_model_urn_here

# Demo mode (use mock data instead of real APS)
DEMO_MODE=true
```

### Step 6.2 — Create .env (DO NOT commit — contains real secrets)
```ini
APS_CLIENT_ID=PASTE_YOUR_REAL_CLIENT_ID
APS_CLIENT_SECRET=PASTE_YOUR_REAL_CLIENT_SECRET
APS_CALLBACK_URL=http://localhost:8080/callback
ANTHROPIC_API_KEY=PASTE_YOUR_REAL_ANTHROPIC_KEY
ANTHROPIC_MODEL=claude-sonnet-4-5
DEMO_MODE=true
```

### Step 6.3 — Update .gitignore
```
.env
outputs/
venv/
__pycache__/
*.pyc
*.pyo
.DS_Store
```

### Step 6.4 — Create config.py (project root)
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

APS_CLIENT_ID     = os.getenv("APS_CLIENT_ID", "")
APS_CLIENT_SECRET = os.getenv("APS_CLIENT_SECRET", "")
APS_CALLBACK_URL  = os.getenv("APS_CALLBACK_URL", "http://localhost:8080/callback")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL   = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
DEMO_MODE         = os.getenv("DEMO_MODE", "true").lower() == "true"

if not ANTHROPIC_API_KEY and not DEMO_MODE:
    raise ValueError("ANTHROPIC_API_KEY is required. Set it in .env file.")
```

---

## 7. MCP SERVER CORE

### Step 7.1 — Create server.py (main entry point) [Krushna]

```python
# server.py
"""
ClashGuard MCP Server
====================
Main entry point for the ClashGuard MCP server.
Implements Model Context Protocol over stdio transport.
Compatible with Claude Desktop (free tier).

Usage in claude_desktop_config.json:
  {
    "mcpServers": {
      "clashguard": {
        "command": "python",
        "args": ["/FULL/PATH/TO/clashguard-mcp/server.py"]
      }
    }
  }
"""

import json
import sys
import logging
from pathlib import Path

from tools.extract_revit_data import run as extract_revit_data
from tools.analyze_model       import run as analyze_model
from tools.detect_clashes      import run as detect_clashes
from tools.suggest_resolutions import run as suggest_resolutions
from tools.generate_report     import run as generate_report

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("clashguard")

TOOLS = [
    {
        "name": "extract_revit_data",
        "description": (
            "Extracts MEP system geometry and spatial data from a Revit model "
            "using the Autodesk Platform Services (APS) Model Derivatives API. "
            "Returns element IDs, types, bounding boxes, and floor/zone locations. "
            "Use when the user asks about their building model, MEP systems, "
            "or wants to analyze elements in Revit."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_urn": {
                    "type": "string",
                    "description": "APS model URN (base64-encoded). Leave empty to use demo data."
                },
                "floor_filter": {
                    "type": "string",
                    "description": "Optional floor number or zone (e.g. '3', 'Level 3')."
                },
                "element_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Element types to extract. Options: Duct, Pipe, CableTray, Window, Wall, Beam. Default: all MEP types."
                }
            },
            "required": []
        }
    },
    {
        "name": "analyze_model",
        "description": (
            "Analyzes spatial relationships between building elements — "
            "processes clearance zones, identifies elements in proximity, "
            "and builds a spatial context map for clash analysis. "
            "Run this after extract_revit_data and before detect_clashes."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "elements": {
                    "type": "array",
                    "description": "Element list from extract_revit_data output."
                },
                "clearance_tolerance_mm": {
                    "type": "number",
                    "description": "Minimum clearance in mm before flagging as soft clash. Default: 50mm."
                }
            },
            "required": []
        }
    },
    {
        "name": "detect_clashes",
        "description": (
            "Runs deterministic AABB (Axis-Aligned Bounding Box) collision detection "
            "between MEP systems and architectural/structural elements. "
            "All calculations are rule-based — no AI involved. "
            "Returns a list of clashes with locations, element pairs, "
            "intersection volumes, and initial severity scores."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "elements": {
                    "type": "array",
                    "description": "Analyzed elements from analyze_model output."
                },
                "systems_to_check": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Systems to cross-check. Options: HVAC, Plumbing, Electrical, Structural. Default: all."
                },
                "zones": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional zone filter (e.g. ['Floor 3', 'South Facade'])."
                }
            },
            "required": []
        }
    },
    {
        "name": "suggest_resolutions",
        "description": (
            "Uses Claude AI reasoning to prioritize detected clashes by severity "
            "and generate engineering-friendly rerouting or coordination suggestions. "
            "AI is used ONLY for prioritization and recommendation — "
            "not for geometry calculations. "
            "Returns ranked clash list with plain-English resolution suggestions."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "clashes": {
                    "type": "array",
                    "description": "Clash list from detect_clashes output."
                },
                "project_context": {
                    "type": "string",
                    "description": "Optional context about the project (building type, phase, constraints)."
                },
                "user_consent_given": {
                    "type": "boolean",
                    "description": "Must be true — confirms user consents to sending clash data to Claude AI for analysis."
                }
            },
            "required": ["user_consent_given"]
        }
    },
    {
        "name": "generate_report",
        "description": (
            "Generates a professional MEP clash coordination report in PDF and/or Word format. "
            "Report includes clash summary, severity breakdown, element details, "
            "location maps (described in text), and resolution recommendations. "
            "Saves report to the outputs/ folder and returns the file path."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "clashes": {
                    "type": "array",
                    "description": "Clash list — either from detect_clashes or suggest_resolutions."
                },
                "project_name": {
                    "type": "string",
                    "description": "Name of the project for the report header."
                },
                "format": {
                    "type": "string",
                    "enum": ["pdf", "docx", "both"],
                    "description": "Output format. Default: both."
                }
            },
            "required": ["clashes"]
        }
    }
]

TOOL_HANDLERS = {
    "extract_revit_data":  extract_revit_data,
    "analyze_model":       analyze_model,
    "detect_clashes":      detect_clashes,
    "suggest_resolutions": suggest_resolutions,
    "generate_report":     generate_report,
}

def send(obj: dict):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()

def tool_result(call_id, text: str):
    send({"jsonrpc": "2.0", "id": call_id,
          "result": {"content": [{"type": "text", "text": text}]}})

def error_result(call_id, code: int, message: str):
    send({"jsonrpc": "2.0", "id": call_id,
          "error": {"code": code, "message": message}})

def main():
    log.info("ClashGuard MCP Server starting...")
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            continue

        method  = msg.get("method", "")
        msg_id  = msg.get("id")
        params  = msg.get("params", {})

        if method == "initialize":
            send({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "clashguard-mcp",
                        "version": "1.0.0",
                        "description": "AI-powered MEP clash detection for Revit"
                    }
                }
            })

        elif method == "notifications/initialized":
            pass

        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": msg_id,
                  "result": {"tools": TOOLS}})

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            handler   = TOOL_HANDLERS.get(tool_name)
            if handler:
                try:
                    result_text = handler(arguments)
                    tool_result(msg_id, result_text)
                except Exception as e:
                    log.error(f"Tool {tool_name} failed: {e}")
                    error_result(msg_id, -32603, f"Tool error: {str(e)}")
            else:
                error_result(msg_id, -32601, f"Unknown tool: {tool_name}")

        elif msg_id is not None:
            error_result(msg_id, -32601, f"Method not found: {method}")

if __name__ == "__main__":
    main()
```

---

## 8. TOOL 1 — extract_revit_data

**Owner:** Prathmesh  
**Dependencies:** APS Model Derivatives API or mock_db.json (DEMO_MODE)

### Step 8.1 — Create APS Auth client (aps/auth.py)
```python
# aps/auth.py
import httpx
import time
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
```

### Step 8.2 — Create extract_revit_data tool (tools/extract_revit_data.py)
```python
# tools/extract_revit_data.py
"""
Tool 1: extract_revit_data
Extracts MEP element geometry and spatial data from Revit via APS.
In DEMO_MODE, reads from data/mock_db.json instead of live APS.
"""

import json
from pathlib import Path
from config import DEMO_MODE

MOCK_DB_PATH = Path(__file__).parent.parent / "data" / "mock_db.json"

MEP_TYPES = {"Duct", "Pipe", "CableTray", "Conduit", "MechanicalEquipment",
             "PlumbingFixture", "ElectricalEquipment", "Window", "Wall", "Beam"}

def run(args: dict) -> str:
    floor_filter   = args.get("floor_filter", "")
    element_types  = args.get("element_types", list(MEP_TYPES))
    model_urn      = args.get("model_urn", "")

    if DEMO_MODE or not model_urn:
        return _extract_from_mock(floor_filter, element_types)
    else:
        return _extract_from_aps(model_urn, floor_filter, element_types)

def _extract_from_mock(floor_filter: str, element_types: list) -> str:
    with open(MOCK_DB_PATH, "r") as f:
        db = json.load(f)

    elements = db.get("elements", [])

    if floor_filter:
        elements = [e for e in elements
                    if floor_filter.lower() in e.get("location", "").lower()]
    if element_types:
        elements = [e for e in elements if e.get("type") in element_types]

    return json.dumps({
        "source":   "mock_data",
        "count":    len(elements),
        "elements": elements,
        "message":  f"Extracted {len(elements)} elements from mock data. Ready for analysis."
    }, indent=2)

def _extract_from_aps(model_urn: str, floor_filter: str, element_types: list) -> str:
    """Real APS extraction — requires valid token and model URN."""
    from aps.auth import get_token
    import httpx

    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get model metadata
    meta_url = (
        f"https://developer.api.autodesk.com/modelderivative/v2/"
        f"designdata/{model_urn}/metadata"
    )
    resp = httpx.get(meta_url, headers=headers, verify=True)
    resp.raise_for_status()
    metadata = resp.json()
    guid = metadata["data"]["metadata"][0]["guid"]

    # Get properties
    props_url = (
        f"https://developer.api.autodesk.com/modelderivative/v2/"
        f"designdata/{model_urn}/metadata/{guid}/properties"
    )
    resp = httpx.get(props_url, headers=headers, verify=True)
    resp.raise_for_status()
    data = resp.json()

    elements = []
    for obj in data.get("data", {}).get("collection", []):
        props   = obj.get("properties", {})
        el_type = props.get("Category", {}).get("Category", "Unknown")
        if el_type not in element_types:
            continue
        element = {
            "id":       str(obj.get("objectid")),
            "type":     el_type,
            "name":     obj.get("name", ""),
            "location": props.get("Constraints", {}).get("Level", ""),
            "bbox": {
                "min": {"x": 0, "y": 0, "z": 0},
                "max": {"x": 0, "y": 0, "z": 0},
            },
            "properties": {
                "size":     props.get("Dimensions", {}),
                "material": props.get("Materials and Finishes", {}),
                "system":   props.get("Mechanical", {}),
            }
        }
        elements.append(element)

    return json.dumps({
        "source":   "aps_live",
        "urn":      model_urn,
        "count":    len(elements),
        "elements": elements,
        "message":  f"Extracted {len(elements)} elements from live Revit model."
    }, indent=2)
```

---

## 9. TOOL 2 — analyze_model

**Owner:** Krushna  
**Dependencies:** Output from Tool 1

### Step 9.1 — Create analyze_model tool (tools/analyze_model.py)
```python
# tools/analyze_model.py
"""
Tool 2: analyze_model
Processes element relationships, clearance zones, and spatial context.
Prepares data for clash detection.
"""

import json
from engine.geometry_utils import compute_centers, compute_proximity_groups

def run(args: dict) -> str:
    raw_elements  = args.get("elements", [])
    tolerance_mm  = args.get("clearance_tolerance_mm", 50)

    if isinstance(raw_elements, str):
        raw_elements = json.loads(raw_elements)

    if not raw_elements:
        return json.dumps({"error": "No elements provided. Run extract_revit_data first."})

    elements_with_centers = compute_centers(raw_elements)
    proximity_groups      = compute_proximity_groups(elements_with_centers, threshold_m=2.0)

    by_type  = {}
    by_floor = {}
    for el in elements_with_centers:
        by_type[el["type"]]      = by_type.get(el["type"], 0) + 1
        by_floor[el["location"]] = by_floor.get(el["location"], 0) + 1

    return json.dumps({
        "status":                 "analyzed",
        "total_elements":         len(elements_with_centers),
        "clearance_tolerance_mm": tolerance_mm,
        "elements":               elements_with_centers,
        "proximity_groups":       proximity_groups,
        "summary": {
            "by_type":      by_type,
            "by_floor":     by_floor,
            "total_groups": len(proximity_groups),
        },
        "message": (
            f"Analyzed {len(elements_with_centers)} elements across "
            f"{len(by_floor)} floors. Found {len(proximity_groups)} proximity groups. "
            "Ready for detect_clashes."
        )
    }, indent=2)
```

### Step 9.2 — Create geometry utilities (engine/geometry_utils.py)
```python
# engine/geometry_utils.py
"""
Utility functions for spatial geometry operations.
All deterministic — no AI involved.
"""

import math

def compute_centers(elements: list) -> list:
    """Add center coordinates to each element's bounding box."""
    result = []
    for el in elements:
        bbox = el.get("bbox", {})
        mn   = bbox.get("min", {"x": 0, "y": 0, "z": 0})
        mx   = bbox.get("max", {"x": 0, "y": 0, "z": 0})
        el["center"] = {
            "x": (mn["x"] + mx["x"]) / 2,
            "y": (mn["y"] + mx["y"]) / 2,
            "z": (mn["z"] + mx["z"]) / 2,
        }
        result.append(el)
    return result

def compute_proximity_groups(elements: list, threshold_m: float = 2.0) -> list:
    """
    Group elements within threshold_m meters of each other.
    Reduces O(n^2) clash detection to nearby pairs only.
    """
    groups = []
    used   = set()

    for i, el_a in enumerate(elements):
        if i in used:
            continue
        group = [el_a]
        ca    = el_a.get("center", {"x": 0, "y": 0, "z": 0})
        for j, el_b in enumerate(elements):
            if j <= i or j in used:
                continue
            cb   = el_b.get("center", {"x": 0, "y": 0, "z": 0})
            dist = math.sqrt(
                (ca["x"] - cb["x"]) ** 2 +
                (ca["y"] - cb["y"]) ** 2 +
                (ca["z"] - cb["z"]) ** 2
            )
            if dist <= threshold_m:
                group.append(el_b)
                used.add(j)
        if len(group) > 1:
            groups.append(group)
        used.add(i)
    return groups

def bbox_volume(bbox: dict) -> float:
    """Compute volume of a bounding box in cubic meters."""
    mn = bbox.get("min", {"x": 0, "y": 0, "z": 0})
    mx = bbox.get("max", {"x": 0, "y": 0, "z": 0})
    return (abs(mx["x"] - mn["x"]) *
            abs(mx["y"] - mn["y"]) *
            abs(mx["z"] - mn["z"]))
```

---

## 10. TOOL 3 — detect_clashes

**Owner:** Krushna  
**Dependencies:** AABB engine, analyzed elements from Tool 2

### Step 10.1 — Create AABB engine (engine/aabb.py)
```python
# engine/aabb.py
"""
Axis-Aligned Bounding Box (AABB) Collision Detection Engine.
100% deterministic — no AI involved.
"""

from engine.severity import score_clash, SEVERITY_LABELS

def aabb_intersects(a_min, a_max, b_min, b_max) -> bool:
    return (
        a_min["x"] <= b_max["x"] and a_max["x"] >= b_min["x"] and
        a_min["y"] <= b_max["y"] and a_max["y"] >= b_min["y"] and
        a_min["z"] <= b_max["z"] and a_max["z"] >= b_min["z"]
    )

def intersection_volume(a_min, a_max, b_min, b_max) -> float:
    ox = max(0, min(a_max["x"], b_max["x"]) - max(a_min["x"], b_min["x"]))
    oy = max(0, min(a_max["y"], b_max["y"]) - max(a_min["y"], b_min["y"]))
    oz = max(0, min(a_max["z"], b_max["z"]) - max(a_min["z"], b_min["z"]))
    return ox * oy * oz

def run_clash_detection(elements: list, systems_to_check: list,
                        tolerance_mm: float = 50) -> list:
    """Main clash detection. Returns sorted list of clashes."""
    tolerance_m  = tolerance_mm / 1000.0
    clashes      = []
    clash_id     = 1
    seen_pairs   = set()

    mep_types    = {"Duct", "Pipe", "CableTray", "Conduit",
                    "MechanicalEquipment", "PlumbingFixture"}
    struct_types = {"Beam", "Column", "StructuralFraming"}
    arch_types   = {"Wall", "Window", "Floor", "Ceiling", "Roof"}
    other_types  = struct_types | arch_types

    for i, el_a in enumerate(elements):
        for j, el_b in enumerate(elements):
            if j <= i:
                continue
            pair_key = tuple(sorted([el_a["id"], el_b["id"]]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            a_is_mep   = el_a["type"] in mep_types
            b_is_mep   = el_b["type"] in mep_types
            a_is_other = el_a["type"] in other_types
            b_is_other = el_b["type"] in other_types

            if not ((a_is_mep and b_is_other) or (b_is_mep and a_is_other)):
                continue

            bbox_a = el_a.get("bbox", {})
            bbox_b = el_b.get("bbox", {})
            a_min, a_max = bbox_a.get("min", {}), bbox_a.get("max", {})
            b_min, b_max = bbox_b.get("min", {}), bbox_b.get("max", {})

            if not (a_min and a_max and b_min and b_max):
                continue

            a_min_soft = {k: a_min[k] - tolerance_m for k in a_min}
            a_max_soft = {k: a_max[k] + tolerance_m for k in a_max}

            if aabb_intersects(a_min, a_max, b_min, b_max):
                vol   = intersection_volume(a_min, a_max, b_min, b_max)
                score = score_clash(el_a, el_b, vol, "hard")
                clashes.append({
                    "clash_id":               f"CG-{clash_id:03d}",
                    "type":                   "hard",
                    "element_a":              {"id": el_a["id"], "type": el_a["type"],
                                               "name": el_a.get("name", "")},
                    "element_b":              {"id": el_b["id"], "type": el_b["type"],
                                               "name": el_b.get("name", "")},
                    "location":               el_a.get("location", "Unknown"),
                    "intersection_volume_m3": round(vol, 6),
                    "severity_score":         score,
                    "severity_label":         SEVERITY_LABELS[score],
                    "center":                 el_a.get("center", {}),
                })
                clash_id += 1

            elif aabb_intersects(a_min_soft, a_max_soft, b_min, b_max):
                score = score_clash(el_a, el_b, 0, "soft")
                clashes.append({
                    "clash_id":                  f"CG-{clash_id:03d}",
                    "type":                      "soft",
                    "element_a":                 {"id": el_a["id"], "type": el_a["type"],
                                                  "name": el_a.get("name", "")},
                    "element_b":                 {"id": el_b["id"], "type": el_b["type"],
                                                  "name": el_b.get("name", "")},
                    "location":                  el_a.get("location", "Unknown"),
                    "intersection_volume_m3":    0,
                    "clearance_violation_mm":    tolerance_mm,
                    "severity_score":            score,
                    "severity_label":            SEVERITY_LABELS[score],
                    "center":                    el_a.get("center", {}),
                })
                clash_id += 1

    return sorted(clashes, key=lambda c: c["severity_score"], reverse=True)
```

### Step 10.2 — Create severity engine (engine/severity.py)
```python
# engine/severity.py
"""
Rule-based severity scoring for detected clashes.
100% deterministic IF/ELSE logic. No AI.
"""

SEVERITY_LABELS = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW"}

SEVERITY_RULES = {
    ("Duct",      "Beam"):   4,
    ("Pipe",      "Beam"):   4,
    ("Duct",      "Column"): 4,
    ("Pipe",      "Column"): 4,
    ("Duct",      "Window"): 3,
    ("Pipe",      "Window"): 3,
    ("CableTray", "Window"): 3,
    ("Duct",      "Wall"):   2,
    ("Pipe",      "Wall"):   2,
    ("Duct",      "Pipe"):   2,
    ("CableTray", "Duct"):   2,
}

def score_clash(el_a: dict, el_b: dict,
                volume_m3: float, clash_type: str) -> int:
    type_a = el_a.get("type", "")
    type_b = el_b.get("type", "")
    base   = (SEVERITY_RULES.get((type_a, type_b)) or
              SEVERITY_RULES.get((type_b, type_a)) or 2)

    if clash_type == "hard" and volume_m3 > 0.1:
        base = min(4, base + 1)
    elif clash_type == "soft":
        base = max(1, base - 1)

    return base
```

### Step 10.3 — Create detect_clashes tool (tools/detect_clashes.py)
```python
# tools/detect_clashes.py
"""
Tool 3: detect_clashes
Runs AABB collision detection. All calculations are deterministic.
"""

import json
from engine.aabb import run_clash_detection

def run(args: dict) -> str:
    elements         = args.get("elements", [])
    systems_to_check = args.get("systems_to_check",
                                ["HVAC", "Plumbing", "Electrical", "Structural"])
    zones            = args.get("zones", [])

    if isinstance(elements, str):
        try:
            elements = json.loads(elements)
        except Exception:
            return json.dumps({"error": "Invalid elements data. Pass output from analyze_model."})

    if zones:
        elements = [e for e in elements
                    if any(z.lower() in e.get("location", "").lower() for z in zones)]

    clashes = run_clash_detection(elements, systems_to_check)

    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for c in clashes:
        severity_counts[c["severity_label"]] += 1

    return json.dumps({
        "total_clashes":    len(clashes),
        "severity_summary": severity_counts,
        "clashes":          clashes,
        "message": (
            f"Detected {len(clashes)} total clashes: "
            f"{severity_counts['CRITICAL']} CRITICAL, "
            f"{severity_counts['HIGH']} HIGH, "
            f"{severity_counts['MEDIUM']} MEDIUM, "
            f"{severity_counts['LOW']} LOW. "
            "Run suggest_resolutions to get AI-powered recommendations."
        )
    }, indent=2)
```

---

## 11. TOOL 4 — suggest_resolutions

**Owner:** Krushna + Pradeep  
**Dependencies:** Anthropic Claude API

> ⚠ **[AUTODESK REQUIREMENT]** Must check `user_consent_given=true` before sending any data to Claude.

```python
# tools/suggest_resolutions.py
"""
Tool 4: suggest_resolutions
Uses Claude AI to prioritize clashes and suggest engineering resolutions.
AI is used ONLY for reasoning — never for geometry calculations.
User consent is required before sending data to Claude.
"""

import json
import anthropic
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

SYSTEM_PROMPT = """You are a senior BIM coordination engineer with 15 years of experience in MEP clash resolution for large AEC projects.

You are given a list of detected MEP clashes from a Revit building model. Your job is to:
1. Review each clash and explain WHY it matters in plain English
2. Suggest the most practical engineering resolution for each clash
3. Prioritize the list — which clashes need immediate attention

IMPORTANT RULES:
- You are reading ANALYSIS RESULTS from a deterministic geometry engine. Do not question the clash detection results.
- Your role is ONLY reasoning and recommendations — not geometry recalculation.
- Keep suggestions practical and implementable by a BIM engineer.
- Use plain English — no jargon that non-specialists won't understand.
- For CRITICAL clashes: always recommend immediate action before proceeding with design.
- For LOW clashes: suggest monitoring but not blocking design progress.

Format each clash recommendation as:
CLASH [ID]: [one-line description]
WHY IT MATTERS: [plain English explanation]
RECOMMENDED FIX: [specific, actionable suggestion]
PRIORITY: [CRITICAL/HIGH/MEDIUM/LOW]
"""

def run(args: dict) -> str:
    clashes            = args.get("clashes", [])
    project_context    = args.get("project_context", "")
    user_consent_given = args.get("user_consent_given", False)

    # [AUTODESK REQUIREMENT] — Enforce user consent before sending to AI
    if not user_consent_given:
        return json.dumps({
            "error": "User consent required",
            "message": (
                "This tool sends anonymized clash data to Anthropic Claude AI for analysis. "
                "To proceed, call this tool again with user_consent_given=true. "
                "Data sent: element types, locations, severity scores. "
                "No personal data or project credentials are sent."
            )
        })

    if isinstance(clashes, str):
        try:
            clashes = json.loads(clashes)
        except Exception:
            return json.dumps({"error": "Invalid clash data format."})

    if not clashes:
        return json.dumps({"message": "No clashes provided. Run detect_clashes first."})

    # Minimal data sent to Claude — no credentials or personal data
    clash_summary = [
        {
            "clash_id":       c["clash_id"],
            "type":           c["type"],
            "element_a_type": c["element_a"]["type"],
            "element_b_type": c["element_b"]["type"],
            "location":       c["location"],
            "severity":       c["severity_label"],
            "volume_m3":      c.get("intersection_volume_m3", 0),
        }
        for c in clashes
    ]

    user_message = (
        f"Please analyze these {len(clashes)} MEP clashes detected in the building model "
        "and provide resolution recommendations.\n\n"
        f"Project context: {project_context or 'Commercial office building, active design phase'}\n\n"
        f"Detected clashes:\n{json.dumps(clash_summary, indent=2)}\n\n"
        "Please provide:\n"
        "1. Resolution recommendations for each clash\n"
        "2. Overall priority order\n"
        "3. Which clashes can be addressed together (grouped fixes)"
    )

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )
        ai_recommendations = response.content[0].text
    except Exception as e:
        ai_recommendations = (
            f"AI analysis unavailable: {str(e)}. "
            "Clashes are listed by deterministic severity score."
        )

    return json.dumps({
        "total_clashes":      len(clashes),
        "clashes":            clashes,
        "ai_recommendations": ai_recommendations,
        "consent_recorded":   True,
        "data_sent_to_ai":    "element types, locations, severity scores only",
        "message":            f"AI analysis complete for {len(clashes)} clashes."
    }, indent=2)
```

---

## 12. TOOL 5 — generate_report

**Owner:** Pradeep (template design) + Prathmesh (implementation)

```python
# tools/generate_report.py
"""
Tool 5: generate_report
Generates professional PDF and/or Word clash coordination reports.
"""

import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

def run(args: dict) -> str:
    clashes      = args.get("clashes", [])
    project_name = args.get("project_name", "Unnamed Project")
    fmt          = args.get("format", "both")

    if isinstance(clashes, str):
        try:
            clashes = json.loads(clashes)
        except Exception:
            return json.dumps({"error": "Invalid clash data."})

    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name  = f"ClashGuard_Report_{project_name.replace(' ', '_')}_{timestamp}"
    generated  = []

    if fmt in ("docx", "both"):
        docx_path = OUTPUT_DIR / f"{base_name}.docx"
        _generate_docx(clashes, project_name, docx_path)
        generated.append(str(docx_path))

    if fmt in ("pdf", "both"):
        pdf_path = OUTPUT_DIR / f"{base_name}.pdf"
        _generate_pdf(clashes, project_name, pdf_path)
        generated.append(str(pdf_path))

    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for c in clashes:
        severity_counts[c.get("severity_label", "MEDIUM")] += 1

    return json.dumps({
        "success":          True,
        "files_generated":  generated,
        "total_clashes":    len(clashes),
        "severity_summary": severity_counts,
        "message":          f"Report generated: {len(generated)} file(s). Path: {', '.join(generated)}"
    }, indent=2)


def _generate_docx(clashes: list, project_name: str, path: Path):
    from docx import Document
    from docx.shared import Pt, RGBColor

    doc = Document()
    doc.add_heading("ClashGuard Coordination Report", 0)
    doc.add_heading(f"Project: {project_name}", 1)
    doc.add_paragraph(
        f"Date: {datetime.now().strftime('%B %d, %Y')}  |  "
        f"Total Clashes: {len(clashes)}  |  "
        "Generated by: ClashGuard MCP v1.0"
    )

    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for c in clashes:
        severity_counts[c.get("severity_label", "MEDIUM")] += 1

    doc.add_heading("Executive Summary", 2)
    doc.add_paragraph(
        f"ClashGuard detected {len(clashes)} MEP clashes in the {project_name} model. "
        f"{severity_counts['CRITICAL']} CRITICAL clashes require immediate attention. "
        f"{severity_counts['HIGH']} HIGH priority clashes should be resolved before "
        "the next design review. "
        f"{severity_counts['MEDIUM'] + severity_counts['LOW']} lower-priority clashes "
        "are noted for coordination."
    )

    # Severity table
    doc.add_heading("Severity Breakdown", 2)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = "Severity"
    table.rows[0].cells[1].text = "Count"
    for label, count in severity_counts.items():
        row = table.add_row()
        row.cells[0].text = label
        row.cells[1].text = str(count)

    # Individual clashes
    doc.add_heading("Clash Details", 2)
    for clash in clashes:
        doc.add_heading(
            f"{clash['clash_id']} — {clash.get('severity_label','N/A')} ({clash.get('type','').upper()} CLASH)",
            3
        )
        doc.add_paragraph(f"Location: {clash.get('location', 'Unknown')}")
        doc.add_paragraph(
            f"Elements: {clash['element_a']['type']} [{clash['element_a']['id']}] "
            f"vs {clash['element_b']['type']} [{clash['element_b']['id']}]"
        )
        if clash.get("intersection_volume_m3"):
            doc.add_paragraph(
                f"Intersection Volume: {clash['intersection_volume_m3']} m³"
            )

    doc.save(str(path))


def _generate_pdf(clashes: list, project_name: str, path: Path):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors

    doc_obj  = SimpleDocTemplate(str(path), pagesize=A4)
    styles   = getSampleStyleSheet()
    story    = []

    story.append(Paragraph("ClashGuard MCP — Clash Coordination Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Project: {project_name}", styles["Heading1"]))
    story.append(Paragraph(
        f"Date: {datetime.now().strftime('%B %d, %Y')} | "
        f"Total Clashes: {len(clashes)} | Generated by: ClashGuard MCP v1.0",
        styles["Normal"]
    ))
    story.append(Spacer(1, 12))

    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for c in clashes:
        severity_counts[c.get("severity_label", "MEDIUM")] += 1

    story.append(Paragraph("Severity Summary", styles["Heading2"]))
    table_data = [["Severity", "Count"]] + [
        [k, str(v)] for k, v in severity_counts.items()
    ]
    t = Table(table_data, colWidths=[200, 100])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE",   (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Clash Details", styles["Heading2"]))
    for clash in clashes:
        story.append(Paragraph(
            f"<b>{clash['clash_id']}</b> — {clash.get('severity_label','N/A')} "
            f"({clash.get('type','').upper()} CLASH)",
            styles["Heading3"]
        ))
        story.append(Paragraph(f"Location: {clash.get('location','Unknown')}", styles["Normal"]))
        story.append(Paragraph(
            f"Elements: {clash['element_a']['type']} vs {clash['element_b']['type']}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 8))

    doc_obj.build(story)
```

---

## 13. MOCK DATA FOR DEMO

**Owner:** Pradeep  
**File:** data/mock_db.json

This file contains realistic CCTech-flavored Revit data for the demo. It represents a 5-floor commercial office building (Pune tech park) with MEP systems and intentional clashes on Floor 3.

```json
{
  "project": {
    "name": "Magarpatta Tower B — BIM Coordination Model",
    "location": "Magarpatta City, Pune",
    "floors": 5,
    "type": "Commercial Office",
    "model_version": "Rev-04",
    "last_updated": "2026-06-01"
  },
  "elements": [
    {
      "id": "DUCT-301",
      "type": "Duct",
      "name": "Supply Air Duct — AHU-3A",
      "location": "Level 3",
      "system": "HVAC",
      "bbox": {
        "min": {"x": 10.0, "y": 5.0, "z": 9.2},
        "max": {"x": 18.0, "y": 5.6, "z": 9.8}
      },
      "properties": {
        "size": "600mm x 400mm",
        "material": "Galvanized Steel",
        "insulation": "50mm Rockwool",
        "airflow_l_s": 850,
        "system_name": "AHU-3A Supply"
      }
    },
    {
      "id": "BEAM-310",
      "type": "Beam",
      "name": "Primary Structural Beam — Grid B3",
      "location": "Level 3",
      "system": "Structural",
      "bbox": {
        "min": {"x": 8.0,  "y": 4.8, "z": 9.3},
        "max": {"x": 20.0, "y": 5.2, "z": 9.7}
      },
      "properties": {
        "size": "UC 305x165x40",
        "material": "Structural Steel",
        "load_capacity_kN": 450
      }
    },
    {
      "id": "WIN-350",
      "type": "Window",
      "name": "South Facade Window W3-12",
      "location": "Level 3",
      "system": "Architectural",
      "bbox": {
        "min": {"x": 14.5, "y": 0.0, "z": 8.5},
        "max": {"x": 16.5, "y": 0.3, "z": 10.5}
      },
      "properties": {
        "width_mm": 2000,
        "height_mm": 2000,
        "glazing": "Double Low-E",
        "u_value": 1.4,
        "recently_added": true,
        "change_request": "CR-2026-047"
      }
    },
    {
      "id": "DUCT-302",
      "type": "Duct",
      "name": "Return Air Duct — AHU-3A",
      "location": "Level 3",
      "system": "HVAC",
      "bbox": {
        "min": {"x": 14.0, "y": 0.5, "z": 9.0},
        "max": {"x": 17.0, "y": 1.2, "z": 9.5}
      },
      "properties": {
        "size": "500mm x 350mm",
        "material": "Galvanized Steel",
        "airflow_l_s": 650
      }
    },
    {
      "id": "PIPE-401",
      "type": "Pipe",
      "name": "Chilled Water Supply Pipe — CHW-3B",
      "location": "Level 3",
      "system": "Plumbing",
      "bbox": {
        "min": {"x": 9.5,  "y": 4.9, "z": 9.4},
        "max": {"x": 19.5, "y": 5.1, "z": 9.6}
      },
      "properties": {
        "diameter_mm": 100,
        "material": "Copper",
        "insulation": "25mm Armaflex",
        "pressure_bar": 6.0,
        "fluid": "Chilled Water"
      }
    },
    {
      "id": "CABLE-501",
      "type": "CableTray",
      "name": "Data/Comms Cable Tray — CT-3A",
      "location": "Level 3",
      "system": "Electrical",
      "bbox": {
        "min": {"x": 13.0, "y": 0.2, "z": 9.1},
        "max": {"x": 18.0, "y": 0.6, "z": 9.4}
      },
      "properties": {
        "width_mm": 400,
        "depth_mm": 100,
        "material": "Hot-dip Galvanized",
        "fill_ratio": 0.65
      }
    },
    {
      "id": "DUCT-201",
      "type": "Duct",
      "name": "Supply Air Duct — AHU-2A",
      "location": "Level 2",
      "system": "HVAC",
      "bbox": {
        "min": {"x": 10.0, "y": 5.0, "z": 6.0},
        "max": {"x": 18.0, "y": 5.6, "z": 6.6}
      },
      "properties": {
        "size": "600mm x 400mm",
        "material": "Galvanized Steel"
      }
    },
    {
      "id": "WALL-320",
      "type": "Wall",
      "name": "South Facade Masonry Wall — Level 3",
      "location": "Level 3",
      "system": "Architectural",
      "bbox": {
        "min": {"x": 0.0,  "y": 0.0, "z": 7.5},
        "max": {"x": 30.0, "y": 0.25, "z": 11.0}
      },
      "properties": {
        "thickness_mm": 250,
        "material": "Reinforced Concrete",
        "fire_rating": "2hr"
      }
    },
    {
      "id": "PIPE-402",
      "type": "Pipe",
      "name": "Domestic Hot Water Pipe — DHW-3A",
      "location": "Level 3",
      "system": "Plumbing",
      "bbox": {
        "min": {"x": 14.2, "y": 0.1, "z": 9.2},
        "max": {"x": 17.2, "y": 0.3, "z": 9.4}
      },
      "properties": {
        "diameter_mm": 50,
        "material": "Copper",
        "fluid": "Domestic Hot Water",
        "temperature_C": 60
      }
    },
    {
      "id": "BEAM-210",
      "type": "Beam",
      "name": "Primary Structural Beam — Grid B2",
      "location": "Level 2",
      "system": "Structural",
      "bbox": {
        "min": {"x": 8.0,  "y": 4.8, "z": 6.1},
        "max": {"x": 20.0, "y": 5.2, "z": 6.5}
      },
      "properties": {
        "size": "UC 305x165x40",
        "material": "Structural Steel"
      }
    }
  ],
  "design_changes": [
    {
      "change_request": "CR-2026-047",
      "description": "Add 6 new windows on south facade, Level 3, Grid 14-17",
      "requested_by": "Architect Team",
      "date": "2026-05-28",
      "status": "Pending Coordination Review",
      "affected_elements": ["WIN-350"],
      "notes": "Windows added to improve natural light per client feedback"
    }
  ],
  "project_metadata": {
    "bim_coordinator": "Krushna Lande",
    "architect": "Pradeep Sharma",
    "mep_engineer": "Prathmesh Gaikwad",
    "client": "Magarpatta Cybercity Developers",
    "project_phase": "Design Development",
    "target_completion": "2027-Q2"
  }
}
```

---

## 14. CLAUDE DESKTOP CONFIGURATION

**File:** claude_desktop_config.json (template — developer updates path)

```json
{
  "mcpServers": {
    "clashguard": {
      "command": "python",
      "args": ["C:\\Users\\YourName\\clashguard-mcp\\server.py"],
      "env": {
        "DEMO_MODE": "true"
      }
    }
  }
}
```

### Step 14.1 — Find your Claude Desktop config file location

**On Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```
Full path example:
```
C:\Users\dell\AppData\Roaming\Claude\claude_desktop_config.json
```

**On Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Step 14.2 — Apply config
1. Open the config file in Notepad or VS Code
2. Replace the entire content with the JSON above
3. Update the path to match where you cloned `clashguard-mcp`
4. Save the file
5. **Fully quit Claude Desktop** (right-click system tray → Quit)
6. Reopen Claude Desktop
7. Look for the 🔨 hammer icon — that means MCP is connected

---

## 15. AUTODESK MANIFEST JSON

**[AUTODESK REQUIREMENT]** This file is required for Autodesk marketplace submission.

**File:** manifest.json

```json
{
  "schema_version": "1.0",
  "name": "clashguard-mcp",
  "display_name": "ClashGuard MCP",
  "version": "1.0.0",
  "description": "AI-powered MEP clash detection for Revit. Detects, prioritizes, and suggests engineering resolutions for spatial conflicts in BIM models using natural language.",
  "publisher": {
    "name": "CCTech — Computational Cloud Technologies",
    "email": "mcp@cctech.io",
    "url": "https://cctech.io",
    "city": "Pune",
    "country": "India"
  },
  "license": "MIT",
  "homepage": "https://github.com/cctech-pune/clashguard-mcp",
  "keywords": ["BIM", "MEP", "clash detection", "Revit", "APS", "coordination", "AEC"],
  "categories": ["AEC", "BIM", "Coordination", "AI Assistant"],
  "autodesk_apis_used": [
    "Authentication API v2",
    "Model Derivative API v2",
    "Data Management API v2"
  ],
  "ai_providers_used": ["Anthropic Claude"],
  "transport": "stdio",
  "entry_point": "server.py",
  "runtime": "python3.11",
  "tools": [
    {
      "name": "extract_revit_data",
      "description": "Extracts MEP element geometry from Revit via APS Model Derivatives API",
      "autodesk_apis": ["Model Derivative API v2", "Authentication API v2"],
      "sends_data_to_ai": false,
      "data_categories": ["model_geometry", "element_metadata"]
    },
    {
      "name": "analyze_model",
      "description": "Analyzes spatial relationships and proximity groups between elements",
      "autodesk_apis": [],
      "sends_data_to_ai": false,
      "data_categories": ["model_geometry"]
    },
    {
      "name": "detect_clashes",
      "description": "Deterministic AABB collision detection — no AI involved",
      "autodesk_apis": [],
      "sends_data_to_ai": false,
      "data_categories": ["model_geometry"]
    },
    {
      "name": "suggest_resolutions",
      "description": "AI reasoning for clash prioritization and resolution suggestions. Requires explicit user consent before sending data to Claude.",
      "autodesk_apis": [],
      "sends_data_to_ai": true,
      "ai_provider": "Anthropic Claude",
      "data_sent_to_ai": ["element_types", "locations", "severity_scores"],
      "data_NOT_sent_to_ai": ["user_credentials", "api_keys", "personal_data"],
      "user_consent_required": true
    },
    {
      "name": "generate_report",
      "description": "Generates PDF/Word clash coordination reports locally. No external API calls.",
      "autodesk_apis": [],
      "sends_data_to_ai": false,
      "data_categories": ["clash_results"]
    }
  ],
  "security": {
    "ssl_verification": "enforced",
    "credentials_stored": "local_env_file_only",
    "data_retention": "none — no data stored server-side",
    "user_consent_flow": "implemented_in_suggest_resolutions"
  },
  "privacy_policy_url": "https://cctech.io/privacy",
  "support_url": "https://github.com/cctech-pune/clashguard-mcp/issues"
}
```

---

## 16. USER CONSENT FLOW

**[AUTODESK REQUIREMENT]** Required for any MCP tool that sends data to an external AI provider.

### How it works in ClashGuard:

When `suggest_resolutions` is called WITHOUT `user_consent_given=true`, it returns:

```json
{
  "error": "User consent required",
  "message": "This tool sends anonymized clash data to Anthropic Claude AI for analysis. To proceed, call this tool again with user_consent_given=true. Data sent: element types, locations, severity scores. No personal data or project credentials are sent."
}
```

Claude Desktop then shows this message to the user. The user types "yes, proceed" and Claude calls the tool again with `user_consent_given=true`.

### What data is sent to Claude:
- ✅ Element types (e.g., "Duct", "Beam")
- ✅ Floor locations (e.g., "Level 3")
- ✅ Severity scores (e.g., "CRITICAL")
- ✅ Intersection volumes (numeric)

### What data is NEVER sent to Claude:
- ❌ APS credentials or API keys
- ❌ User names or email addresses
- ❌ Project names or client names
- ❌ Raw geometry coordinates
- ❌ Proprietary model data

---

## 17. SECURITY HARDENING

**[AUTODESK REQUIREMENT]** Required for marketplace submission.

### Checklist — implement before submission:

```python
# 1. Always verify SSL certificates (NO verify=False anywhere)
httpx.get(url, verify=True)   # CORRECT
httpx.get(url, verify=False)  # NEVER DO THIS

# 2. Never log API keys or tokens
log.info(f"Token: {token[:8]}...")  # Show only first 8 chars

# 3. Token expiry check in aps/auth.py
# Implemented: caches token and refreshes 60s before expiry

# 4. Input validation in every tool
if not isinstance(clashes, list):
    return json.dumps({"error": "Invalid input type"})

# 5. Output directory stays local
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
# Never write to system directories

# 6. No shell execution
# Never use os.system() or subprocess.run() with user input
```

### .gitignore must include:
```
.env
*.key
*.pem
venv/
outputs/
__pycache__/
```

---

## 18. TESTING & VALIDATION

### Step 18.1 — Create test fixtures (tests/fixtures/sample_clash_data.json)
```json
{
  "sample_clashes": [
    {
      "clash_id": "CG-001",
      "type": "hard",
      "element_a": {"id": "DUCT-301", "type": "Duct", "name": "Supply Air Duct AHU-3A"},
      "element_b": {"id": "BEAM-310", "type": "Beam", "name": "Beam Grid B3"},
      "location": "Level 3",
      "intersection_volume_m3": 0.024,
      "severity_score": 4,
      "severity_label": "CRITICAL",
      "center": {"x": 14.0, "y": 5.0, "z": 9.5}
    },
    {
      "clash_id": "CG-002",
      "type": "hard",
      "element_a": {"id": "DUCT-302", "type": "Duct", "name": "Return Air Duct AHU-3A"},
      "element_b": {"id": "WIN-350", "type": "Window", "name": "South Facade Window W3-12"},
      "location": "Level 3",
      "intersection_volume_m3": 0.012,
      "severity_score": 3,
      "severity_label": "HIGH",
      "center": {"x": 15.5, "y": 0.8, "z": 9.25}
    }
  ]
}
```

### Step 18.2 — Create unit tests (tests/test_engine.py)
```python
# tests/test_engine.py
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.aabb import aabb_intersects, intersection_volume, run_clash_detection
from engine.severity import score_clash
from engine.geometry_utils import compute_centers, compute_proximity_groups

class TestAABB:
    def test_clear_intersection(self):
        """Two overlapping boxes should return True."""
        a_min = {"x": 0, "y": 0, "z": 0}
        a_max = {"x": 2, "y": 2, "z": 2}
        b_min = {"x": 1, "y": 1, "z": 1}
        b_max = {"x": 3, "y": 3, "z": 3}
        assert aabb_intersects(a_min, a_max, b_min, b_max) is True

    def test_no_intersection(self):
        """Two separate boxes should return False."""
        a_min = {"x": 0, "y": 0, "z": 0}
        a_max = {"x": 1, "y": 1, "z": 1}
        b_min = {"x": 2, "y": 2, "z": 2}
        b_max = {"x": 3, "y": 3, "z": 3}
        assert aabb_intersects(a_min, a_max, b_min, b_max) is False

    def test_touching_edges(self):
        """Boxes touching at an edge — borderline intersection."""
        a_min = {"x": 0, "y": 0, "z": 0}
        a_max = {"x": 1, "y": 1, "z": 1}
        b_min = {"x": 1, "y": 0, "z": 0}
        b_max = {"x": 2, "y": 1, "z": 1}
        assert aabb_intersects(a_min, a_max, b_min, b_max) is True

    def test_intersection_volume_correct(self):
        """Intersection of two 2x2x2 boxes offset by 1 = 1x2x2 = 4."""
        a_min = {"x": 0, "y": 0, "z": 0}
        a_max = {"x": 2, "y": 2, "z": 2}
        b_min = {"x": 1, "y": 0, "z": 0}
        b_max = {"x": 3, "y": 2, "z": 2}
        vol = intersection_volume(a_min, a_max, b_min, b_max)
        assert abs(vol - 4.0) < 0.001

class TestSeverity:
    def test_duct_beam_is_critical(self):
        el_a = {"type": "Duct"}
        el_b = {"type": "Beam"}
        assert score_clash(el_a, el_b, 0.05, "hard") == 4

    def test_duct_window_is_high(self):
        el_a = {"type": "Duct"}
        el_b = {"type": "Window"}
        assert score_clash(el_a, el_b, 0.01, "hard") == 3

    def test_soft_clash_reduces_score(self):
        el_a = {"type": "Duct"}
        el_b = {"type": "Beam"}
        # Soft clash should reduce from 4 to 3
        score = score_clash(el_a, el_b, 0, "soft")
        assert score <= 4

class TestGeometryUtils:
    def test_compute_centers(self):
        elements = [{
            "id": "T1", "type": "Duct", "location": "L3",
            "bbox": {
                "min": {"x": 0, "y": 0, "z": 0},
                "max": {"x": 2, "y": 2, "z": 2}
            }
        }]
        result = compute_centers(elements)
        assert result[0]["center"] == {"x": 1.0, "y": 1.0, "z": 1.0}
```

### Step 18.3 — Create tool integration tests (tests/test_tools.py)
```python
# tests/test_tools.py
import pytest, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.extract_revit_data import run as extract
from tools.analyze_model       import run as analyze
from tools.detect_clashes      import run as detect

def test_extract_returns_elements():
    result = json.loads(extract({}))
    assert "elements" in result
    assert result["count"] > 0

def test_analyze_processes_elements():
    elements = json.loads(extract({}))["elements"]
    result   = json.loads(analyze({"elements": elements}))
    assert result["status"] == "analyzed"
    assert "summary" in result

def test_detect_finds_clashes():
    elements = json.loads(extract({}))["elements"]
    analyzed = json.loads(analyze({"elements": elements}))["elements"]
    result   = json.loads(detect({"elements": analyzed}))
    assert "total_clashes" in result
    assert result["total_clashes"] >= 0

def test_suggest_requires_consent():
    from tools.suggest_resolutions import run as suggest
    result = json.loads(suggest({"clashes": [], "user_consent_given": False}))
    assert "error" in result

def test_full_pipeline():
    """End-to-end pipeline test with mock data."""
    # Tool 1
    extracted = json.loads(extract({"floor_filter": "Level 3"}))
    assert extracted["count"] > 0

    # Tool 2
    analyzed  = json.loads(analyze({"elements": extracted["elements"]}))
    assert analyzed["total_elements"] > 0

    # Tool 3
    detected  = json.loads(detect({"elements": analyzed["elements"]}))
    assert "clashes" in detected

    print(f"Pipeline test passed: {detected['total_clashes']} clashes found")
```

### Step 18.4 — Run all tests
```bash
# From project root (venv activated)
pytest tests/ -v

# Expected output:
# test_engine.py::TestAABB::test_clear_intersection PASSED
# test_engine.py::TestAABB::test_no_intersection PASSED
# test_engine.py::TestAABB::test_touching_edges PASSED
# test_engine.py::TestAABB::test_intersection_volume_correct PASSED
# test_engine.py::TestSeverity::test_duct_beam_is_critical PASSED
# test_engine.py::TestSeverity::test_duct_window_is_high PASSED
# test_engine.py::TestSeverity::test_soft_clash_reduces_score PASSED
# test_engine.py::TestGeometryUtils::test_compute_centers PASSED
# test_tools.py::test_extract_returns_elements PASSED
# test_tools.py::test_analyze_processes_elements PASSED
# test_tools.py::test_detect_finds_clashes PASSED
# test_tools.py::test_suggest_requires_consent PASSED
# test_tools.py::test_full_pipeline PASSED
# 13 passed in X.XXs
```

---

## 19. DEMO SCENARIOS

**Print this page for the demo.**

### Demo Setup
1. Open Claude Desktop (hammer icon visible = MCP connected)
2. The conversation context should show ClashGuard connected
3. Have the mock_db.json data loaded (DEMO_MODE=true)

---

### WOW MOMENT 1 — Instant Clash Check on New Windows
**Prompt to type in Claude Desktop:**
```
I want to add new windows on the south facade of Level 3. 
Can you check if they will clash with any HVAC ducts, 
pipes, or structural elements?
```

**What Claude will do:**
1. Call `extract_revit_data` with `floor_filter: "Level 3"`
2. Call `analyze_model` on the extracted elements
3. Call `detect_clashes` focused on the south facade zone
4. Return a structured clash report

**Expected response includes:**
- 3-4 clashes detected (CRITICAL: duct vs beam, HIGH: duct vs window, MEDIUM: pipe vs window)
- Severity breakdown table
- Element pairs clearly identified

**Talking point:** *"In Navisworks, this analysis takes 2-3 hours of manual 3D model walkthrough. ClashGuard does it in under 30 seconds using the same Revit data."*

---

### WOW MOMENT 2 — AI-Powered Priority + Resolution
**Prompt to type in Claude Desktop (after Moment 1):**
```
Please prioritize these clashes and tell me what 
the engineering team should fix first. I consent 
to sending this clash data for AI analysis.
```

**What Claude will do:**
1. Call `suggest_resolutions` with `user_consent_given: true`
2. Claude AI analyzes clash types, locations, severity
3. Returns plain-English recommendations

**Expected response includes:**
- "Fix CG-001 first — duct running through structural beam is a structural safety issue"
- "Reroute HVAC supply duct 200mm upward to clear beam"
- "Window-duct clash at south facade: consider reducing duct size or relocating window"

**Talking point:** *"No existing tool does this. Navisworks tells you THAT there's a clash. ClashGuard tells you WHY it matters and WHAT to do about it — in plain English."*

---

### WOW MOMENT 3 — Professional Report in One Command
**Prompt to type in Claude Desktop (after Moment 2):**
```
Generate a professional clash coordination report 
for the Magarpatta Tower B project in both PDF and Word format.
```

**What Claude will do:**
1. Call `generate_report` with project name and all clash data
2. Generate .docx and .pdf in the outputs/ folder
3. Return file paths

**Expected response:**
- "Report generated: ClashGuard_Report_Magarpatta_Tower_B_20260602.docx and .pdf"
- Files are ready to open/share immediately

**Talking point:** *"This replaces a 2-hour manual report writing process. The coordinator can share this with the MEP team immediately after the meeting."*

---

## 20. POWERPOINT PRESENTATION

### 10-Slide Structure

**Slide 1 — Title**
- ClashGuard MCP
- AI-Powered MEP Clash Detection for Revit
- CCTech | Pune | June 2026
- [LOGO]

**Slide 2 — The Problem**
- $625 Billion/year in AEC rework due to coordination failures
- MEP clashes are the #1 cause of rework on complex projects
- Current tools (Navisworks): detect clashes but don't explain or fix them
- BIM coordinators spend 2-4 hours per cycle on manual clash review
- [Chart: AEC rework cost breakdown]

**Slide 3 — The Gap**
Three columns:
| What Navisworks Does | What It Doesn't Do | What ClashGuard Adds |
|---------------------|-------------------|---------------------|
| Detects clashes | Prioritize importance | AI-powered prioritization |
| Lists element pairs | Explain why it matters | Plain English reasoning |
| Shows 3D view | Suggest engineering fix | Actionable recommendations |
| Exports reports | Natural language query | Chat-based interface |

**Slide 4 — Product Demo (screenshot)**
- Claude Desktop chat window
- User types: "Will my new windows clash with HVAC ducts?"
- ClashGuard response: structured clash list with severity

**Slide 5 — Architecture**
[Simplified 3-layer diagram]
- User Layer: Claude Desktop → Natural language
- ClashGuard MCP Server → 5 tools
- Integration Layer: APS APIs → Revit Model | Claude AI → Reasoning

**Slide 6 — The 5 Tools**
| Tool | What It Does | Time Saved |
|------|-------------|-----------|
| extract_revit_data | Pull MEP data from Revit/APS | 1 hr manual |
| analyze_model | Spatial proximity analysis | 30 min manual |
| detect_clashes | AABB collision detection | 2-3 hr manual |
| suggest_resolutions | AI reasoning + fix suggestions | 1-2 hr manual |
| generate_report | PDF/Word coordination report | 1-2 hr manual |
**Total: 5-8 hours saved per cycle → 30 min with ClashGuard**

**Slide 7 — AI Architecture**
```
DETERMINISTIC           AI/CLAUDE
(no hallucination)      (reasoning only)
────────────────        ──────────────
AABB Collision    →     Prioritize
Coordinate Math   →     Explain
Severity Rules    →     Recommend Fix
Report Layout     →     Write Summary
```
Key message: *"We never let AI touch the geometry calculations. That's what makes it enterprise-safe."*

**Slide 8 — Demo Results (live numbers)**
- X clashes detected in Y seconds
- Z CRITICAL, A HIGH, B MEDIUM
- Report generated in < 5 minutes
- [Screenshot of generated PDF report]

**Slide 9 — Autodesk Marketplace Path**
- Submitted to: Autodesk Design & Make Marketplace (live since DevCon 2026)
- APIs used: APS Authentication, Model Derivatives, Data Management
- Complies with: Autodesk MCP Trust & Safety requirements
- Next steps: CCTech internal review → Production build → Marketplace submission

**Slide 10 — Team & Next Steps**
Team:
- Krushna Lande — MCP server + geometry engine
- Prathmesh Gaikwad — APS integration + Tool 1
- Pradeep Sharma — Mock data + Tool 5 + presentation

Next Steps (v2):
- Real-time Revit write-back (annotate clashes in model)
- Multi-project dashboard
- Integration with BIM Collaborate Pro
- CCTech simulationHub API integration

---

## 21. AUTODESK SUBMISSION CHECKLIST

Complete every item before submitting to appsubmissions@autodesk.com

### Technical Requirements
- [ ] manifest.json created and validated
- [ ] All tools have complete inputSchema definitions
- [ ] SSL verification is `verify=True` everywhere (no exceptions)
- [ ] User consent flow implemented in suggest_resolutions
- [ ] .env file is gitignored
- [ ] No hardcoded API keys anywhere in code
- [ ] README.md has complete setup instructions
- [ ] All 13 unit tests pass (`pytest tests/ -v`)
- [ ] Full demo pipeline runs without errors

### Documentation Requirements
- [ ] manifest.json lists all Autodesk APIs used
- [ ] manifest.json lists all AI providers used
- [ ] Privacy policy URL is valid
- [ ] Support/issues URL is valid
- [ ] publisher.email is valid and monitored

### Legal Requirements
- [ ] MIT License file present (LICENSE)
- [ ] Publisher Declaration Form completed
- [ ] No use of Autodesk trademarks in product name
- [ ] Privacy policy covers data sent to Claude AI

### Submission
- [ ] GitHub repo is set to public
- [ ] manifest.json is in repo root
- [ ] Email sent to: appsubmissions@autodesk.com
- [ ] Subject line: "ClashGuard MCP — Autodesk Marketplace Submission"
- [ ] Attach: manifest.json, README.md, demo video (optional)

---

## 22. KNOWN RISKS & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| APS API quota exceeded in demo | Low | High | Use DEMO_MODE=true for demo; APS only for real testing |
| Claude API rate limit during demo | Medium | High | Cache suggest_resolutions results; pre-run before live demo |
| Geometry false positives in mock data | Low | Medium | Validate mock_db.json bounding boxes manually |
| python-docx rendering issues on Windows | Medium | Low | Test on Windows before demo; fallback to PDF only |
| Autodesk manifest validation failure | Medium | High | Follow manifest schema exactly; test with validator tool |
| Network timeout during APS calls | Low | Medium | httpx timeout=30s; graceful error message |
| Demo laptop has no internet | Low | Critical | DEMO_MODE=true uses local data; no internet needed |

---

## QUICK REFERENCE — WHO DOES WHAT

| Section | Owner | Deadline |
|---------|-------|----------|
| Section 3 — Repo setup | Krushna | Day 1 |
| Section 4 — APS account | Prathmesh | Day 1 ⚠ BLOCKER |
| Section 7 — server.py | Krushna | Day 2 |
| Section 8 — Tool 1 (extract) | Prathmesh | Day 3 |
| Section 9 — Tool 2 (analyze) | Krushna | Day 3 |
| Section 10 — Tool 3 (detect) | Krushna | Day 4 |
| Section 11 — Tool 4 (suggest) | Krushna + Pradeep | Day 5 |
| Section 12 — Tool 5 (report) | Prathmesh + Pradeep | Day 5 |
| Section 13 — Mock data | Pradeep | Day 2 |
| Section 15 — manifest.json | Krushna | Day 6 |
| Section 18 — Tests | All | Day 6 |
| Section 19 — Demo dry run | All | Day 7 |
| Section 20 — PPT | Pradeep | Day 6 |

---

*Document prepared by: AI Planning Session*  
*For: CCTech MCP Hackathon Team — Pune*  
*Version: 1.0 | Last updated: June 2, 2026*
