# server.py
"""
ClashGuard MCP Server
====================
Main entry point for the ClashGuard MCP server.
Implements Model Context Protocol over stdio transport.
Compatible with Claude Desktop (free tier).
"""

import json
import sys
import logging
from pathlib import Path

# Add project root to sys.path to allow internal imports to work
sys.path.insert(0, str(Path(__file__).parent))

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
