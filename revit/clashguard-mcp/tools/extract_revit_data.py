# tools/extract_revit_data.py
"""
Tool 1: extract_revit_data
Extracts MEP element geometry and spatial data from Revit via APS.
In DEMO_MODE, reads from data/mock_db.json instead of live APS.
"""

import json
import sys
from pathlib import Path

# Add project root to sys.path if not present to allow config imports
sys.path.insert(0, str(Path(__file__).parent.parent))
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

def _extract_from_aps(model_urn: str, floor_filter: str, element_types: list) -> str:
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
