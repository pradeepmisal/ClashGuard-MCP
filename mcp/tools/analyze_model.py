# tools/analyze_model.py
"""Tool 2: Analyzes spatial relationships between building elements."""
import json
from engine.geometry_utils import compute_centers, compute_proximity_groups


def run(args: dict) -> str:
    elements     = args.get("elements", [])
    tolerance_mm = args.get("clearance_tolerance_mm", 50)

    if isinstance(elements, str):
        try:
            elements = json.loads(elements)
        except Exception:
            return json.dumps({"error": "Invalid elements JSON. Pass the elements array from extract_revit_data."})

    if not elements:
        return json.dumps({"error": "No elements provided."})

    elements = compute_centers(elements)
    groups   = compute_proximity_groups(elements, threshold_m=2.0)

    by_type  = {}
    by_floor = {}
    for el in elements:
        by_type[el["type"]]      = by_type.get(el["type"], 0) + 1
        by_floor[el["location"]] = by_floor.get(el["location"], 0) + 1

    return json.dumps({
        "status":                 "analyzed",
        "total_elements":         len(elements),
        "clearance_tolerance_mm": tolerance_mm,
        "elements":               elements,
        "proximity_groups":       groups,
        "summary": {
            "by_type":      by_type,
            "by_floor":     by_floor,
            "total_groups": len(groups),
        },
        "message": (f"Analyzed {len(elements)} elements across {len(by_floor)} floor(s). "
                    f"Found {len(groups)} proximity groups ready for clash detection.")
    }, indent=2)
