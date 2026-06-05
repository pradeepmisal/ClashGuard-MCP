# server.py
"""
ClashGuard MCP Server — Main Entry Point
Implements Model Context Protocol (MCP) over stdio transport.
Compatible with Claude Desktop (free tier).

Setup:
  1. pip install -r requirements.txt
  2. Copy .env.example to .env and fill in your API keys
  3. Add to Claude Desktop config (see README.md)
  4. Restart Claude Desktop — look for the hammer icon

Claude Desktop config location:
  Windows: %APPDATA%\\Claude\\claude_desktop_config.json
  Mac:     ~/Library/Application Support/Claude/claude_desktop_config.json

Config content:
{
  "mcpServers": {
    "clashguard": {
      "command": "python",
      "args": ["C:\\\\FULL\\\\PATH\\\\TO\\\\clashguard-mcp\\\\server.py"]
    }
  }
}
"""

import json
import sys
import logging

from tools.extract_revit_data import run as extract_revit_data
from tools.analyze_model       import run as analyze_model
from tools.detect_clashes      import run as detect_clashes
from tools.suggest_resolutions import run as suggest_resolutions
from tools.generate_report     import run as generate_report

logging.basicConfig(level=logging.INFO, stream=sys.stderr,
                    format="[ClashGuard] %(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("clashguard")

# ── Tool Definitions ──────────────────────────────────────────────
# AUTODESK COMPLIANCE: Descriptions are plain factual statements.
# No instructions ("use when...", "run after...") — would cause rejection.
TOOLS = [
    {
        "name": "extract_revit_data",
        "description": (
            "Extracts MEP and architectural element geometry, bounding boxes, "
            "and spatial data from a Revit model. Supports local demo data "
            "and live Autodesk APS Model Derivatives API."
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
                    "description": "Optional floor or level filter, e.g. 'Level 3'."
                },
                "element_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Element types to include: Duct, Pipe, CableTray, Window, Wall, Beam."
                },
                "use_revit_export": {
                    "type": "boolean",
                    "description": "Load data from C# Revit plugin export instead of demo data."
                }
            },
            "required": []
        }
    },
    {
        "name": "analyze_model",
        "description": (
            "Computes spatial centers and proximity relationships between "
            "building elements. Prepares data for clash detection."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "elements": {
                    "type": "array",
                    "description": "Element list from extract_revit_data."
                },
                "clearance_tolerance_mm": {
                    "type": "number",
                    "description": "Minimum clearance in mm before soft-clash flag. Default: 50mm."
                }
            },
            "required": []
        }
    },
    {
        "name": "detect_clashes",
        "description": (
            "Performs deterministic AABB collision detection between MEP systems "
            "and architectural or structural elements. Returns hard clashes "
            "(physical overlap) and soft clashes (clearance violations) with severity scores."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "elements": {
                    "type": "array",
                    "description": "Analyzed elements from analyze_model."
                },
                "systems_to_check": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "MEP systems to check: HVAC, Plumbing, Electrical, Structural."
                },
                "zones": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional zone filter, e.g. ['Level 3', 'South Facade']."
                }
            },
            "required": []
        }
    },
    {
        "name": "suggest_resolutions",
        "description": (
            "Sends anonymized clash data to Anthropic Claude AI and returns "
            "prioritized resolution recommendations. Requires explicit user consent "
            "before sending data. No personal data or credentials are transmitted."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "clashes": {
                    "type": "array",
                    "description": "Clash list from detect_clashes."
                },
                "project_context": {
                    "type": "string",
                    "description": "Optional project context: building type, design phase, constraints."
                },
                "user_consent_given": {
                    "type": "boolean",
                    "description": "Set to true when user has consented to sending clash data to Claude AI."
                }
            },
            "required": ["user_consent_given"]
        }
    },
    {
        "name": "generate_report",
        "description": (
            "Generates a MEP clash coordination report in PDF and Word formats. "
            "Files are saved locally. No external data transmission."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "clashes": {
                    "type": "array",
                    "description": "Clash list from detect_clashes or suggest_resolutions."
                },
                "project_name": {
                    "type": "string",
                    "description": "Project name for the report header."
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

# ── MCP stdio Protocol Loop ───────────────────────────────────────

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
    log.info("ClashGuard MCP Server v1.0 starting...")
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError as e:
            log.warning(f"JSON decode error: {e}")
            continue

        method = msg.get("method", "")
        msg_id = msg.get("id")
        params = msg.get("params", {})

        log.info(f"← {method} (id={msg_id})")

        if method == "initialize":
            send({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities":    {"tools": {}},
                    "serverInfo":      {"name": "clashguard-mcp", "version": "1.0.0"}
                }
            })

        elif method == "notifications/initialized":
            log.info("Client initialized successfully")

        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            log.info(f"  → tool: {tool_name} args: {list(arguments.keys())}")
            handler = TOOL_HANDLERS.get(tool_name)
            if handler:
                try:
                    result = handler(arguments)
                    tool_result(msg_id, result)
                    log.info(f"  ✓ {tool_name} completed")
                except Exception as e:
                    log.error(f"  ✗ {tool_name} failed: {e}")
                    error_result(msg_id, -32603, f"Tool error: {str(e)}")
            else:
                error_result(msg_id, -32601, f"Unknown tool: {tool_name}")

        elif msg_id is not None:
            error_result(msg_id, -32601, f"Method not found: {method}")


if __name__ == "__main__":
    main()
