# adapter.py
"""
Converts ClashGuard C# Revit plugin export (clashguard_payloads.json)
into the Python MCP Tool 1 element format.

C# exports coordinates in millimeters with field name 'level'.
Python Tools expect coordinates in meters with field name 'location'.
This adapter handles the conversion transparently.
"""

import json
from pathlib import Path

# Maps C# OST category names to PRD element type names
CATEGORY_MAP = {
    "DuctCurves":          "Duct",
    "FlexDuctCurves":      "Duct",
    "DuctFitting":         "Duct",
    "DuctAccessory":       "Duct",
    "PipeCurves":          "Pipe",
    "FlexPipeCurves":      "Pipe",
    "PipeFitting":         "Pipe",
    "PipeAccessory":       "Pipe",
    "Conduit":             "Conduit",
    "ConduitFitting":      "Conduit",
    "CableTray":           "CableTray",
    "CableTrayFitting":    "CableTray",
    "MechanicalEquipment": "MechanicalEquipment",
    "PlumbingFixtures":    "PlumbingFixture",
    "FireProtection":      "Pipe",
    "ElectricalEquipment": "ElectricalEquipment",
    "ElectricalFixtures":  "ElectricalEquipment",
    "LightingFixtures":    "ElectricalEquipment",
    "Walls":               "Wall",
    "Doors":               "Door",
    "Windows":             "Window",
    "Floors":              "Floor",
    "Ceilings":            "Ceiling",
    "Roofs":               "Roof",
    "StructuralFraming":   "Beam",
    "StructuralColumns":   "Column",
    "StructuralFoundation":"Column",
    "Stairs":              "Stair",
    "Ramps":               "Ramp",
}


def load_csharp_export(json_path: str) -> list:
    """
    Loads the C# plugin's exported JSON and converts to Tool 1 format.
    Handles coordinate conversion: mm -> meters.
    Handles field rename: 'level' -> 'location', 'category' -> 'type'.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    elements = data.get("elements", [])
    converted = []

    for elem in elements:
        # Parse bounding box — C# serializer outputs arrays [x, y, z]
        bbox = elem.get("bbox", {})
        raw_min = bbox.get("min", [0, 0, 0])
        raw_max = bbox.get("max", [0, 0, 0])

        # Support both array format [x,y,z] and object format {x:,y:,z:}
        if isinstance(raw_min, list):
            mn = {"x": raw_min[0], "y": raw_min[1], "z": raw_min[2]}
            mx = {"x": raw_max[0], "y": raw_max[1], "z": raw_max[2]}
        else:
            mn = raw_min
            mx = raw_max

        # Convert mm -> meters (C# outputs mm; Python AABB engine uses meters)
        mn_m = {k: round(v / 1000.0, 4) for k, v in mn.items()}
        mx_m = {k: round(v / 1000.0, 4) for k, v in mx.items()}

        category = elem.get("category", "")
        elem_id  = str(elem.get("id", ""))

        converted.append({
            "id":       elem_id,
            "type":     CATEGORY_MAP.get(category, "Unknown"),
            "name":     f"{category} (ID: {elem_id})",
            "location": elem.get("level", "Unknown"),
            "zone":     elem.get("system_name", ""),
            "bbox":     {"min": mn_m, "max": mx_m},
            "properties": {
                "system": elem.get("system", ""),
                "sizing": elem.get("sizing", {}),
            }
        })

    return converted


def save_as_mock_db(elements: list, output_path: str):
    """Saves converted elements as a mock_db.json-compatible file for reuse."""
    payload = {
        "project":     "ClashGuard — Live Revit Export",
        "description": f"Real Revit model data exported via C# plugin. {len(elements)} elements.",
        "elements":    elements
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"[adapter] Saved {len(elements)} elements to {output_path}")
