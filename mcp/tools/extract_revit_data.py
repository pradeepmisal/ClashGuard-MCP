# tools/extract_revit_data.py
"""
Tool 1: extract_revit_data
Extracts MEP and architectural element data from a Revit model.

Data source priority:
  1. C# Revit plugin export (CSHARP_EXPORT_PATH) — real Revit data, no APS needed
  2. APS Model Derivatives API — live cloud data (requires credentials)
  3. data/mock_db.json — built-in demo data (always works, for presentation)
"""
import json
from pathlib import Path
from config import DEMO_MODE, MOCK_DB_PATH, CSHARP_EXPORT_PATH
from adapter import load_csharp_export

MEP_TYPES  = {"Duct", "Pipe", "CableTray", "Conduit", "MechanicalEquipment",
              "PlumbingFixture", "ElectricalEquipment"}
ARCH_TYPES = {"Window", "Wall", "Beam", "Column", "Floor", "Ceiling", "Roof", "Door"}
ALL_TYPES  = MEP_TYPES | ARCH_TYPES


def run(args: dict) -> str:
    floor_filter     = args.get("floor_filter", "")
    element_types    = set(args.get("element_types", list(ALL_TYPES)))
    model_urn        = args.get("model_urn", "")
    use_revit_export = args.get("use_revit_export", False)

    # Priority 1: C# plugin export (real Revit data, no APS)
    if use_revit_export and CSHARP_EXPORT_PATH and Path(CSHARP_EXPORT_PATH).exists():
        return _from_csharp(CSHARP_EXPORT_PATH, floor_filter, element_types)

    # Priority 2: APS live data
    if not DEMO_MODE and model_urn:
        return _from_aps(model_urn, floor_filter, element_types)

    # Priority 3: Demo mock data
    return _from_mock(floor_filter, element_types)


def _from_csharp(path: str, floor_filter: str, element_types: set) -> str:
    """Load real Revit data from C# plugin export."""
    try:
        elements = load_csharp_export(path)
        if floor_filter:
            elements = [e for e in elements
                        if floor_filter.lower() in e.get("location", "").lower()]
        elements = [e for e in elements if e.get("type") in element_types]
        return json.dumps({
            "source":   "csharp_revit_export",
            "count":    len(elements),
            "elements": elements,
            "message":  f"Loaded {len(elements)} elements from Revit plugin export (real model data)."
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to load C# export: {str(e)}. Falling back to mock data."})


def _from_mock(floor_filter: str, element_types: set) -> str:
    """Load built-in demo data from mock_db.json."""
    with open(MOCK_DB_PATH, "r", encoding="utf-8") as f:
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
        "project":  db.get("project", ""),
        "message":  f"Extracted {len(elements)} elements from demo data. Ready for analysis."
    }, indent=2)


def _from_aps(model_urn: str, floor_filter: str, element_types: set) -> str:
    """Live extraction via APS Model Derivatives API."""
    try:
        from aps.auth import get_token
        import httpx

        token   = get_token()
        headers = {"Authorization": f"Bearer {token}"}

        meta_url = (f"https://developer.api.autodesk.com/modelderivative/v2"
                    f"/designdata/{model_urn}/metadata")
        meta = httpx.get(meta_url, headers=headers, verify=True, timeout=30)
        meta.raise_for_status()
        guid = meta.json()["data"]["metadata"][0]["guid"]

        props_url = (f"https://developer.api.autodesk.com/modelderivative/v2"
                     f"/designdata/{model_urn}/metadata/{guid}/properties")
        props = httpx.get(props_url, headers=headers, verify=True, timeout=30)
        props.raise_for_status()

        elements = []
        for obj in props.json().get("data", {}).get("collection", []):
            p  = obj.get("properties", {})
            tp = p.get("Category", {}).get("Category", "Unknown")
            if tp not in element_types:
                continue
            elements.append({
                "id":       str(obj.get("objectid")),
                "type":     tp,
                "name":     obj.get("name", ""),
                "location": p.get("Constraints", {}).get("Level", ""),
                "zone":     "",
                "bbox":     {"min": {"x": 0, "y": 0, "z": 0},
                             "max": {"x": 0, "y": 0, "z": 0}},
                "properties": {"size": p.get("Dimensions", {})}
            })

        return json.dumps({
            "source":   "aps_live",
            "urn":      model_urn,
            "count":    len(elements),
            "elements": elements,
            "message":  f"Extracted {len(elements)} elements from live Revit model via APS."
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"APS extraction failed: {str(e)}"})
