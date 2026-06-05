# tools/analyze_model.py
"""
Tool 2: analyze_model
Processes element relationships, clearance zones, and spatial context.
Prepares data for clash detection.
"""

import json
from engine.geometry_utils import compute_centers, compute_proximity_groups

def run(args: dict) -> str:
    raw_elements           = args.get("elements", [])
    tolerance_mm           = args.get("clearance_tolerance_mm", 50)

    if isinstance(raw_elements, str):
        try:
            parsed = json.loads(raw_elements)
            if isinstance(parsed, dict):
                raw_elements = parsed.get("elements", [])
            else:
                raw_elements = parsed
        except:
            raw_elements = []
    elif isinstance(raw_elements, dict):
        raw_elements = raw_elements.get("elements", [])

    if not raw_elements:
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
