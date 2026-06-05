# ClashGuard MCP

**AI-Powered MEP Clash Detection for Revit**

Detect, prioritize, and resolve MEP (Mechanical, Electrical, Plumbing) clashes in Autodesk Revit using natural language with Claude AI — in under 5 minutes.

---

## 🎯 The Problem

MEP clashes cost the global AEC industry **$625 billion/year** in rework. Current tools like Navisworks detect clashes but don't prioritize them or suggest fixes. Architects and BIM coordinators waste 2-4 hours per cycle manually investigating clashes in complex models.

## ✨ The Solution

ClashGuard MCP brings AI-powered reasoning into your clash detection workflow:

```
Architect types in Claude:  "Will my new windows clash with HVAC ducts?"
                                          ↓
                         ClashGuard analyzes the model
                                          ↓
                    Gets prioritized, actionable answers in 5 minutes
```

**Without** opening Navisworks. **Without** manual coordination meetings.

---

## 🏗️ Complete Architecture Flow

See how your query flows through the entire system:

![MEP Clash Detective Architecture Flow](./MEP%20Clash%20Detective.png)

**The Flow Explained:**

1. **You (Architect/BIM Coordinator)** → Ask a natural language question in Claude
2. **MCP Server** → Routes your request to one of 5 specialized tools
3. **Data Sources** → Pulls from:
   - **Revit/BIM APIs** — Extract building geometry, MEP systems
   - **APS/Forge APIs** — Access models, derivatives, metadata
   - **Knowledge Engine** — Apply building codes, MEP rules, clearance standards
4. **Claude Reasoning Layer** → Understands your intent, analyzes conflicts, prioritizes clashes
5. **Smart Outputs** → Get:
   - Model updates (clash annotations, suggested moves)
   - Professional reports (PDF, Excel, JSON for dashboards)
6. **Ready for Action** → Clash info flows to your team for coordination & construction

**Real Use Case (shown on right):**
- Architect adds windows to 3rd floor south façade
- System detects HVAC duct collision
- Suggests rerouting with cost/impact estimates
- Updates model and generates coordination sheet

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Claude Desktop** (free tier)
- **Anthropic API Key** ([Get one here](https://console.anthropic.com))
- **Autodesk APS Account** (optional for demo mode)

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/cctech-pune/clashguard-mcp.git
cd clashguard-mcp

# Create Python virtual environment
python3.11 -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```ini
# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-sonnet-4-5

# Autodesk Platform Services (optional for real data)
APS_CLIENT_ID=your_aps_client_id
APS_CLIENT_SECRET=your_aps_client_secret

# Demo mode (uses mock data)
DEMO_MODE=true
```

**Don't have an Anthropic API key?**
- Get one free at [console.anthropic.com](https://console.anthropic.com) (Claude 3.5 Sonnet included)
- You'll have $5 free credits for testing

### 3. Connect to Claude Desktop

1. Open your Claude Desktop config file:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add ClashGuard to your MCP servers:

```json
{
  "mcpServers": {
    "clashguard": {
      "command": "python",
      "args": ["C:\\FULL\\PATH\\TO\\clashguard-mcp\\server.py"]
    }
  }
}
```

3. Restart Claude Desktop. You should see **ClashGuard** in the tool menu.

### 4. Run Your First Query

In Claude Desktop, type:

```
Can you detect clashes between HVAC ducts and structural elements in my Revit model?
```

ClashGuard will respond with detected clashes, severity levels, and suggested resolutions.

---

## 🛠 Features

| Feature | Description |
|---------|-------------|
| **Extract Revit Data** | Pull MEP system geometry and element data via APS APIs |
| **Analyze Model** | Identify spatial conflicts between building systems |
| **Detect Clashes** | Use deterministic AABB collision detection + AI reasoning |
| **Suggest Resolutions** | Get AI-generated rerouting and design fix suggestions |
| **Generate Reports** | Export professional clash reports (Word/PDF format) |

---

## 📁 Project Structure

```
clashguard-mcp/
│
├── server.py                    # Main entry point (run this)
├── requirements.txt             # Python dependencies
├── .env                         # Your API keys (git-ignored)
├── .env.example                 # Template for .env
├── manifest.json                # Autodesk MCP manifest
│
├── tools/                       # MCP Tool implementations
│   ├── extract_revit_data.py    # Extract geometry from Revit
│   ├── analyze_model.py         # Spatial analysis
│   ├── detect_clashes.py        # Collision detection
│   ├── suggest_resolutions.py   # AI-powered fix suggestions
│   └── generate_report.py       # Report generation
│
├── engine/                      # Deterministic geometry engine
│   ├── aabb.py                  # AABB bounding box collision
│   ├── severity.py              # Rule-based severity scoring
│   └── geometry_utils.py        # Coordinate helpers
│
├── aps/                         # Autodesk Platform Services client
│   ├── auth.py                  # OAuth token management
│   ├── model_derivatives.py     # Model Derivatives API
│   └── revit_client.py          # Revit element extraction
│
├── data/
│   ├── mock_db.json             # Demo data (no APS needed)
│   ├── severity_rules.json      # Clash severity definitions
│   └── report_templates/        # Report generation templates
│
├── outputs/                     # Generated reports
├── tests/                       # Unit and integration tests
├── docs/                        # Documentation
└── logs/                        # Debug logs
```

---

## 🔌 How It Works: The 5 Tools

### Tool 1: Extract Revit Data
Pulls MEP system elements from your Revit model via Autodesk APS APIs.

**What it does:**
- Reads HVAC ducts, electrical runs, plumbing pipes
- Extracts coordinates, bounding boxes, element IDs
- Organizes by floor/zone

**Use when:** "Show me all the MEP systems on Level 3"

---

### Tool 2: Analyze Model
Analyzes spatial relationships and identifies potential conflict zones.

**What it does:**
- Detects overlapping bounding boxes
- Calculates clearance distances
- Identifies high-risk zones

**Use when:** "Are there any tight spaces in my model?"

---

### Tool 3: Detect Clashes
Performs deterministic collision detection + AI reasoning to find real clashes.

**What it does:**
- AABB collision detection (100% deterministic)
- Calculates clash volumes and intersection points
- Applies rule-based severity scoring
- Uses Claude AI to prioritize and explain

**Use when:** "Detect all clashes between MEP systems"

---

### Tool 4: Suggest Resolutions
AI-powered suggestions for how to fix detected clashes.

**What it does:**
- Generates rerouting paths for pipes/ducts
- Suggests coordinate adjustments
- Provides cost/impact estimates
- Recommends which clashes to fix first

**Use when:** "How should I reroute this duct to avoid the pipe?"

---

### Tool 5: Generate Report
Creates professional PDF/Word clash reports.

**What it does:**
- Lists all detected clashes
- Includes severity rankings
- Shows suggested resolutions
- Generates coordinates for field teams

**Use when:** "Export a report of all clashes"

---

## 💡 Architecture Principles

### ✅ Deterministic + AI
- **Geometry calculations** (collision, clearance): 100% deterministic, rule-based code
- **Reasoning** (prioritization, explanations, fixes): Claude AI

This design ensures Autodesk compliance — no hallucination risk for engineering calculations.

### ✅ Local-First Design
- Runs entirely on your machine via Claude Desktop
- No external servers, no data uploads
- Option to connect to real APS data or use mock demo data

### ✅ Privacy & Security
- All processing is local
- APS credentials stored in `.env` (git-ignored)
- No clash data is sent to external services

---

## 🧪 Demo Mode

**Don't have APS credentials yet?** No problem — use demo mode:

```bash
# Set in .env
DEMO_MODE=true
```

ClashGuard will use pre-loaded sample Revit data to demonstrate all 5 tools. Perfect for testing and learning.

---

## 🔐 Real Data Mode

To connect to your actual Revit models on Autodesk BIM 360:

### 1. Create an APS Developer Account
1. Go to [aps.autodesk.com](https://aps.autodesk.com)
2. Sign in or create an Autodesk account
3. Go to Developer Portal and create an app
4. Select APIs: Data Management, Model Derivatives, Authentication
5. Copy your `CLIENT_ID` and `CLIENT_SECRET`

### 2. Set Up Your Credentials
```ini
# .env file
APS_CLIENT_ID=your_client_id_here
APS_CLIENT_SECRET=your_client_secret_here
DEMO_MODE=false
```

### 3. Get Your Model URN
- Upload a Revit file to Autodesk BIM 360
- Copy the file's URN (base64-encoded identifier) from the URL

### 4. Query Your Real Model
```
In Claude: "Analyze the MEP clashes in URN: urn:adsk:objects:os.object:fs.file:a360-xxxxxxxx"
```

---

## 🧑‍💻 For Developers

### Run Tests
```bash
pytest tests/ -v
```

### Enable Debug Logging
```python
# In server.py or any tool
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Add a New Tool
1. Create a new file in `tools/`
2. Implement the `run()` async function
3. Register it in `server.py` under `TOOLS`
4. Test with `pytest`

### Extend the Geometry Engine
- All collision detection lives in `engine/aabb.py`
- All scoring rules live in `engine/severity.py`
- Add new calculations in `engine/geometry_utils.py`

---

## 📊 Supported Revit Elements

**MEP Categories:**
- HVAC Ducts & Equipment
- Electrical Conduits & Panels
- Plumbing Pipes & Fixtures
- Structural Columns & Beams
- Architectural Walls & Openings

**Currently Analyzed:**
- Coordinate geometry (centerlines, bounding boxes)
- Element IDs and names
- Floor/zone assignments
- System classifications (HVAC type, electrical voltage, etc.)

---

## ⚠️ Known Limitations

| Limitation | Workaround |
|-----------|-----------|
| Only reads element geometry (no write-back) | v2 will support model annotations |
| Requires pre-exported URN | v2 will support direct file upload |
| Single-model analysis | v2 will support multi-model clash detection |
| Demo data only covers basic MEP | Use real APS data for production models |

---

## 🛡️ Security & Compliance

✅ **Autodesk Marketplace Ready**
- Trust & Safety requirements met (deterministic geometry)
- OAuth 2.0 support for APS authentication
- No external data transmission
- HTTPS-only API communication

✅ **GDPR & Data Privacy**
- No personal data collection
- Local processing only
- Credentials encrypted in `.env`
- Audit logging available

---

## 📞 Support & Contributing

### Get Help
- **Documentation**: See `docs/` folder
- **Issues**: Create a GitHub issue with:
  - Your Python version (`python --version`)
  - Your `.env` file settings (redact secrets!)
  - The exact Claude message that failed
  - Error logs from `logs/` folder

### Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes and add tests
4. Submit a pull request

---

## 📜 License

MIT License — See [LICENSE](./LICENSE) file

---

## 🎓 Learn More

- **[Architecture Deep Dive](./docs/ARCHITECTURE.md)** — System design & decisions
- **[API Reference](./docs/IMPLEMENTATION_SUMMARY.md)** — Tool schemas & responses
- **[Autodesk Compliance](./docs/AUTODESK_COMPLIANCE.md)** — Marketplace requirements
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)** — Common issues & fixes

---

## 🙏 Acknowledgments

Built for the **CCTECH Innovation Hackathon** (June 2026)  
Presented by **Autodesk** & **Mercer | Mettl**

**Team:** Krushna, Prathmesh, and contributors

---

## 🎯 Roadmap (v2)

- [ ] Direct Revit write-back (annotate clashes in model)
- [ ] Multi-model clash detection
- [ ] AWS Lambda deployment
- [ ] Advanced 3D visualization
- [ ] Collaborative team workflows
- [ ] Clash history & version tracking

---

**Ready to eliminate MEP clashes?** Start with the [Quick Start](#-quick-start) section above! 🚀

