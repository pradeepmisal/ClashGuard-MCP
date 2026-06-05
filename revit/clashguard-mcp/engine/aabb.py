# engine/aabb.py
"""
Axis-Aligned Bounding Box (AABB) Collision Detection Engine.
100% deterministic — no AI involved.
Finds intersections between pairs of 3D bounding boxes.
"""

from engine.severity import score_clash, SEVERITY_LABELS

def aabb_intersects(a_min, a_max, b_min, b_max) -> bool:
    """
    Returns True if two AABBs intersect.
    Checks all 3 axes — if any axis has no overlap, no collision.
    """
    return (
        a_min["x"] <= b_max["x"] and a_max["x"] >= b_min["x"] and
        a_min["y"] <= b_max["y"] and a_max["y"] >= b_min["y"] and
        a_min["z"] <= b_max["z"] and a_max["z"] >= b_min["z"]
    )

def intersection_volume(a_min, a_max, b_min, b_max) -> float:
    """Calculate the volume of the intersection of two AABBs."""
    ox = max(0, min(a_max["x"], b_max["x"]) - max(a_min["x"], b_min["x"]))
    oy = max(0, min(a_max["y"], b_max["y"]) - max(a_min["y"], b_min["y"]))
    oz = max(0, min(a_max["z"], b_max["z"]) - max(a_min["z"], b_min["z"]))
    return ox * oy * oz

def run_clash_detection(elements: list, systems_to_check: list, tolerance_mm: float = 50) -> list:
    """
    Main clash detection function.
    Compares all element pairs and returns list of detected clashes.
    """
    tolerance_m = tolerance_mm / 1000.0
    clashes = []
    clash_id = 1
    seen_pairs = set()

    mep_types      = {"Duct", "Pipe", "CableTray", "Conduit", "MechanicalEquipment", "PlumbingFixture"}
    struct_types   = {"Beam", "Column", "StructuralFraming"}
    arch_types     = {"Wall", "Window", "Floor", "Ceiling", "Roof"}

    for i, el_a in enumerate(elements):
        for j, el_b in enumerate(elements):
            if j <= i:
                continue
            pair_key = tuple(sorted([el_a["id"], el_b["id"]]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            # Only check MEP vs structural/architectural crosses
            a_is_mep   = el_a["type"] in mep_types
            b_is_mep   = el_b["type"] in mep_types
            a_is_other = el_a["type"] in struct_types | arch_types
            b_is_other = el_b["type"] in struct_types | arch_types

            if not ((a_is_mep and b_is_other) or (b_is_mep and a_is_other)):
                continue

            bbox_a = el_a.get("bbox", {})
            bbox_b = el_b.get("bbox", {})
            a_min, a_max = bbox_a.get("min", {}), bbox_a.get("max", {})
            b_min, b_max = bbox_b.get("min", {}), bbox_b.get("max", {})

            if not (a_min and a_max and b_min and b_max):
                continue

            # Expand bbox by tolerance for soft clash detection
            a_min_soft = {k: a_min[k] - tolerance_m for k in a_min}
            a_max_soft = {k: a_max[k] + tolerance_m for k in a_max}

            # Hard clash
            if aabb_intersects(a_min, a_max, b_min, b_max):
                vol = intersection_volume(a_min, a_max, b_min, b_max)
                severity_score = score_clash(el_a, el_b, vol, "hard")
                clashes.append({
                    "clash_id":        f"CG-{clash_id:03d}",
                    "type":            "hard",
                    "element_a":       {"id": el_a["id"], "type": el_a["type"], "name": el_a.get("name", "")},
                    "element_b":       {"id": el_b["id"], "type": el_b["type"], "name": el_b.get("name", "")},
                    "location":        el_a.get("location", "Unknown"),
                    "intersection_volume_m3": round(vol, 6),
                    "severity_score":  severity_score,
                    "severity_label":  SEVERITY_LABELS[severity_score],
                    "center": el_a.get("center", {}),
                })
                clash_id += 1

            # Soft clash (within tolerance but not hard)
            elif aabb_intersects(a_min_soft, a_max_soft, b_min, b_max):
                severity_score = score_clash(el_a, el_b, 0, "soft")
                clashes.append({
                    "clash_id":        f"CG-{clash_id:03d}",
                    "type":            "soft",
                    "element_a":       {"id": el_a["id"], "type": el_a["type"], "name": el_a.get("name", "")},
                    "element_b":       {"id": el_b["id"], "type": el_b["type"], "name": el_b.get("name", "")},
                    "location":        el_a.get("location", "Unknown"),
                    "intersection_volume_m3": 0,
                    "clearance_violation_mm": tolerance_mm,
                    "severity_score":  severity_score,
                    "severity_label":  SEVERITY_LABELS[severity_score],
                    "center": el_a.get("center", {}),
                })
                clash_id += 1

    return sorted(clashes, key=lambda c: c["severity_score"], reverse=True)
