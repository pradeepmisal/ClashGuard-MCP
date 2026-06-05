# ClashGuard MCP — Complete Setup & Usage Guide

**Version:** 1.0  
**Date:** June 5, 2026  
**Status:** ✅ Ready for Demo & Autodesk Submission

---

## 📋 Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Full Setup Guide](#full-setup-guide)
3. [Configuration](#configuration)
4. [Running the MCP Server](#running-the-mcp-server)
5. [Claude Desktop Integration](#claude-desktop-integration)
6. [Demo Scenarios](#demo-scenarios)
7. [Testing & Validation](#testing--validation)
8. [Troubleshooting](#troubleshooting)
9. [Architecture Overview](#architecture-overview)

---

## Quick Start

### Prerequisites
- Windows/Mac/Linux
- Python 3.11+ (installed and in PATH)
- Claude Desktop (free tier available)
- 30-50 MB disk space

### Setup (Choose One)

#### Option 1: Using Batch Script (Windows)
```batch
cd clashguard-mcp
setup.bat
```

#### Option 2: Manual Setup
```bash
# 1. Navigate to project
cd clashguard-mcp

# 2. Create & activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify setup
python test_setup.py

# 5. Start server (for testing)
python server.py
```

---

## Full Setup Guide

### Step 1: Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```ini
# For demo (no keys needed):
DEMO_MODE=true

# For real APS/Claude integration (optional):
APS_CLIENT_ID=your_client_id
APS_CLIENT_SECRET=your_client_secret
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_MODEL=claude-sonnet-4-5

# Alternative: Use free Gemini API
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-1.5-flash
```

**In DEMO_MODE=true:**
- ✅ No API keys required
- ✅ Uses realistic mock data (11 sample MEP elements)
- ✅ All 5 tools work locally
- ✅ Perfect for demo & testing

### Step 2: Verify Installation

Run the verification script:
```bash
python test_setup.py
```

Expected output:
```
✓ Python Version: 3.12.3
✓ All 11 dependencies verified
✓ 5 tools defined and registered
✓ Config loaded correctly
✓ Mock data loaded (11 elements)
✓ Basic tool functionality verified
✓ All setup checks passed!
```

### Step 3: Run Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test file
pytest tests/test_engine.py -v

# Expected: 13 tests pass
```

---

## Configuration

### config.py — Main Configuration

All settings are loaded from `.env` and accessed via `config.py`:

```python
from config import (
    APS_CLIENT_ID,        # Autodesk APS credentials
    APS_CLIENT_SECRET,
    ANTHROPIC_API_KEY,    # Claude API key (if not using Gemini)
    GEMINI_API_KEY,       # Free Google AI Studio key (alternative)
    DEMO_MODE,            # Use mock data (True/False)
    MOCK_DB_PATH,         # Path to demo data JSON
    OUTPUT_DIR,           # Reports saved here
    BASE_DIR,             # Project root
)
```

### Choosing Your AI Backend

**Option A: Anthropic Claude (Recommended)**
```ini
# .env
ANTHROPIC_API_KEY=sk-proj-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-5
```

**Option B: Google Gemini (Free)**
```ini
# .env
GEMINI_API_KEY=AIz...
GEMINI_MODEL=gemini-1.5-flash
```

Get free Gemini key: https://aistudio.google.com/apikey

### Using Real Revit Data

**Option 1: From APS (Live Revit Model)**
```python
from tools.extract_revit_data import run
result = run({
    "model_urn": "urn:adsk:objects:os.object:fs...",  # Your model URN
    "floor_filter": "Level 3"
})
```

**Option 2: From C# Revit Plugin Export**
```ini
# .env
CSHARP_EXPORT_PATH=C:\Users\YourName\Desktop\revit_export.json
```

**Option 3: Mock Data (Demo — Default)**
```ini
# .env
DEMO_MODE=true
```

---

## Running the MCP Server

### Local Testing (Development)

```bash
# Terminal 1: Start the MCP server
python server.py

# Expected output:
# [ClashGuard] 2026-06-05 14:23:45 INFO ClashGuard MCP Server starting...
# [ClashGuard] 2026-06-05 14:23:45 INFO Listening on stdio...
# (server waits for Claude Desktop to connect)
```

The server will:
- Load configuration from `.env`
- Verify all dependencies
- Start listening on stdin/stdout
- Wait for Claude Desktop to call tools

### One-Command Full Demo

```bash
python demo.py
```

This runs all 5 tools end-to-end with mock data:
1. Extract elements from mock building
2. Analyze spatial relationships
3. Detect clashes automatically
4. Generate AI-powered recommendations
5. Create professional report

Expected output: `outputs/ClashGuard_Report_*.docx` + `.pdf`

---

## Claude Desktop Integration

### Step 1: Find Claude Config File

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```
Full path:
```
C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json
```

**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Get Your Project Path

```bash
# From project directory, get absolute path:
cd clashguard-mcp
pwd  # Mac/Linux
cd   # Windows
```

Copy this path. Example:
```
D:\CC_Tech\MCP hack cctech\clashguard-mcp
```

### Step 3: Add ClashGuard to Claude Config

Open `claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "clashguard": {
      "command": "python",
      "args": ["C:\\\\FULL\\\\PATH\\\\TO\\\\clashguard-mcp\\\\server.py"]
    }
  }
}
```

**Important:** Replace `C:\\FULL\\PATH\\TO\\clashguard-mcp\\server.py` with your actual path!

### Step 4: Restart Claude Desktop

1. **Fully quit** Claude Desktop (right-click system tray → Quit)
2. Wait 3 seconds
3. Reopen Claude Desktop
4. Look for **🔨 hammer icon** in the chat interface
5. If you see it → **MCP is connected!**

### Verification

In Claude Desktop, start a new chat and type:

```
Hello! Tell me what tools you have available.
```

Expected response should list:
- ✅ extract_revit_data
- ✅ analyze_model
- ✅ detect_clashes
- ✅ suggest_resolutions
- ✅ generate_report

---

## Demo Scenarios

### Scenario 1: Instant Clash Check (30 seconds)

**Type in Claude Desktop:**
```
I want to add new windows on the south facade of Level 3. 
Can you check if they will clash with any HVAC ducts, pipes, 
or structural elements?
```

**What happens:**
1. Claude calls `extract_revit_data("Level 3", ["Duct", "Pipe", "Window", "Beam"])`
2. Claude calls `analyze_model()` with the extracted elements
3. Claude calls `detect_clashes()` to find intersections
4. Claude returns a clash report with:
   - 3-4 clashes detected (CRITICAL/HIGH/MEDIUM)
   - Element pairs clearly identified
   - Spatial locations

**Expected clashes in mock data:**
- **CG-001 (CRITICAL):** HVAC duct crosses structural beam
- **CG-002 (HIGH):** HVAC duct near new window
- **CG-003 (MEDIUM):** Sprinkler pipe near cable tray

---

### Scenario 2: AI-Powered Prioritization (1 minute)

**Type in Claude:**
```
Please prioritize these clashes for the MEP team. 
Which should they fix first and why? 
I consent to sending clash data for analysis.
```

**What happens:**
1. Claude calls `suggest_resolutions()` with `user_consent_given=true`
2. Anthropic Claude (or Gemini) analyzes the clashes
3. Returns plain-English recommendations:

**Expected response:**
```
CLASH CG-001 (CRITICAL) — DUCTWORK × STRUCTURAL BEAM
├─ Why: Load-bearing beam cannot be altered; duct reroute is safer
├─ Fix: Reroute HVAC supply duct up 300mm to clear beam
└─ Priority: Fix FIRST — blocking other MEP layouts

CLASH CG-002 (HIGH) — DUCTWORK × NEW WINDOW
├─ Why: New windows already in design; duct flexibility is better
├─ Fix: Shift duct 150mm west to clear window opening
└─ Priority: Fix SECOND — architect may need window adjustment

CLASH CG-003 (MEDIUM) — SPRINKLER PIPE × CABLE TRAY
├─ Why: Both systems have routing flexibility
├─ Fix: Lower cable tray by 50mm — electrical has more headroom
└─ Priority: Fix if schedule allows — not blocking critical path
```

---

### Scenario 3: Professional Report (30 seconds)

**Type in Claude:**
```
Generate a professional clash coordination report for 
the Magarpatta Tower Level 3 project in PDF and Word format.
```

**What happens:**
1. Claude calls `generate_report()`
2. Python creates professional documents with:
   - Executive summary
   - Clash locations with coordinates
   - Severity breakdown chart
   - Recommended fixes
   - High-resolution 3D clash visualizations (if available)

**Files created:**
```
outputs/
├── ClashGuard_Report_Magarpatta_Tower_20260605_143000.docx  (650 KB)
├── ClashGuard_Report_Magarpatta_Tower_20260605_143000.pdf   (1.2 MB)
└── clash_data_20260605_143000.json  (backup data)
```

---

## Testing & Validation

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_engine.py::TestAABB::test_intersection_volume_correct -v

# Coverage report
pytest tests/ --cov=engine --cov=tools
```

### Integration Tests

```bash
# Full pipeline test
python -m pytest tests/test_tools.py::test_full_pipeline -v
```

### Manual Testing with Demo Script

```bash
# Run all tools end-to-end
python -c "
from tools.extract_revit_data import run as extract
from tools.analyze_model import run as analyze
from tools.detect_clashes import run as detect
import json

elements = json.loads(extract({'use_demo_data': True}))['elements']
analysis = json.loads(analyze({'elements': elements}))
clashes = json.loads(detect({'elements': analysis['elements']}))

print(f'Found {clashes[\"total_clashes\"]} clashes')
for clash in clashes['clashes'][:3]:
    print(f'  - {clash[\"id\"]}: {clash[\"elements\"][0]} × {clash[\"elements\"][1]}')
"
```

---

## Troubleshooting

### Issue: "ClashGuard MCP not appearing in Claude Desktop"

**Cause:** Config file not found or syntax error

**Solution:**
1. Find config file using paths above ☝
2. Verify file is named exactly `claude_desktop_config.json`
3. Check syntax: paste in https://jsonlint.com
4. Verify path separators are `\\` (Windows) or `/` (Mac/Linux)
5. Fully restart Claude Desktop

### Issue: "ModuleNotFoundError: No module named 'anthropic'"

**Solution:**
```bash
pip install -r requirements.txt --upgrade
# OR
pip install anthropic httpx requests trimesh shapely numpy python-docx reportlab python-dotenv pytest pytest-asyncio
```

### Issue: "FileNotFoundError: mock_db.json"

**Cause:** Running from wrong directory

**Solution:**
```bash
cd clashguard-mcp  # Must be in project root
python server.py
```

### Issue: "KeyError: 'MOCK_DB_PATH'"

**Cause:** `.env` not loading properly

**Solution:**
```bash
# Check .env exists
ls -la .env  # Mac/Linux
dir .env    # Windows

# Verify format (no spaces around =)
cat .env | grep DEMO_MODE  # Should show: DEMO_MODE=true
```

### Issue: Tests failing with "Import Error"

**Solution:**
```bash
# Verify you're in the right directory
pwd  # Should end in /clashguard-mcp

# Install in editable mode
pip install -e .

# Try tests again
pytest tests/ -v
```

---

## Architecture Overview

### System Components

```
Claude Desktop (User Interface)
    ↓ (stdio via MCP protocol)
server.py (Main Entry Point)
    ├─ Tool 1: extract_revit_data
    │   └─ → aps/auth.py (token mgmt)
    │   └─ → data/mock_db.json (demo mode)
    ├─ Tool 2: analyze_model
    │   └─ → engine/geometry_utils.py
    ├─ Tool 3: detect_clashes
    │   └─ → engine/aabb.py (deterministic collision detection)
    │   └─ → engine/severity.py (rule-based scoring)
    ├─ Tool 4: suggest_resolutions
    │   └─ → Claude API / Gemini API (AI reasoning only)
    └─ Tool 5: generate_report
        └─ → python-docx / reportlab (report generation)
```

### Deterministic vs AI

**Deterministic (100% reliable):**
- AABB bounding box collision detection
- Intersection volume calculation
- Severity scoring rules
- Geometric analysis

**AI-Powered (Reasoning only):**
- Natural language understanding
- Why clashes matter (context)
- Fix recommendations
- Report writing

**This separation ensures:**
- ✅ Autodesk Trust & Safety compliance
- ✅ No AI hallucinations in geometry
- ✅ Reproducible results
- ✅ Explainable clash detection

---

## File Structure

```
clashguard-mcp/
├── server.py                 # Main MCP server
├── config.py                 # Configuration loader
├── test_setup.py             # Verification script
├── requirements.txt          # Python dependencies
├── .env                      # Secrets (gitignored)
├── .env.example              # Template
├── manifest.json             # Autodesk MCP manifest
├── claude_desktop_config.json # Claude config template
│
├── tools/                    # 5 MCP tools
│   ├── extract_revit_data.py
│   ├── analyze_model.py
│   ├── detect_clashes.py
│   ├── suggest_resolutions.py
│   └── generate_report.py
│
├── engine/                   # Deterministic geometry engine
│   ├── aabb.py              # Collision detection
│   ├── severity.py          # Severity scoring
│   └── geometry_utils.py    # Coordinate math
│
├── aps/                     # Autodesk API clients
│   ├── auth.py              # OAuth token management
│   └── (add model_derivatives.py for real APS)
│
├── data/
│   └── mock_db.json         # Demo data (11 MEP elements)
│
├── outputs/                 # Generated reports (gitignored)
│
└── tests/
    ├── test_tools.py        # Tool integration tests
    └── test_engine.py       # Geometry engine tests
```

---

## Next Steps

### ✅ Completed
- ✅ Python environment configured
- ✅ All dependencies installed
- ✅ Test suite passing
- ✅ Server ready for deployment

### 📝 To-Do
1. [ ] Set up Claude Desktop config (5 min)
2. [ ] Add API keys if using real APS/Claude
3. [ ] Run demo scenarios in Claude Desktop
4. [ ] Generate sample reports
5. [ ] Submit to Autodesk marketplace (if deploying)

### 🚀 For Production
1. Deploy to AWS Lambda
2. Set up OAuth 2.0 callback handler
3. Connect to real Autodesk BIM 360 projects
4. Enable write-back to Revit (v2)
5. Multi-user collaboration (v2)

---

## Support & Contact

- **GitHub:** https://github.com/cctech-pune/clashguard-mcp
- **Issues:** Report on GitHub
- **Documentation:** See [PRD.md](PRD.md) for full technical spec
- **Author:** CCTech MCP Team

---

**Last Updated:** June 5, 2026  
**Status:** ✅ Ready for Use
