# ClashGuard MCP — Quick Reference Guide

**Quick Commands Reference** (Copy & Paste Ready)

## 1️⃣ Initial Setup

```bash
# Clone/enter project
cd clashguard-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR venv\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements.txt

# Verify setup
python test_setup.py
```

## 2️⃣ Running the Server

### Local Development
```bash
# Start MCP server (listens on stdio)
python server.py

# Expected: [ClashGuard] server listening...
# (server waits for Claude Desktop)
```

### Run Complete Demo
```bash
# End-to-end demo with all 5 tools
python demo.py

# Expected: 16 clashes detected, reports generated
```

## 3️⃣ Claude Desktop Setup

### Find Config File
```
Windows: %APPDATA%\Claude\claude_desktop_config.json
Mac:     ~/Library/Application Support/Claude/claude_desktop_config.json
```

### Add ClashGuard to Config
```json
{
  "mcpServers": {
    "clashguard": {
      "command": "python",
      "args": ["D:\\CC_Tech\\MCP hack cctech\\clashguard-mcp\\server.py"]
    }
  }
}
```

**Note:** Update path to your project location!

### Verify Connection
1. Save config file
2. Fully quit Claude Desktop
3. Reopen Claude Desktop
4. Look for 🔨 hammer icon (means MCP connected)
5. Type: "What tools do you have?"

## 4️⃣ Environment Variables (.env)

```ini
# For demo (works as-is):
DEMO_MODE=true

# For real APS/Claude (optional):
APS_CLIENT_ID=your_client_id
APS_CLIENT_SECRET=your_client_secret
ANTHROPIC_API_KEY=sk-proj-xxxxx
```

## 5️⃣ Testing

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test
pytest tests/test_engine.py::TestAABB -v

# Test with coverage
pytest tests/ --cov=engine --cov=tools
```

## 6️⃣ The 5 Tools

### Tool 1: Extract Revit Data
```python
extract_revit_data({
    "floor_filter": "Level 3",
    "element_types": ["Duct", "Pipe", "Window", "Beam"]
})
# Returns: 10+ MEP elements with bounding boxes
```

### Tool 2: Analyze Model
```python
analyze_model({
    "elements": [... from Tool 1 ...],
    "clearance_tolerance_mm": 50
})
# Returns: Spatial centers, proximity groups
```

### Tool 3: Detect Clashes (Deterministic)
```python
detect_clashes({
    "elements": [... from Tool 2 ...],
    "systems_to_check": ["Duct", "Pipe", "Beam"],
    "tolerance_mm": 50
})
# Returns: 16 clashes (CRITICAL/HIGH/MEDIUM/LOW)
```

### Tool 4: Suggest Resolutions (AI)
```python
suggest_resolutions({
    "clashes": [... from Tool 3 ...],
    "user_consent_given": true
})
# Returns: Engineering recommendations
```

### Tool 5: Generate Report
```python
generate_report({
    "clashes": [... from Tool 3 ...],
    "project_name": "Magarpatta Tower — Level 3",
    "export_format": "both"  # PDF + Word
})
# Returns: /outputs/ClashGuard_Report_*.docx + .pdf
```

## 7️⃣ Prompt Examples for Claude Desktop

### Scenario 1: Quick Clash Check
```
I want to add new windows on the south facade of Level 3.
Can you check if they will clash with HVAC ducts, pipes, or beams?
```

### Scenario 2: Get AI Recommendations
```
Please analyze these clashes and tell me which ones are CRITICAL.
What should the MEP team fix first?
I consent to sending clash data to Claude AI for analysis.
```

### Scenario 3: Generate Report
```
Generate a professional clash coordination report for the project
and save it in PDF and Word format.
```

## 8️⃣ Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt --upgrade` |
| MCP not in Claude | Check config file path, verify JSON syntax, restart Claude |
| Tests failing | `cd clashguard-mcp` (ensure correct directory) |
| No reports generated | Check `outputs/` folder exists, verify write permissions |
| Clashes showing None | Mock data loading issue — run `python demo.py` |

## 9️⃣ Project Structure

```
clashguard-mcp/
├── server.py              # Main entry point (run this)
├── config.py              # Configuration
├── test_setup.py          # Verify installation
├── demo.py                # Complete demo
├── setup.bat              # Windows one-click setup
│
├── tools/                 # 5 MCP tools
├── engine/                # Collision detection
├── aps/                   # Autodesk API clients
├── data/mock_db.json      # Demo data
├── tests/                 # Unit tests
└── outputs/               # Generated reports
```

## 🔟 Architecture

```
User Types in Claude Desktop
    ↓
    server.py receives request
    ↓
    Tool executes (e.g., detect_clashes)
    ↓
    engine/aabb.py — Deterministic collision detection
    ↓
    Result returned to Claude
    ↓
    Claude displays answer + can call other tools
```

**Key Design:**
- ✅ **Geometry = 100% Deterministic** (no hallucination)
- ✅ **Reasoning = AI-Powered** (Claude/Gemini)
- ✅ **Separation = Autodesk Compliant**

## 🎯 Demo Output Example

```
TOOL 1: Extract Revit Data
✓ Extracted 10 elements (2 ducts, 1 pipe, 5 windows, 1 beam)

TOOL 2: Analyze Model
✓ Analysis complete (spatial centers computed)

TOOL 3: Detect Clashes
✓ Found 16 clashes
  🔴 CRITICAL: 6
  🟠 HIGH: 9
  🟡 MEDIUM: 1

TOOL 4: Suggest Resolutions
✓ AI recommendations generated
  [1] DUCT × BEAM: Reroute duct up 300mm
  [2] DUCT × WINDOW: Shift duct 150mm west

TOOL 5: Generate Report
✓ Reports generated
  ClashGuard_Report_Magarpatta_Tower_20260605.docx (650 KB)
  ClashGuard_Report_Magarpatta_Tower_20260605.pdf (1.2 MB)
```

## 📞 Support

- **GitHub Issues:** Report bugs here
- **Documentation:** See `SETUP_GUIDE.md` and `PRD.md`
- **Email:** See GitHub repo

---

**Last Updated:** June 5, 2026  
**Version:** 1.0 (Production Ready)
