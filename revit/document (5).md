bashcat &gt; /mnt/user-data/outputs/PRD.md &lt;&lt; 'ENDOFFILE'
# ClashGuard MCP — Complete Product Requirements &amp; Execution Plan
**Version:** 1.0   
**Deadline:** June 5, 2026 (Demo + Codebase + PPT)  
**Final Goal:** Production-grade MCP submitted to Autodesk Design &amp; Make Marketplace

---

&gt; **HOW TO USE THIS DOCUMENT**  
&gt; This is a complete, self-contained execution plan. Every step is numbered and actionable.  
&gt; - If you are an **AI agent**: execute every step in order. Steps marked `[MANUAL]` require human action.  
&gt; - If you are a **developer**: read Section 0 first, then follow your assigned sections.  
&gt; - Steps marked `⚠` are blockers — nothing after them works until they are done.  
&gt; - Steps marked `[AUTODESK REQUIREMENT]` are mandatory for marketplace submission.

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
18. [Testing &amp; Validation](#18-testing--validation)
19. [Demo Scenarios](#19-demo-scenarios)
20. [PowerPoint Presentation](#20-powerpoint-presentation)
21. [Autodesk Submission Checklist](#21-autodesk-submission-checklist)
22. [Known Risks &amp; Mitigations](#22-known-risks--mitigations)

---

## 1. PROJECT OVERVIEW

### What We Are Building
**ClashGuard MCP** is a Model Context Protocol server that connects Claude AI to Autodesk Revit via APS APIs to detect, prioritize, and suggest resolutions for MEP (Mechanical, Electrical, Plumbing) clashes using natural language.

### The One-Sentence Pitch
&gt; An architect types "Will my new windows clash with HVAC ducts?" in Claude Desktop and gets a prioritized, actionable answer — without opening Navisworks — in under 5 minutes.

### Why It Matters
- MEP clashes cost the global AEC industry $625 billion/year in rework
- Current tools (Navisworks) detect clashes but don't prioritize or suggest fixes
- ClashGuard is the first MCP to bring natural language + AI reasoning into this workflow
- Targets: Autodesk Design &amp; Make Marketplace (live since DevCon 2026)

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
Autodesk's Trust &amp; Safety requirements for marketplace MCPs require that engineering calculations be reliable and not subject to AI hallucination. Our architecture satisfies this by design.

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
pip freeze &gt; requirements.txt
```

---

## 4. APS DEVELOPER ACCOUNT SETUP

&gt; ⚠ **BLOCKER** — Without this, Tools 1 and 2 cannot be built or tested against real Revit data. Do this on Day 1.

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
&gt; If CCTech has a Revit model available — even a simple one with ducts, pipes, and walls — upload it to BIM 360 to get a real URN for testing. If not, skip this and use mock data (Section 13).

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
```bash
cat &gt; .env.example &lt;&lt; 'EOF'
# Autodesk Platform Services (APS)
APS_CLIENT_ID=your_aps_client_id_here
APS_CLIENT_SECRET=your_aps_client_secret_here
APS_CALLBACK_URL=http://localhost:8080/callback

# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-6

# Optional: Revit project URN for real testing
APS_TEST_URN=your_model_urn_here

# Demo mode (use mock data instead of real APS)
DEMO_MODE=true
EOF
```

### Step 6.2 — Create .env (DO NOT commit — contains real secrets)
```bash
cat &gt; .env &lt;&lt; 'EOF'
APS_CLIENT_ID=PASTE_YOUR_REAL_CLIENT_ID
APS_CLIENT_SECRET=PASTE_YOUR_REAL_CLIENT_SECRET
APS_CALLBACK_URL=http://localhost:8080/callback
ANTHROPIC_API_KEY=PASTE_YOUR_REAL_ANTHROPIC_KEY
ANTHROPIC_MODEL=claude-sonnet-4-6
DEMO_MODE=true
EOF
```

### Step 6.3 — Update .gitignore
```bash
cat &gt;&gt; .gitignore &lt;&lt; 'EOF'
.env
outputs/
venv/
__pycache__/
*.pyc
*.pyo
.DS_Store
EOF
```

### Step 6.4 — Create config loader (config.py)
```python
# config.py — create this file in project root
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

# Tool imports
from tools.extract_revit_data import run as extract_revit_data
from tools.analyze_model       import run as analyze_model
from tools.detect_clashes      import run as detect_clashes
from tools.suggest_resolutions import run as suggest_resolutions
from tools.generate_report     import run as generate_report

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("clashguard")

# ── MCP Tool Definitions ──────────────────────────────────────────────────
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
                    "description": "Optional floor number or zone to filter elements (e.g. '3', 'Level 3')."
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

# ── MCP Protocol Loop ─────────────────────────────────────────────────────
def send(obj: dict):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()

def tool_result(call_id, text: str):
    send({"jsonrpc": "2.0", "id": call_id, "result": {"content": [{"type": "text", "text": text}]}})

def error_result(call_id, code: int, message: str):
    send({"jsonrpc": "2.0", "id": call_id, "error": {"code": code, "message": message}})

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
            send({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})

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

### Step 8.1 — Create APS Auth client (aps/auth.py) [Prathmesh]
```python
# aps/auth.py
import httpx
import time
from config import APS_CLIENT_ID, APS_CLIENT_SECRET

_token_cache = {"token": None, "expires_at": 0}

def get_token() -&gt; str:
    """Get a valid 2-legged APS access token. Caches until expiry."""
    now = time.time()
    if _token_cache["token"] and now &lt; _token_cache["expires_at"] - 60:
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

### Step 8.2 — Create extract_revit_data tool [Prathmesh]
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

def run(args: dict) -&gt; str:
    floor_filter   = args.get("floor_filter", "")
    element_types  = args.get("element_types", list(MEP_TYPES))
    model_urn      = args.get("model_urn", "")

    if DEMO_MODE or not model_urn:
        return _extract_from_mock(floor_filter, element_types)
    else:
        return _extract_from_aps(model_urn, floor_filter, element_types)

def _extract_from_mock(floor_filter: str, element_types: list) -&gt; str:
    with open(MOCK_DB_PATH, "r") as f:
        db = json.load(f)

    elements = db.get("elements", [])

    # Apply filters
    if floor_filter:
        elements = [e for e in elements if floor_filter.lower() in e.get("location", "").lower()]
    if element_types:
        elements = [e for e in elements if e.get("type") in element_types]

    return json.dumps({
        "source":    "mock_data",
        "count":     len(elements),
        "elements":  elements,
        "message":   f"Extracted {len(elements)} elements from mock data. Ready for analysis."
    }, indent=2)

def _extract_from_aps(model_urn: str, floor_filter: str, element_types: list) -&gt; str:
    """Real APS extraction — requires valid token and model URN."""
    from aps.auth import get_token
    import httpx

    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get model metadata
    meta_url = f"https://developer.api.autodesk.com/modelderivative/v2/designdata/{model_urn}/metadata"
    resp = httpx.get(meta_url, headers=headers, verify=True)
    resp.raise_for_status()
    metadata = resp.json()

    guid = metadata["data"]["metadata"][0]["guid"]

    # Get properties for MEP elements
    props_url = f"https://developer.api.autodesk.com/modelderivative/v2/designdata/{model_urn}/metadata/{guid}/properties"
    resp = httpx.get(props_url, headers=headers, verify=True)
    resp.raise_for_status()
    data = resp.json()

    # Parse into standardized element format
    elements = []
    for obj in data.get("data", {}).get("collection", []):
        props = obj.get("properties", {})
        el_type = props.get("Category", {}).get("Category", "Unknown")
        if el_type not in element_types:
            continue

        # Extract bounding box from geometry (simplified)
        element = {
            "id":       str(obj.get("objectid")),
            "type":     el_type,
            "name":     obj.get("name", ""),
            "location": props.get("Constraints", {}).get("Level", ""),
            "bbox": {
                "min": {"x": 0, "y": 0, "z": 0},  # Real values from APS geometry
                "max": {"x": 0, "y": 0, "z": 0},
            },
            "properties": {
                "size":      props.get("Dimensions", {}),
                "material":  props.get("Materials and Finishes", {}),
                "system":    props.get("Mechanical", {}),
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

### Step 9.1 — Create analyze_model tool [Krushna]
```python
# tools/analyze_model.py
"""
Tool 2: analyze_model
Processes element relationships, clearance zones, and spatial context.
Prepares data for clash detection.
"""

import json
from engine.geometry_utils import compute_centers, compute_proximity_groups

def run(args: dict) -&gt; str:
    raw_elements           = args.get("elements", [])
    tolerance_mm           = args.get("clearance_tolerance_mm", 50)

    if isinstance(raw_elements, str):
        raw_elements = json.loads(raw_elements)

    if not raw_elements:
        # Try to parse elements from nested JSON (if Tool 1 output passed directly)
        return json.dumps({"error": "No elements provided. Run extract_revit_data first."})

    # Compute element centers
    elements_with_centers = compute_centers(raw_elements)

    # Group elements by proximity (for efficient clash checking)
    proximity_groups = compute_proximity_groups(elements_with_centers, threshold_m=2.0)

    # Build spatial context summary
    by_type = {}
    by_floor = {}
    for el in elements_with_centers:
        by_type[el["type"]]     = by_type.get(el["type"], 0) + 1
        by_floor[el["location"]] = by_floor.get(el["location"], 0) + 1

    return json.dumps({
        "status":             "analyzed",
        "total_elements":     len(elements_with_centers),
        "clearance_tolerance_mm": tolerance_mm,
        "elements":           elements_with_centers,
        "proximity_groups":   proximity_groups,
        "summary": {
            "by_type":        by_type,
            "by_floor":       by_floor,
            "total_groups":   len(proximity_groups),
        },
        "message": (
            f"Analyzed {len(elements_with_centers)} elements across "
            f"{len(by_floor)} floors. Found {len(proximity_groups)} proximity groups "
            f"for efficient clash checking. Ready for detect_clashes."
        )
    }, indent=2)
```

### Step 9.2 — Create geometry utilities [Krushna]
```python
# engine/geometry_utils.py
"""
Utility functions for spatial geometry operations.
All deterministic — no AI involved.
"""

def compute_centers(elements: list) -&gt; list:
    """Add center coordinates to each element's bounding box."""
    result = []
    for el in elements:
        bbox = el.get("bbox", {})
        mn = bbox.get("min", {"x": 0, "y": 0, "z": 0})
        mx = bbox.get("max", {"x": 0, "y": 0, "z": 0})
        el["center"] = {
            "x": (mn["x"] + mx["x"]) / 2,
            "y": (mn["y"] + mx["y"]) / 2,
            "z": (mn["z"] + mx["z"]) / 2,
        }
        result.append(el)
    return result

def compute_proximity_groups(elements: list, threshold_m: float = 2.0) -&gt; list:
    """
    Group elements that are within threshold_m meters of each other.
    Reduces O(n^2) clash detection to only nearby element pairs.
    """
    import math
    groups = []
    used = set()

    for i, el_a in enumerate(elements):
        if i in used:
            continue
        group = [el_a]
        ca = el_a.get("center", {"x": 0, "y": 0, "z": 0})
        for j, el_b in enumerate(elements):
            if j &lt;= i or j in used:
                continue
            cb = el_b.get("center", {"x": 0, "y": 0, "z": 0})
            dist = math.sqrt(
                (ca["x"] - cb["x"]) ** 2 +
                (ca["y"] - cb["y"]) ** 2 +
                (ca["z"] - cb["z"]) ** 2
            )
            if dist &lt;= threshold_m:
                group.append(el_b)
                used.add(j)
        if len(group) &gt; 1:
            groups.append(group)
        used.add(i)
    return groups

def bbox_volume(bbox: dict) -&gt; float:
    """Compute the volume of a bounding box in cubic meters."""
    mn = bbox.get("min", {"x": 0, "y": 0, "z": 0})
    mx = bbox.get("max", {"x": 0, "y": 0, "z": 0})
    dx = abs(mx["x"] - mn["x"])
    dy = abs(mx["y"] - mn["y"])
    dz = abs(mx["z"] - mn["z"])
    return dx * dy * dz
```

---

## 10. TOOL 3 — detect_clashes

**Owner:** Krushna  
**Dependencies:** AABB engine, analyzed elements from Tool 2

### Step 10.1 — Create AABB collision engine [Krushna]
```python
# engine/aabb.py
"""
Axis-Aligned Bounding Box (AABB) Collision Detection Engine.
100% deterministic — no AI involved.
Finds intersections between pairs of 3D bounding boxes.
"""

from engine.severity import score_clash, SEVERITY_LABELS

def aabb_intersects(a_min, a_max, b_min, b_max) -&gt; bool:
    """
    Returns True if two AABBs intersect.
    Checks all 3 axes — if any axis has no overlap, no collision.
    """
    return (
        a_min["x"] &lt;= b_max["x"] and a_max["x"] &gt;= b_min["x"] and
        a_min["y"] &lt;= b_max["y"] and a_max["y"] &gt;= b_min["y"] and
        a_min["z"] &lt;= b_max["z"] and a_max["z"] &gt;= b_min["z"]
    )

def intersection_volume(a_min, a_max, b_min, b_max) -&gt; float:
    """Calculate the volume of the intersection of two AABBs."""
    ox = max(0, min(a_max["x"], b_max["x"]) - max(a_min["x"], b_min["x"]))
    oy = max(0, min(a_max["y"], b_max["y"]) - max(a_min["y"], b_min["y"]))
    oz = max(0, min(a_max["z"], b_max["z"]) - max(a_min["z"], b_min["z"]))
    return ox * oy * oz

def run_clash_detection(elements: list, systems_to_check: list, tolerance_mm: float = 50) -&gt; list:
    """
    Main clash detection function.
    Compares all element pairs and returns list of detected clashes.
    """
    tolerance_m = tolerance_mm / 1000.0
    clashes = []
    clash_id = 1
    seen_pairs = set()

    mep_types      = {"Duct", "Pipe", "CableTray", "Conduit", "MechanicalEquipment", "PlumbingFixture"}
    struct_types   = {"Beam", "Column", "StructuralFraming"}
    arch_types     = {"Wall", "Window", "Floor", "Ceiling", "Roof"}

    for i, el_a in enumerate(elements):
        for j, el_b in enumerate(elements):
            if j &lt;= i:
                continue
            pair_key = tuple(sorted([el_a["id"], el_b["id"]]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            # Only check MEP vs structural/architectural crosses
            a_is_mep   = el_a["type"] in mep_types
            b_is_mep   = el_b["type"] in mep_types
            a_is_other = el_a["type"] in struct_types | arch_types
            b_is_other = el_b["type"] in struct_types | arch_types

            if not ((a_is_mep and b_is_other) or (b_is_mep and a_is_other)):
                continue

            bbox_a = el_a.get("bbox", {})
            bbox_b = el_b.get("bbox", {})
            a_min, a_max = bbox_a.get("min", {}), bbox_a.get("max", {})
            b_min, b_max = bbox_b.get("min", {}), bbox_b.get("max", {})

            if not (a_min and a_max and b_min and b_max):
                continue

            # Expand bbox by tolerance for soft clash detection
            a_min_soft = {k: a_min[k] - tolerance_m for k in a_min}
            a_max_soft = {k: a_max[k] + tolerance_m for k in a_max}

            # Hard clash
            if aabb_intersects(a_min, a_max, b_min, b_max):
                vol = intersection_volume(a_min, a_max, b_min, b_max)
                severity_score = score_clash(el_a, el_b, vol, "hard")
                clashes.append({
                    "clash_id":        f"CG-{clash_id:03d}",
                    "type":            "hard",
                    "element_a":       {"id": el_a["id"], "type": el_a["type"], "name": el_a.get("name", "")},
                    "element_b":       {"id": el_b["id"], "type": el_b["type"], "name": el_b.get("name", "")},
                    "location":        el_a.get("location", "Unknown"),
                    "intersection_volume_m3": round(vol, 6),
                    "severity_score":  severity_score,
                    "severity_label":  SEVERITY_LABELS[severity_score],
                    "center": el_a.get("center", {}),
                })
                clash_id += 1

            # Soft clash (within tolerance but not hard)
            elif aabb_intersects(a_min_soft, a_max_soft, b_min, b_max):
                severity_score = score_clash(el_a, el_b, 0, "soft")
                clashes.append({
                    "clash_id":        f"CG-{clash_id:03d}",
                    "type":            "soft",
                    "element_a":       {"id": el_a["id"], "type": el_a["type"], "name": el_a.get("name", "")},
                    "element_b":       {"id": el_b["id"], "type": el_b["type"], "name": el_b.get("name", "")},
                    "location":        el_a.get("location", "Unknown"),
                    "intersection_volume_m3": 0,
                    "clearance_violation_mm": tolerance_mm,
                    "severity_score":  severity_score,
                    "severity_label":  SEVERITY_LABELS[severity_score],
                    "center": el_a.get("center", {}),
                })
                clash_id += 1

    return sorted(clashes, key=lambda c: c["severity_score"], reverse=True)
```

### Step 10.2 — Create severity rules engine [Krushna]
```python
# engine/severity.py
"""
Rule-based severity scoring for detected clashes.
100% deterministic — IF/ELSE logic based on engineering rules.
No AI involved in scoring.
"""

SEVERITY_LABELS = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW"}

# Rules: element type combinations and their base severity
SEVERITY_RULES = {
    # (type_a, type_b): score
    ("Duct",   "Beam"):   4,   # CRITICAL — structural interference
    ("Pipe",   "Beam"):   4,   # CRITICAL — structural interference
    ("Duct",   "Column"): 4,   # CRITICAL — structural interference
    ("Pipe",   "Column"): 4,   # CRITICAL — structural interference
    ("Duct",   "Window"): 3,   # HIGH — facade interference
    ("Pipe",   "Window"): 3,   # HIGH — facade interference
    ("Duct",   "Wall"):   2,   # MEDIUM — can penetrate with sleeve
    ("Pipe",   "Wall"):   2,   # MEDIUM — can penetrate with sleeve
    ("Duct",   "Pipe"):   2,   # MEDIUM — MEP coordination
    ("CableTray", "Duct"):2,   # MEDIUM — MEP coordination
}

def score_clash(el_a: dict, el_b: dict, volume_m3: float, clash_type: str) -&gt; int:
    """
    Score a clash from 1 (low) to 4 (critical) using rule-based logic.
    Returns integer severity score.
    """
    type_a = el_a.get("type", "")
    type_b = el_b.get("type", "")

    # Look up rule (try both orderings)
    base = SEVERITY_RULES.get((type_a, type_b)) or \
           SEVERITY_RULES.get((type_b, type_a)) or 2

    # Adjust for volume (larger intersection = more severe)
    if clash_type == "hard" and volume_m3 &gt; 0.1:
        base = min(4, base + 1)
    elif clash_type == "soft":
        base = max(1, base - 1)

    return base
```

### Step 10.3 — Create detect_clashes tool [Krushna]
```python
# tools/detect_clashes.py
"""
Tool 3: detect_clashes
Runs AABB collision detection on the analyzed model elements.
All calculations are deterministic — no AI.
"""

import json
from engine.aabb import run_clash_detection

def run(args: dict) -&gt; str:
    elements         = args.get("elements", [])
    systems_to_check = args.get("systems_to_check", ["HVAC", "Plumbing", "Electrical", "Structural"])
    zones            = args.get("zones", [])

    if isinstance(elements, str):
        try:
            elements = json.loads(elements)
        except:
            return json.dumps({"error": "Invalid elements data. Pass output from analyze_model."})

    # Filter by zone if specified
    if zones:
        elements = [e for e in elements if any(z.lower() in e.get("location", "").lower() for z in zones)]

    clashes = run_clash_detection(elements, systems_to_check)

    # Count by severity
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for c in clashes:
        severity_counts[c["severity_label"]] += 1

    result = {
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
    }
    return json.dumps(result, indent=2)
```

---

## 11. TOOL 4 — suggest_resolutions

**Owner:** Krushna + Pradeep (prompt engineering)  
**Dependencies:** Anthropic Claude API, clash list from Tool 3

&gt; ⚠ **[AUTODESK REQUIREMENT]** This tool must check `user_consent_given=true` before sending any data to Claude. This is a mandatory Autodesk marketplace requirement.

```python
# tools/suggest_resolutions.py
"""
Tool 4: suggest_resolutions
Uses Claude AI to prioritize clashes and suggest engineering resolutions.
IMPORTANT: AI is used ONLY for reasoning — never for geometry calculations.
IMPORTANT: User consent is required before sending data to Claude.
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

def run(args: dict) -&gt; str:
    clashes             = args.get("clashes", [])
    project_context     = args.get("project_context", "")
    user_consent_given  = args.get("user_consent_given", False)

    # [AUTODESK REQUIREMENT] — Enforce user consent before sending to AI
    if not user_consent_given:
        return json.dumps({
            "error": "User consent required",
            "message": (
                "This tool sends anonymized clash data to Anthropic's Claude AI for analysis. "
                "To proceed, call this tool again with user_consent_given=true. "
                "Data sent: element types, locations, severity scores. "
                "No personal data, user data, or project credentials are sent."
            )
        })

    if isinstance(clashes, str):
        try:
            clashes = json.loads(clashes)
        except:
            return json.dumps({"error": "Invalid clash data format."})

    if not clashes:
        return json.dumps({"message": "No clashes provided. Run detect_clashes first."})

    # Build user message — only send minimum required data to Claude
    clash_summary = []
    for c in clashes:
        clash_summary.append({
            "clash_id":       c["clash_id"],
            "type":           c["type"],
            "element_a_type": c["element_a"]["type"],
            "element_b_type": c["element_b"]["type"],
            "location":       c["location"],
            "severity":       c["severity_label"],
            "volume_m3":      c.get("intersection_volume_m3", 0),
        })

    user_message = f"""Please analyze these {len(clashes)} MEP clashes detected in the building model and provide resolution recommendations.

Project context: {project_context or 'Commercial office building, active design phase'}

Detected clashes:
{json.dumps(clash_summary, indent=2)}

Please provide:
1. Resolution recommendations for each clash
2. Overall priority order
3. Which clashes can be addressed together (grouped fixes)
"""

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
        ai_recommendations = f"AI analysis unavailable: {str(e)}. Clashes are listed by deterministic severity score."

    return json.dumps({
        "total_clashes":        len(clashes),
        "clashes":              clashes,
        "ai_recommendations":   ai_recommendations,
        "consent_recorded":     True,
        "data_sent_to_ai":      "element types, locations, severity scores only — no personal or credential data",
        "message": f"AI analysis complete for {len(clashes)} clashes. See ai_recommendations for prioritized resolution plan."
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

def run(args: dict) -&gt; str:
    clashes      = args.get("clashes", [])
    project_name = args.get("project_name", "Unnamed Project")
    fmt          = args.get("format", "both")

    if isinstance(clashes, str):
        try:
            clashes = json.loads(clashes)
        except:
            return json.dumps({"error": "Invalid clash data."})

    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name    = f"ClashGuard_Report_{project_name.replace(' ', '_')}_{timestamp}"
    generated    = []

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
        "message": f"Report generated: {len(generated)} file(s). Path: {', '.join(generated)}"
    }, indent=2)

def _generate_docx(clashes: list, project_name: str, path: Path):
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    doc.add_heading(f"ClashGuard Coordination Report", 0)
    doc.add_heading(f"Project: {project_name}", 1)

    info = doc.add_paragraph()
    info.add_run(f"Date: {datetime.now().strftime('%B %d, %Y')}  |  "
                 f"Total Clashes: {len(clashes)}  |  "
                 f"Generated by: ClashGuard MCP v1.0")

    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for c in clashes:
        severity_counts[c.get("severity_label", "MEDIUM")] += 1

    doc.add_heading("Executive Summary", 2)
    doc.add_paragraph(
        f"ClashGuard detected {len(clashes)} MEP clashes in the {project_name} model. "
        f"Immediate attention required for {severity_counts['CRITICAL']} CRITICAL "
        f"and {severity_counts['HIGH']} HIGH severity clashes. "
        f"All geometry calculations were performed deterministically."
    )

    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, h in enumerate(["Severity", "Count", "Action", "Timeline"]):
        hdr[i].text = h

    rows_data = [
        ("CRITICAL", str(severity_counts["CRITICAL"]), "Immediate action required", "Before next design iteration"),
        ("HIGH",     str(severity_counts["HIGH"]),     "Address this sprint",        "Within 3 days"),
        ("MEDIUM",   str(severity_counts["MEDIUM"]),   "Resolve before construction doc", "Within 2 weeks"),
        ("LOW",      str(severity_counts["LOW"]),      "Monitor and note",            "Before issue"),
    ]
    for r in rows_data:
        row_cells = table.add_row().cells
        for i, val in enumerate(r):
            row_cells[i].text = val

    doc.add_heading("Clash Details", 2)
    for c in clashes:
        doc.add_heading(f"{c['clash_id']} — {c['severity_label']}: {c['element_a']['type']} vs {c['element_b']['type']}", 3)
        doc.add_paragraph(
            f"Location: {c.get('location', 'Unknown')}  |  "
            f"Type: {c['type'].upper()} clash  |  "
            f"Volume: {c.get('intersection_volume_m3', 0):.4f} m³"
        )
        if c.get("ai_recommendation"):
            doc.add_paragraph(f"Recommendation: {c['ai_recommendation']}")

    doc.save(str(path))

def _generate_pdf(clashes: list, project_name: str, path: Path):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm

    doc    = SimpleDocTemplate(str(path), pagesize=A4,
                               rightMargin=20*mm, leftMargin=20*mm,
                               topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story  = []

    story.append(Paragraph("ClashGuard Coordination Report", styles["Title"]))
    story.append(Paragraph(f"Project: {project_name}", styles["Heading1"]))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')} | Total Clashes: {len(clashes)}", styles["Normal"]))
    story.append(Spacer(1, 10*mm))

    sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for c in clashes:
        sev_counts[c.get("severity_label", "MEDIUM")] += 1

    story.append(Paragraph("Summary", styles["Heading2"]))
    data = [["Severity", "Count"]] + [[k, str(v)] for k, v in sev_counts.items()]
    t = Table(data, colWidths=[80*mm, 40*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0052CC")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6FB")]),
    ]))
    story.append(t)
    story.append(Spacer(1, 10*mm))

    story.append(Paragraph("Clash Details", styles["Heading2"]))
    for c in clashes:
        story.append(Paragraph(
            f"&lt;b&gt;{c['clash_id']}&lt;/b&gt; — {c['severity_label']}: "
            f"{c['element_a']['type']} vs {c['element_b']['type']} @ {c.get('location', 'Unknown')}",
            styles["Heading3"]
        ))
        story.append(Spacer(1, 3*mm))

    doc.build(story)
```

---

## 13. MOCK DATA FOR DEMO

**Owner:** Pradeep (data design)  
This file makes the entire demo work without any live APS or Revit connection. It simulates a real 3rd-floor south facade scenario.

### Step 13.1 — Create mock_db.json [Pradeep]
```json
{
  "project": "CCTech Demo Building — 3rd Floor South Facade",
  "description": "Office building in Pune. Architect adding 5 new windows on south facade, Level 3.",
  "elements": [
    {
      "id": "duct-001",
      "type": "Duct",
      "name": "HVAC Main Supply Duct SD-301",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": {
        "min": {"x": 10.0, "y": 8.8, "z": 9.0},
        "max": {"x": 20.0, "y": 9.2, "z": 9.3}
      },
      "properties": {
        "size": "450x300mm",
        "system": "HVAC Supply",
        "material": "GI Sheet"
      }
    },
    {
      "id": "duct-002",
      "type": "Duct",
      "name": "HVAC Return Duct RD-302",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": {
        "min": {"x": 10.0, "y": 8.5, "z": 8.6},
        "max": {"x": 20.0, "y": 8.8, "z": 8.9}
      },
      "properties": {
        "size": "300x200mm",
        "system": "HVAC Return",
        "material": "GI Sheet"
      }
    },
    {
      "id": "pipe-001",
      "type": "Pipe",
      "name": "Sprinkler Main Pipe SP-301",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": {
        "min": {"x": 8.0,  "y": 8.95, "z": 9.3},
        "max": {"x": 22.0, "y": 9.05, "z": 9.4}
      },
      "properties": {
        "diameter": "DN100",
        "system": "Fire Suppression",
        "material": "Steel"
      }
    },
    {
      "id": "conduit-001",
      "type": "CableTray",
      "name": "Electrical Cable Tray CT-301",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": {
        "min": {"x": 9.0,  "y": 8.7, "z": 8.5},
        "max": {"x": 21.0, "y": 8.9, "z": 8.7}
      },
      "properties": {
        "size": "300x100mm",
        "system": "Electrical Distribution",
        "material": "Perforated Steel"
      }
    },
    {
      "id": "win-new-01",
      "type": "Window",
      "name": "New Window W3-01 (Proposed)",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": {
        "min": {"x": 11.0, "y": 8.6, "z": 8.8},
        "max": {"x": 12.5, "y": 9.4, "z": 9.5}
      },
      "properties": {"type": "Fixed Glazing", "size": "1500x700mm", "status": "Proposed"}
    },
    {
      "id": "win-new-02",
      "type": "Window",
      "name": "New Window W3-02 (Proposed)",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": {
        "min": {"x": 13.5, "y": 8.6, "z": 8.8},
        "max": {"x": 15.0, "y": 9.4, "z": 9.5}
      },
      "properties": {"type": "Fixed Glazing", "size": "1500x700mm", "status": "Proposed"}
    },
    {
      "id": "win-new-03",
      "type": "Window",
      "name": "New Window W3-03 (Proposed) — CLASH",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": {
        "min": {"x": 16.0, "y": 8.7, "z": 9.0},
        "max": {"x": 17.5, "y": 9.3, "z": 9.4}
      },
      "properties": {"type": "Fixed Glazing", "size": "1500x700mm", "status": "Proposed"}
    },
    {
      "id": "win-new-04",
      "type": "Window",
      "name": "New Window W3-04 (Proposed)",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": {
        "min": {"x": 18.5, "y": 8.6, "z": 8.8},
        "max": {"x": 20.0, "y": 9.4, "z": 9.5}
      },
      "properties": {"type": "Fixed Glazing", "size": "1500x700mm", "status": "Proposed"}
    },
    {
      "id": "win-new-05",
      "type": "Window",
      "name": "New Window W3-05 (Proposed) — SOFT CLASH",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": {
        "min": {"x": 10.2, "y": 8.6, "z": 8.7},
        "max": {"x": 11.7, "y": 9.4, "z": 9.1}
      },
      "properties": {"type": "Fixed Glazing", "size": "1500x700mm", "status": "Proposed"}
    },
    {
      "id": "beam-001",
      "type": "Beam",
      "name": "Structural Beam SB-301",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": {
        "min": {"x": 0.0,  "y": 8.85, "z": 9.1},
        "max": {"x": 25.0, "y": 9.15, "z": 9.5}
      },
      "properties": {"size": "UC305x305", "material": "Steel", "load_bearing": true}
    },
    {
      "id": "wall-001",
      "type": "Wall",
      "name": "South Facade Wall W-301",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": {
        "min": {"x": 8.0,  "y": 9.0,  "z": 8.0},
        "max": {"x": 22.0, "y": 9.25, "z": 11.0}
      },
      "properties": {"thickness": "250mm", "type": "External Facade", "material": "Brick + Insulation"}
    }
  ]
}
```

---

## 14. CLAUDE DESKTOP CONFIGURATION

### Step 14.1 — Find Claude Desktop config location [MANUAL]
```
Windows: %APPDATA%\Claude\claude_desktop_config.json
Mac:     ~/Library/Application Support/Claude/claude_desktop_config.json
Linux:   ~/.config/Claude/claude_desktop_config.json
```

### Step 14.2 — Paste this config (update the path) [MANUAL: Krushna or Prathmesh]
```json
{
  "mcpServers": {
    "clashguard": {
      "command": "python",
      "args": ["C:\\Users\\YOURNAME\\Desktop\\clashguard-mcp\\server.py"]
    }
  }
}
```

&gt; On Windows use double backslashes: `C:\\Users\\...`  
&gt; On Mac/Linux use forward slashes: `/Users/yourname/Desktop/clashguard-mcp/server.py`

### Step 14.3 — Restart Claude Desktop
1. Right-click Claude icon in system tray
2. Click "Quit"
3. Reopen Claude Desktop
4. Look for 🔨 hammer icon in chat input bar
5. Click it — you should see all 5 ClashGuard tools listed

---

## 15. AUTODESK MANIFEST JSON

&gt; **[AUTODESK REQUIREMENT]** This file must be submitted with the Publisher Declaration Form.

### Step 15.1 — Create manifest.json in project root [Pradeep]
```json
{
  "mcp_manifest_version": "1.0",
  "app_model": "A",
  "mcp_spec_version": "2025-11-25",
  "server": {
    "name": "clashguard-mcp",
    "version": "1.0.0",
    "description": "AI-powered MEP clash detection for Revit using Autodesk APS and Claude AI",
    "transport": "stdio"
  },
  "tools": [
    {
      "name": "extract_revit_data",
      "description": "Extracts MEP element geometry and spatial data from a Revit model using the APS Model Derivatives API. Returns element bounding boxes, types, and floor locations. Does not access personal data or project credentials."
    },
    {
      "name": "analyze_model",
      "description": "Processes spatial relationships between building elements and computes clearance zones. All calculations are deterministic. No data leaves the local environment."
    },
    {
      "name": "detect_clashes",
      "description": "Runs deterministic AABB collision detection on building elements. Identifies hard clashes (physical overlap) and soft clashes (clearance violations). No AI involved — rule-based only."
    },
    {
      "name": "suggest_resolutions",
      "description": "Sends anonymized clash data (element types, locations, severity scores — no personal or credential data) to Anthropic Claude AI for prioritization and engineering resolution suggestions. Requires explicit user consent before each use."
    },
    {
      "name": "generate_report",
      "description": "Generates a professional PDF and Word clash coordination report from the clash detection results. Report is saved locally. No external data transmission."
    }
  ],
  "resources": [],
  "prompts": [],
  "external_endpoints": [
    "https://developer.api.autodesk.com",
    "https://api.anthropic.com"
  ],
  "autodesk_apis_used": [
    "APS Model Derivatives API",
    "Autodesk Authentication API (OAuth 2.0)"
  ],
  "ai_llm_providers": [
    "anthropic-claude (claude-sonnet-4-6)"
  ],
  "data_handling": {
    "personal_data_collected": false,
    "data_sent_to_ai": "Anonymized clash data only: element types, location identifiers, severity scores, intersection volumes. No personal data, user credentials, or full model data.",
    "user_consent_required_before_ai": true,
    "all_connections_https": true
  }
}
```

---

## 16. USER CONSENT FLOW

&gt; **[AUTODESK REQUIREMENT]** Autodesk requires user consent before sending project data to external AI services.

This is already implemented in `suggest_resolutions.py` via the `user_consent_given` parameter. The flow works as follows:

**Demo conversation flow:**
```
User:   "Analyze these clashes and suggest fixes"
Claude: Calls suggest_resolutions(clashes=[...], user_consent_given=false)
Tool:   Returns consent request message

Claude: "This tool will send anonymized clash data (element types and locations) 
         to Anthropic's Claude AI for analysis. No personal data is shared. 
         Do you consent to proceed?"

User:   "Yes, proceed"
Claude: Calls suggest_resolutions(clashes=[...], user_consent_given=true)
Tool:   Returns full AI analysis
```

No code changes needed — this is already in the Tool 4 implementation above.

---

## 17. SECURITY HARDENING

&gt; **[AUTODESK REQUIREMENT]** All external connections must use HTTPS. All endpoints must be declared.

### Step 17.1 — Verify HTTPS enforcement across codebase [Krushna]
```bash
# Search for any non-HTTPS connections or disabled certificate verification
grep -r "http://"     tools/ aps/ engine/ server.py
grep -r "verify=False" tools/ aps/ engine/ server.py

# Both searches should return ZERO results.
# If any http:// found — change to https://
# If any verify=False found — remove it (default is verify=True)
```

### Step 17.2 — Ensure .env is never committed [All]
```bash
# Check .gitignore includes .env
grep "\.env" .gitignore
# Must show: .env

# Verify .env is not tracked
git status
# .env must NOT appear in "Changes to be committed" or "Untracked files to push"

# If .env was accidentally committed — remove it
git rm --cached .env
git commit -m "Remove .env from tracking"
```

### Step 17.3 — Security checklist before submission [Pradeep]
```
[ ] .env not in Git history
[ ] All httpx/requests calls use verify=True (default — don't override)
[ ] APS_CLIENT_SECRET never appears in code or comments
[ ] ANTHROPIC_API_KEY never appears in code or comments
[ ] manifest.json lists ALL external endpoints used
[ ] No tool description contains instructions or sensitive data refs
[ ] suggest_resolutions always checks user_consent_given before API call
[ ] Report outputs directory is gitignored
```

---

## 18. TESTING &amp; VALIDATION

### Step 18.1 — Run the server locally [Krushna]
```bash
# Activate venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Test server starts without errors
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python server.py

# Expected output:
# {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05", ...}}
```

### Step 18.2 — Test all 5 tools [Krushna]
```bash
# Tool 1: Extract (demo mode)
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"extract_revit_data","arguments":{"floor_filter":"Level 3"}}}' | python server.py | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); r=json.loads(d['result']['content'][0]['text']); print(f'Tool 1: {r[\"count\"]} elements extracted')"

# Tool 3: Detect Clashes (most important test)
python3 -c "
import json, sys
sys.path.insert(0, '.')
from tools.extract_revit_data import run as t1
from tools.analyze_model import run as t2
from tools.detect_clashes import run as t3

r1 = json.loads(t1({'floor_filter': 'Level 3'}))
r2 = json.loads(t2({'elements': r1['elements']}))
r3 = json.loads(t3({'elements': r2['elements']}))
print(f'Clashes found: {r3[\"total_clashes\"]}')
print(f'Severity: {r3[\"severity_summary\"]}')
"
# Expected: At least 2 clashes found (win-new-03 vs duct-001/beam-001)
```

### Step 18.3 — Create basic pytest tests [Krushna]
```python
# tests/test_tools.py
import json
import pytest
import sys
sys.path.insert(0, '.')

from tools.extract_revit_data import run as extract
from tools.analyze_model       import run as analyze
from tools.detect_clashes      import run as detect
from tools.suggest_resolutions import run as suggest

def test_extract_returns_elements():
    result = json.loads(extract({}))
    assert "elements" in result
    assert result["count"] &gt; 0

def test_analyze_adds_centers():
    r1 = json.loads(extract({"floor_filter": "Level 3"}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    assert r2["total_elements"] &gt; 0
    for el in r2["elements"]:
        assert "center" in el

def test_detect_finds_clashes():
    r1 = json.loads(extract({}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    r3 = json.loads(detect({"elements": r2["elements"]}))
    assert r3["total_clashes"] &gt;= 1  # Must find at least 1 clash in mock data

def test_detect_clashes_have_severity():
    r1 = json.loads(extract({}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    r3 = json.loads(detect({"elements": r2["elements"]}))
    for clash in r3["clashes"]:
        assert clash["severity_label"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

def test_suggest_requires_consent():
    result = json.loads(suggest({"clashes": [], "user_consent_given": False}))
    assert "error" in result
    assert "consent" in result["message"].lower()

def test_full_pipeline():
    r1 = json.loads(extract({"floor_filter": "Level 3"}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    r3 = json.loads(detect({"elements": r2["elements"]}))
    assert r3["total_clashes"] &gt; 0
    print(f"Full pipeline: {r3['total_clashes']} clashes, severity: {r3['severity_summary']}")
```

```bash
# Run all tests
pytest tests/ -v

# Expected: All 6 tests pass
```

---

## 19. DEMO SCENARIOS

These are the exact prompts to type in Claude Desktop during the demo. Practice these before the presentation.

### Demo Scenario 1: Basic Clash Detection (2 min)
```
Prompt 1:
"I'm an architect working on the CCTech Demo Building. 
I want to add 5 new windows on the south facade of the 3rd floor. 
Before I finalize the design, please extract all the MEP systems on Level 3 
and tell me what's there."

Expected: Claude calls extract_revit_data, returns 10 elements including ducts, pipes, cable trays, windows

Prompt 2 (follow up):
"Great. Now analyze the model and detect any clashes between my proposed 
new windows and the existing MEP systems."

Expected: Claude calls analyze_model then detect_clashes, returns clash list with severity
```

### Demo Scenario 2: AI Recommendations (1.5 min)
```
Prompt:
"I consent to sending the clash data to AI for analysis. 
Please prioritize these clashes and tell me which ones I need to fix today 
before my design review tomorrow morning."

Expected: Claude calls suggest_resolutions with consent=true, returns AI-prioritized list 
with plain-English explanations and specific rerouting suggestions
```

### Demo Scenario 3: Report Generation (1 min)
```
Prompt:
"Perfect. Generate a professional coordination report I can send to the MEP 
consultant today. Include all clash details and the AI recommendations."

Expected: Claude calls generate_report, saves PDF + Word file, returns file paths
WOW moment: "Report saved as PDF and Word file. Ready to send to client."
```

### Timing Guide
```
Total demo time: ~5-6 minutes
- Setup/intro: 30 seconds
- Scenario 1 (extract + detect): 2 minutes
- Scenario 2 (AI suggestions): 1.5 minutes  
- Scenario 3 (report): 1 minute
- Q&amp;A buffer: 1 minute
```

---

## 20. POWERPOINT PRESENTATION

**Owner:** Pradeep  
**Slides:** 10 slides, 5-minute presentation

### Slide Structure
```
Slide 1: Title — ClashGuard MCP | CCTech | Pradeep Misal + Team
Slide 2: The Problem — $625B wasted, 2-4 hrs per Navisworks cycle, no NL interface
Slide 3: What is ClashGuard — one diagram showing the 5-tool pipeline
Slide 4: Architecture — Deterministic Engine + Claude AI reasoning (the key decision)
Slide 5: LIVE DEMO (link to video or run live)
Slide 6: The 5 Tools — table showing tool name, input, output, time saved
Slide 7: Technology Stack — Python, FastAPI, APS APIs, Claude, trimesh
Slide 8: Autodesk Alignment — why this fits the Design &amp; Make Marketplace
Slide 9: Business Impact — 2-4 hours → 5 minutes, $625B industry problem
Slide 10: Team + Next Steps — Pradeep, Krushna, Prathmesh; v2 roadmap

Key messages to emphasize on every slide:
1. "Deterministic geometry — no AI hallucinating coordinates"
2. "Complementary to Revit/Navisworks — not a replacement"
3. "First MCP with natural language clash interface inside Revit"
```

---

## 21. AUTODESK SUBMISSION CHECKLIST

Before submitting to appsubmissions@autodesk.com:

### Code Readiness
```
[ ] server.py runs without errors (python server.py)
[ ] All 5 tools return valid responses
[ ] pytest tests pass (all green)
[ ] Full demo pipeline runs end-to-end
[ ] Report generates PDF and Word file
[ ] Demo prompts tested and rehearsed
```

### Autodesk Requirements
```
[ ] manifest.json created in project root
[ ] manifest.json lists all 5 tools with plain descriptions
[ ] manifest.json declares both external endpoints (Autodesk + Anthropic)
[ ] manifest.json declares anthropic-claude as AI provider
[ ] manifest.json has mcp_spec_version: "2025-11-25"
[ ] User consent flow implemented in suggest_resolutions
[ ] All HTTP calls use HTTPS with verify=True
[ ] .env not in Git history
[ ] Tool descriptions contain no instructions or sensitive data references
[ ] Publisher Declaration Form completed at:
    https://airtable.com/appHPAcNTdVz1ff79/pagR4kGoN4qjIYGGY/form
```

### Submission Package
```
[ ] GitHub repo set to Public (before submission)
[ ] README.md has setup instructions
[ ] .env.example included (not .env)
[ ] manifest.json in root
[ ] requirements.txt up to date
[ ] PPT ready (10 slides)
[ ] Demo video recorded (optional but recommended: 3-5 min screen recording)
```

### Submit to Autodesk
```
Email: appsubmissions@autodesk.com
Subject: MCP Marketplace Submission — ClashGuard MCP (CCTech)
Attach: manifest.json
Attach: completed Publisher Declaration Form (downloaded from Airtable)
Body:   Brief description + GitHub repo link
```

---

## 22. KNOWN RISKS &amp; MITIGATIONS

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| APS account not approved in time | Medium | HIGH — blocks Tools 1+2 | Use DEMO_MODE=true (mock data) for demo. Real APS for production. |
| trimesh installation fails on Windows | Low | Medium | Use `pip install trimesh[easy]` — installs all optional deps |
| Claude API rate limit during demo | Low | Medium | Pre-run demo once before presentation. Cache results. |
| AABB false positives with curved geometry | Medium | Low | Demo uses box-shaped elements only (ducts, windows, beams). Curved pipe clash detection deferred to v2. |
| Manifest rejection by Autodesk | Low | High | Internal review before submission. Address resubmission within 48 hours. |
| bedrock-agentcore conflict with manifest | Medium | Medium | Remove from deployment for v1. Use simple AWS Lambda or local only. |

---

## TEAM ASSIGNMENT SUMMARY

| Task | Owner | Days |
|------|-------|------|
| APS account setup | Prathmesh | Day 1 |
| Repository + folder structure | Krushna | Day 1 |
| Manifest.json + .env setup | Pradeep | Day 1 |
| server.py + MCP protocol | Krushna | Day 1-2 |
| Tool 1: extract_revit_data | Prathmesh | Day 1-2 |
| Tool 2: analyze_model | Krushna | Day 2 |
| engine/aabb.py + severity.py | Krushna | Day 2-3 |
| Tool 3: detect_clashes | Krushna | Day 2-3 |
| Tool 4: suggest_resolutions | Krushna + Pradeep | Day 3 |
| Tool 5: generate_report | Prathmesh | Day 3-4 |
| Mock data (mock_db.json) | Pradeep | Day 1 |
| Claude Desktop config + testing | All | Day 4 |
| pytest + full pipeline test | Krushna | Day 4 |
| Security hardening | Krushna | Day 4 |
| PowerPoint (10 slides) | Pradeep | Day 4-5 |
| Demo rehearsal | All | Day 5 |
| README.md | Pradeep | Day 5 |
| Submission package | Pradeep | Day 5 |

---

*Document Version: 1.0 | Last Updated: June 2, 2026*  
*ClashGuard MCP — CCTech, Computational Cloud Technologies, Pune*  
*For questions: pradeep.misal@o365.cctech.co.in*
ENDOFFILE

echo "PRD.md created successfully"
wc -l /mnt/user-data/outputs/PRD.mdOutputPRD.md created successfully
1969 /mnt/user-data/outputs/PRD.md
Done